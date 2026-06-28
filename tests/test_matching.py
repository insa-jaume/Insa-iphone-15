"""Test del motor de coincidencias con una BD SQLite en memoria."""
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Publication, Source, SourceScope, Subject, SubjectKind
from app.search import build_index_fields, find_matches_for_subject


@pytest.fixture()
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def _add_pub(db, source_id, ext_id, text, day=date(2024, 1, 15)):
    normalized, ids = build_index_fields(text)
    pub = Publication(
        source_id=source_id, ext_id=ext_id, pub_date=day, title=text[:80],
        full_text=text, normalized_text=normalized, identifiers=ids,
    )
    db.add(pub)
    db.commit()
    return pub


def test_match_por_identificador_y_nombre(db):
    src = Source(code="BOE", name="BOE", scope=SourceScope.estatal)
    db.add(src)
    db.commit()

    _add_pub(db, src.id, "BOE-B-2024-1",
             "Notificación a JAUME INSA PEREZ con NIF 21693936Z por deuda.")
    _add_pub(db, src.id, "BOE-B-2024-2",
             "Anuncio relativo a otra persona sin relación.")

    # Coincide por identificador
    subj = Subject(user_id=1, kind=SubjectKind.person, display_name="Jaume Insa Pérez",
                   normalized_name="JAUME INSA PEREZ", normalized_id="21693936Z",
                   id_kind="DNI", monitor_name=True)
    db.add(subj)
    db.commit()

    res = find_matches_for_subject(db, subj)
    assert len(res) == 1
    pub, mtype, term, score = res[0]
    assert mtype.value == "identifier"
    assert score == 100


def test_match_solo_por_nombre(db):
    src = Source(code="BOE", name="BOE", scope=SourceScope.estatal)
    db.add(src)
    db.commit()
    _add_pub(db, src.id, "BOE-B-2024-3",
             "Edicto sobre MARIA GONZALEZ RUIZ vecina de la localidad.")

    subj = Subject(user_id=1, kind=SubjectKind.person, display_name="María González Ruiz",
                   normalized_name="MARIA GONZALEZ RUIZ", normalized_id=None,
                   monitor_name=True)
    db.add(subj)
    db.commit()

    res = find_matches_for_subject(db, subj)
    assert len(res) == 1
    assert res[0][1].value == "name"
    assert res[0][3] == 60
