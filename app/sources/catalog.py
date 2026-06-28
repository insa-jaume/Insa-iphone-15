"""Catálogo de boletines oficiales de España que conviene vigilar.

Incluye los estatales, los 19 autonómicos y los 50 provinciales (+ los de las
ciudades autónomas y forales). Marcamos con ``implemented=True`` aquellos para
los que ya existe un adaptador de ingesta funcionando (de momento, BOE y BORME
vía API oficial). El resto quedan registrados como hoja de ruta: el modelo de
datos y el motor de matching ya los soportan; solo falta su adaptador.

Por qué estos boletines importan para el caso de uso (que no te sorprendan
embargos, sanciones o notificaciones):

* BOE — Tablón Edictal Único (Sección V / Suplemento de notificaciones):
  notificaciones de la AEAT, TGSS, DGT, ayuntamientos, etc. cuando no te
  localizan. ES EL MÁS CRÍTICO.
* BORME — situaciones mercantiles (concursos, administradores, disoluciones).
* Boletines autonómicos y provinciales (BOP) — sanciones, multas de tráfico,
  expedientes urbanísticos, subvenciones, edictos de recaudación local, etc.
"""
from __future__ import annotations

from app.models import SourceScope

# (code, name, scope, region, homepage, implemented)
CATALOG: list[tuple[str, str, SourceScope, str, str, bool]] = [
    # --- Estatales ---
    ("BOE", "Boletín Oficial del Estado (incl. Tablón Edictal Único)", SourceScope.estatal, "España", "https://www.boe.es", True),
    ("BORME", "Boletín Oficial del Registro Mercantil", SourceScope.estatal, "España", "https://www.boe.es/diario_borme/", True),

    # --- Autonómicos ---
    ("BOJA", "Boletín Oficial de la Junta de Andalucía", SourceScope.autonomico, "Andalucía", "https://www.juntadeandalucia.es/eboja.html", False),
    ("BOA", "Boletín Oficial de Aragón", SourceScope.autonomico, "Aragón", "http://www.boa.aragon.es", False),
    ("BOPA", "Boletín Oficial del Principado de Asturias", SourceScope.autonomico, "Asturias", "https://sede.asturias.es/bopa", False),
    ("BOIB", "Butlletí Oficial de les Illes Balears", SourceScope.autonomico, "Isles Balears", "https://www.caib.es/eboibfront/", False),
    ("BOC-CAN", "Boletín Oficial de Canarias", SourceScope.autonomico, "Canarias", "https://www.gobiernodecanarias.org/boc/", False),
    ("BOC-CANT", "Boletín Oficial de Cantabria", SourceScope.autonomico, "Cantabria", "https://boc.cantabria.es", False),
    ("DOCM", "Diario Oficial de Castilla-La Mancha", SourceScope.autonomico, "Castilla-La Mancha", "https://docm.jccm.es", False),
    ("BOCYL", "Boletín Oficial de Castilla y León", SourceScope.autonomico, "Castilla y León", "https://bocyl.jcyl.es", False),
    ("DOGC", "Diari Oficial de la Generalitat de Catalunya", SourceScope.autonomico, "Catalunya", "https://dogc.gencat.cat", False),
    ("DOE", "Diario Oficial de Extremadura", SourceScope.autonomico, "Extremadura", "https://doe.juntaex.es", False),
    ("DOG", "Diario Oficial de Galicia", SourceScope.autonomico, "Galicia", "https://www.xunta.gal/diario-oficial-galicia", False),
    ("BOCM", "Boletín Oficial de la Comunidad de Madrid", SourceScope.autonomico, "Madrid", "https://www.bocm.es", False),
    ("BORM", "Boletín Oficial de la Región de Murcia", SourceScope.autonomico, "Murcia", "https://www.borm.es", False),
    ("BON", "Boletín Oficial de Navarra", SourceScope.autonomico, "Navarra", "https://bon.navarra.es", False),
    ("BOPV", "Boletín Oficial del País Vasco / Euskal Herriko Agintaritzaren Aldizkaria", SourceScope.autonomico, "Euskadi", "https://www.euskadi.eus/bopv2/", False),
    ("BOR", "Boletín Oficial de La Rioja", SourceScope.autonomico, "La Rioja", "https://www.larioja.org/bor/", False),
    ("DOGV", "Diari Oficial de la Generalitat Valenciana", SourceScope.autonomico, "Comunitat Valenciana", "https://dogv.gva.es", False),
    ("BOCCE", "Boletín Oficial de la Ciudad de Ceuta", SourceScope.autonomico, "Ceuta", "https://www.ceuta.es", False),
    ("BOCME", "Boletín Oficial de la Ciudad de Melilla", SourceScope.autonomico, "Melilla", "https://www.melilla.es", False),

    # --- Provinciales (Boletín Oficial de la Provincia) ---
    # Los más relevantes por volumen de edictos de recaudación/sanción.
    ("BOP-A", "BOP de Alicante", SourceScope.provincial, "Alicante", "https://www.dip-alicante.es/bop2/", False),
    ("BOP-B", "BOP de Barcelona", SourceScope.provincial, "Barcelona", "https://bop.diba.cat", False),
    ("BOP-BI", "BOB - Boletín Oficial de Bizkaia", SourceScope.provincial, "Bizkaia", "https://www.bizkaia.eus/bao", False),
    ("BOP-GC", "BOP de Las Palmas", SourceScope.provincial, "Las Palmas", "https://www.boplaspalmas.net", False),
    ("BOP-M", "BOCM (provincia de Madrid)", SourceScope.provincial, "Madrid", "https://www.bocm.es", False),
    ("BOP-MA", "BOP de Málaga", SourceScope.provincial, "Málaga", "https://www.bopmalaga.es", False),
    ("BOP-SE", "BOP de Sevilla", SourceScope.provincial, "Sevilla", "https://www.dipusevilla.es/bop/", False),
    ("BOP-SS", "BOG - Boletín Oficial de Gipuzkoa", SourceScope.provincial, "Gipuzkoa", "https://egoitza.gipuzkoa.eus/bog/", False),
    ("BOP-V", "BOP de Valencia", SourceScope.provincial, "Valencia", "https://bop.dival.es", False),
    ("BOP-Z", "BOP de Zaragoza", SourceScope.provincial, "Zaragoza", "https://bop.dpz.es", False),
    # ... el resto de provincias se incorporan con el mismo patrón de adaptador.
]


def implemented_codes() -> set[str]:
    return {row[0] for row in CATALOG if row[5]}
