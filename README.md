# Alertas Oficiales

Servicio de suscripción que **avisa a una persona o empresa cuando su nombre,
DNI, NIE, NIF o CIF aparece en un boletín oficial de España** (BOE, Tablón
Edictal Único, BORME y, progresivamente, autonómicos y provinciales).

El objetivo: que **no te sorprendan embargos, sanciones o recargos** derivados
de notificaciones que nunca llegaron a tu casa pero que fueron publicadas
oficialmente y, por tanto, tienen efectos legales y plazos que corren.

> Prestador: **Jaume Insa Pérez** (NIF 21693936Z), autónomo con epígrafe de
> prestación de servicios online. Cobro por **Stripe** (5 €/mes).

---

## 1. El problema (por qué existe este servicio)

Cuando una administración no consigue notificarte de forma personal (no te
localizan, fallan los intentos, ignoran tu domicilio), la ley le permite
**notificarte mediante publicación en un boletín oficial**. Desde ese momento la
notificación se considera practicada: empiezan a contar plazos para recurrir,
pagar o alegar, **aunque tú nunca te enteres**. Así es como aparecen embargos,
recargos y sanciones "por sorpresa".

Punto más crítico: el **Tablón Edictal Único (TEU)** del BOE (antigua Sección V),
donde la AEAT, la Seguridad Social (TGSS), la DGT y los ayuntamientos publican
notificaciones de deudas, sanciones y embargos por edicto.

## 2. Boletines vigilados

| Ámbito | Boletines |
|---|---|
| **Estatal** | **BOE** (incl. Tablón Edictal Único / notificaciones), **BORME** |
| **Autonómico (19)** | BOJA, BOA, BOPA, BOIB, BOC (Canarias y Cantabria), DOCM, BOCYL, DOGC, DOE, DOG, BOCM, BORM, BON, BOPV, BOR, DOGV, BOCCE, BOCME |
| **Provincial (50)** | Boletín Oficial de la Provincia (BOP) de cada provincia |

**Implementado hoy** vía API oficial de datos abiertos: **BOE** y **BORME**.
El resto están registrados como hoja de ruta (`/boletines`): el modelo de datos
y el motor de búsqueda ya los soportan; solo falta el adaptador de ingesta de
cada uno (ver §6).

## 3. Cómo funciona

1. **Registro y consentimiento.** El usuario crea su cuenta y declara que los
   datos que quiere vigilar son **suyos** o de alguien a quien **representa**.
2. **Búsqueda preliminar.** Al añadir una identidad, se busca en todo el
   histórico ya indexado y se muestran las coincidencias encontradas.
3. **Suscripción (Stripe).** 5 €/mes. Mientras esté activa, recibe avisos.
4. **Vigilancia diaria.** Un worker descarga cada día los boletines nuevos,
   extrae el texto, detecta identificadores fiscales válidos y nombres, y
   genera coincidencias.
5. **Aviso por email** con el enlace a la publicación oficial.

### Precisión del matching

- **Por identificador (DNI/NIE/CIF):** se extraen del texto solo identificadores
  con **dígito/letra de control válido** y se comparan como token exacto. Altísima
  precisión (score 100).
- **Por nombre:** búsqueda de subcadena normalizada (sin tildes, mayúsculas).
  Útil pero puede dar **homónimos**, por eso se marca como "revisar" (score 60).

## 4. Arquitectura

```
Navegador ── Caddy (HTTPS) ── web (FastAPI) ── PostgreSQL
                                   │
                              worker (APScheduler)
                                   │  ingesta diaria + notificaciones
                          API datos abiertos BOE/BORME
```

| Componente | Tecnología |
|---|---|
| Web/API | FastAPI + Jinja2 |
| Base de datos | PostgreSQL (SQLAlchemy 2.0) |
| Ingesta | `httpx` + API oficial `boe.es/datosabiertos` |
| Programación | APScheduler (worker) |
| Pagos | Stripe (Checkout + Billing Portal + Webhooks) |
| Email | SMTP (stdlib) |
| Despliegue | Docker Compose + Caddy (TLS automático) |

Código principal en `app/`:

