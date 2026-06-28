"""Aplicación web: registro, panel, suscripción Stripe y páginas legales."""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.ingest import match_subject
from app.models import (
    Match,
    Publication,
    Source,
    Subject,
    SubjectKind,
    User,
    utcnow,
)
from app.normalize import classify_identifier, normalize_identifier, normalize_name
from app.search import find_matches_for_subject
from app.security import (
    SESSION_COOKIE,
    create_session_token,
    hash_password,
    read_session_token,
    verify_password,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("web")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title=settings.site_name, docs_url=None, redoc_url=None)

static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
def _startup() -> None:
    # En despliegue, init_db ya creó el esquema; esto lo hace resiliente en dev.
    Base.metadata.create_all(bind=engine)


# --- Contexto y autenticación -------------------------------------------------


def _ctx(request: Request, **extra) -> dict:
    base = {
        "request": request,
        "settings": settings,
        "site_name": settings.site_name,
        "price_eur": settings.price_eur,
        "provider_name": settings.provider_name,
        "provider_nif": settings.provider_nif,
        "provider_email": settings.provider_email,
        "provider_address": settings.provider_address,
        "user": getattr(request.state, "user", None),
    }
    base.update(extra)
    return base


def current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    user_id = read_session_token(token)
    if not user_id:
        return None
    user = db.get(User, user_id)
    request.state.user = user
    return user


def require_user(user: User | None = Depends(current_user)) -> User:
    if user is None:
        raise HTTPException(status_code=303, headers={"Location": "/acceso"})
    return user


def render(name: str, request: Request, **extra) -> HTMLResponse:
    # Starlette >= 0.29 usa la firma (request, name, context).
    return templates.TemplateResponse(request, name, _ctx(request, **extra))


# --- Páginas públicas ---------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
def landing(request: Request, user: User | None = Depends(current_user)):
    return render("landing.html", request)


@app.get("/boletines", response_class=HTMLResponse)
def boletines(request: Request, user: User | None = Depends(current_user), db: Session = Depends(get_db)):
    sources = db.scalars(select(Source).order_by(Source.scope, Source.code)).all()
    return render("boletines.html", request, sources=sources)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# --- Registro / acceso --------------------------------------------------------


@app.get("/registro", response_class=HTMLResponse)
def registro_form(request: Request, user: User | None = Depends(current_user)):
    if user:
        return RedirectResponse("/panel", status_code=303)
    return render("registro.html", request, error=None)


@app.post("/registro", response_class=HTMLResponse)
def registro(
    request: Request,
    db: Session = Depends(get_db),
    full_name: str = Form(""),
    email: str = Form(...),
    password: str = Form(...),
    accept: str = Form(None),
):
    email = email.strip().lower()
    if not accept:
        return render("registro.html", request, error="Debes aceptar las condiciones y la política de privacidad.")
    if len(password) < 8:
        return render("registro.html", request, error="La contraseña debe tener al menos 8 caracteres.")
    if db.scalar(select(User).where(User.email == email)):
        return render("registro.html", request, error="Ya existe una cuenta con ese correo.")

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name.strip(),
        accepted_terms_at=utcnow(),
        consent_self_data=True,
    )
    db.add(user)
    db.commit()

    resp = RedirectResponse("/panel", status_code=303)
    resp.set_cookie(SESSION_COOKIE, create_session_token(user.id), httponly=True,
                    samesite="lax", max_age=60 * 60 * 24 * 30, secure=not settings.debug)
    return resp


@app.get("/acceso", response_class=HTMLResponse)
def acceso_form(request: Request, user: User | None = Depends(current_user)):
    if user:
        return RedirectResponse("/panel", status_code=303)
    return render("acceso.html", request, error=None)


@app.post("/acceso", response_class=HTMLResponse)
def acceso(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):
    email = email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(password, user.password_hash):
        return render("acceso.html", request, error="Credenciales incorrectas.")
    resp = RedirectResponse("/panel", status_code=303)
    resp.set_cookie(SESSION_COOKIE, create_session_token(user.id), httponly=True,
                    samesite="lax", max_age=60 * 60 * 24 * 30, secure=not settings.debug)
    return resp


@app.get("/salir")
def salir():
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie(SESSION_COOKIE)
    return resp


# --- Panel del usuario --------------------------------------------------------