- `models.py` — modelo de datos.
- `normalize.py` — validación de DNI/NIE/CIF y normalización de nombres.
- `sources/` — adaptadores de boletines (`boe.py`, `catalog.py`, `registry.py`).
- `search.py` / `ingest.py` — motor de coincidencias y orquestación.
- `payments.py` — Stripe. `notifier.py` — emails. `scheduler.py` — worker.
- `main.py` — rutas web. `templates/` — páginas (incl. `legal/`).

## 5. Despliegue en el VPS

```bash
git clone <repo> && cd <repo>
cp .env.example .env        # rellenar TODO (Stripe, SMTP, dominio, datos del prestador)
export SITE_DOMAIN=alertas.tudominio.es   # apunta el DNS A/AAAA al VPS

docker compose up -d --build          # levanta db, web, worker y caddy (HTTPS)
```

### Carga del histórico (backfill)

```bash
# Ingerir un rango (intensivo; un día de BOE = cientos de descargas)
docker compose run --rm worker python -m scripts.backfill 2024-01-01 2024-12-31 BOE BORME

# "Desde lo más temprano posible": la API de datos abiertos cubre con
# fiabilidad el BOE moderno (BOE-A) desde ~2010. Ajusta el rango según tu VPS.
docker compose run --rm worker python -m scripts.backfill 2010-01-01 2026-06-28 BOE
```

El worker, además, ejecuta automáticamente la ingesta del **día** (y reintenta
el anterior) a la hora configurada (`INGEST_DAILY_HOUR`).

### Stripe

1. Crea un **producto** con un **precio recurrente de 5 €/mes** y copia su
   `price_...` en `STRIPE_PRICE_ID`.
2. Crea un endpoint de **webhook** apuntando a `https://TU_DOMINIO/webhook/stripe`
   y copia el `whsec_...` en `STRIPE_WEBHOOK_SECRET`.
3. Eventos mínimos: `checkout.session.completed`,
   `customer.subscription.created/updated/deleted`.

### Rendimiento a escala

Para grandes volúmenes, añade índices de PostgreSQL para la búsqueda por nombre:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_pub_normtext_trgm ON publications USING gin (normalized_text gin_trgm_ops);
CREATE INDEX idx_pub_ids_trgm ON publications USING gin (identifiers gin_trgm_ops);
```

## 6. Añadir un boletín nuevo (autonómico/provincial)

1. Crea `app/sources/<codigo>.py` con una subclase de `BulletinSource` que
   implemente `fetch_summary_items(day)` y `fetch_item_text(item)`.
2. Regístrala en `app/sources/registry.py`.
3. Marca `implemented=True` en `app/sources/catalog.py`.

El resto (deduplicado, extracción de identificadores, matching, notificación) es
automático.

## 7. Cumplimiento legal (RGPD / LOPDGDD / LSSI-CE)

La clave de licitud de este servicio: **solo se vigilan datos del propio
suscriptor o de quien él represente, con su consentimiento explícito.** No se
construye ni comercializa una base de datos de terceros. Esto es esencial: la
AEPD ha sancionado la reutilización de datos personales de boletines oficiales
para ofrecer servicios a terceros sin base jurídica.

Incluido en la app: aviso legal, política de privacidad, términos y condiciones,
política de cookies (solo técnica) y contrato/consentimiento del titular, con los
datos del prestador. Stripe y los proveedores de hosting/email actúan como
**encargados del tratamiento** (art. 28 RGPD). Derechos de acceso/rectificación/
supresión accesibles desde el panel (borrado total de cuenta).

> ⚠️ Los textos legales son **plantillas orientativas**: revísalas con un
> profesional antes de operar comercialmente y valora una consulta/EIPD a la AEPD.

## 8. Desarrollo y tests

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q          # tests de validación de identificadores y de matching
```

## 9. Aviso

Servicio **informativo**: no presta asesoramiento jurídico ni sustituye a las
notificaciones oficiales ni al cómputo de plazos. Verifica siempre en la fuente
oficial. Existe un servicio oficial **gratuito** ("Mi BOE") de avisos del TEU por
NIF que requiere identificación electrónica; el valor de este proyecto es la
**agregación** de boletines, el **histórico**, el aviso por **nombre** y la
sencillez de uso.