def _subject_matches(db: Session, subject: Subject) -> list[tuple[Match, Publication, Source]]:
    rows = db.scalars(
        select(Match).where(Match.subject_id == subject.id).order_by(Match.created_at.desc())
    ).all()
    out = []
    for m in rows:
        pub = db.get(Publication, m.publication_id)
        src = db.get(Source, pub.source_id) if pub else None
        out.append((m, pub, src))
    return out


@app.get("/panel", response_class=HTMLResponse)
def panel(request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)):
    subjects = db.scalars(select(Subject).where(Subject.user_id == user.id)).all()
    data = [(s, _subject_matches(db, s)) for s in subjects]
    return render(
        "panel.html", request,
        subjects_data=data,
        has_sub=user.has_active_subscription,
        stripe_enabled=settings.stripe_enabled,
        checkout=request.query_params.get("checkout"),
    )


@app.post("/panel/identidad")
def add_subject(
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
    kind: str = Form("person"),
    display_name: str = Form(...),
    identifier: str = Form(""),
    monitor_name: str = Form(None),
    is_self: str = Form(None),
    consent: str = Form(None),
):
    if not consent:
        raise HTTPException(400, "Debes confirmar que eres el titular del dato o su representante autorizado.")

    norm_id = normalize_identifier(identifier) if identifier else None
    id_kind = classify_identifier(norm_id) if norm_id else None
    if norm_id and not id_kind:
        # Identificador no válido: lo guardamos igual pero sin tipo (matching solo por nombre).
        id_kind = None

    subject = Subject(
        user_id=user.id,
        kind=SubjectKind.company if kind == "company" else SubjectKind.person,
        display_name=display_name.strip(),
        normalized_name=normalize_name(display_name),
        identifier=identifier.strip() or None,
        normalized_id=norm_id,
        id_kind=id_kind,
        is_self=bool(is_self),
        consent_confirmed=True,
        monitor_name=bool(monitor_name),
    )
    db.add(subject)
    db.commit()

    # Búsqueda preliminar sobre todo el histórico ya ingerido.
    match_subject(db, subject)
    return RedirectResponse("/panel", status_code=303)


@app.post("/panel/identidad/{subject_id}/baja")
def remove_subject(subject_id: int, user: User = Depends(require_user), db: Session = Depends(get_db)):
    subject = db.get(Subject, subject_id)
    if subject and subject.user_id == user.id:
        db.delete(subject)
        db.commit()
    return RedirectResponse("/panel", status_code=303)


@app.post("/cuenta/baja")
def delete_account(user: User = Depends(require_user), db: Session = Depends(get_db)):
    """Derecho de supresión (RGPD): elimina la cuenta y todos sus datos."""
    db.delete(user)
    db.commit()
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie(SESSION_COOKIE)
    return resp


# --- Pagos (Stripe) -----------------------------------------------------------


@app.get("/suscribir")
def suscribir(user: User = Depends(require_user), db: Session = Depends(get_db)):
    if not settings.stripe_enabled:
        raise HTTPException(503, "Pagos no configurados todavía.")
    from app.payments import create_checkout_session
    url = create_checkout_session(db, user)
    return RedirectResponse(url, status_code=303)


@app.get("/facturacion")
def facturacion(user: User = Depends(require_user), db: Session = Depends(get_db)):
    if not settings.stripe_enabled:
        raise HTTPException(503, "Pagos no configurados todavía.")
    from app.payments import create_billing_portal
    url = create_billing_portal(db, user)
    return RedirectResponse(url, status_code=303)


@app.post("/webhook/stripe")
async def webhook_stripe(request: Request, db: Session = Depends(get_db)):
    from app.payments import handle_webhook
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    try:
        handle_webhook(db, payload, sig)
    except Exception as exc:  # noqa: BLE001
        log.exception("Webhook Stripe inválido")
        raise HTTPException(400, f"Webhook error: {exc}")
    return Response(status_code=200)


# --- Páginas legales ----------------------------------------------------------

for _slug, _tpl in {
    "aviso-legal": "legal/aviso_legal.html",
    "privacidad": "legal/privacidad.html",
    "terminos": "legal/terminos.html",
    "cookies": "legal/cookies.html",
    "contrato": "legal/contrato.html",
}.items():
    def _make(tpl: str):
        def _view(request: Request, user: User | None = Depends(current_user)):
            return render(tpl, request)
        return _view
    app.add_api_route(f"/{_slug}", _make(_tpl), response_class=HTMLResponse, methods=["GET"])
