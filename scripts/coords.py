# -*- coding: utf-8 -*-
"""Coordenadas (lat, lng) aproximadas de la capital por país ISO-3, para situar las
burbujas del mapa. Lista centrada en receptores habituales de la cooperación española."""

COORDS = {
    # América Latina y Caribe
    "COL": (4.6, -74.1), "PER": (-12.0, -77.0), "BOL": (-16.5, -68.1), "ECU": (-0.2, -78.5),
    "HND": (14.1, -87.2), "GTM": (14.6, -90.5), "SLV": (13.7, -89.2), "NIC": (12.1, -86.3),
    "DOM": (18.5, -69.9), "PRY": (-25.3, -57.6), "CUB": (23.1, -82.4), "VEN": (10.5, -66.9),
    "HTI": (18.6, -72.3), "URY": (-34.9, -56.2), "MEX": (19.4, -99.1), "BRA": (-15.8, -47.9),
    "ARG": (-34.6, -58.4), "CHL": (-33.4, -70.7), "CRI": (9.9, -84.1), "PAN": (9.0, -79.5),
    "GUY": (6.8, -58.2),
    # África
    "MAR": (34.0, -6.8), "MRT": (18.1, -15.9), "SEN": (14.7, -17.5), "MLI": (12.6, -8.0),
    "NER": (13.5, 2.1), "ETH": (9.0, 38.7), "MOZ": (-25.9, 32.6), "GNQ": (3.8, 8.8),
    "NGA": (9.1, 7.4), "CPV": (14.9, -23.5), "DZA": (28.0, 1.7), "TUN": (36.8, 10.2),
    "EGY": (30.0, 31.2), "AGO": (-8.8, 13.2), "CMR": (3.9, 11.5), "SDN": (15.5, 32.5),
    "SOM": (2.0, 45.3), "TCD": (12.1, 15.0), "BFA": (12.4, -1.5), "GMB": (13.4, -16.6),
    "GIN": (9.6, -13.6), "COD": (-4.3, 15.3), "KEN": (-1.3, 36.8), "GHA": (5.6, -0.2),
    "ZWE": (-17.8, 31.0), "LBY": (32.9, 13.2), "TZA": (-6.2, 35.7), "GNB": (11.9, -15.6),
    "SSD": (4.85, 31.6),
    # Oriente Próximo / Mediterráneo / Asia
    "PSE": (31.9, 35.2), "JOR": (31.9, 35.9), "LBN": (33.9, 35.5), "SYR": (33.5, 36.3),
    "IRQ": (33.3, 44.4), "YEM": (15.4, 44.2), "AFG": (34.5, 69.2), "UKR": (50.4, 30.5),
    "PHL": (14.6, 121.0), "BGD": (23.8, 90.4), "IND": (28.6, 77.2), "PAK": (33.7, 73.1),
    "MMR": (16.8, 96.2), "VNM": (21.0, 105.8), "TUR": (39.9, 32.9),
}

# Normalización de nombres frecuentes -> ISO-3 (para entradas de agentes sin iso fiable)
NAME2ISO = {
    "colombia": "COL", "perú": "PER", "peru": "PER", "bolivia": "BOL", "ecuador": "ECU",
    "honduras": "HND", "guatemala": "GTM", "el salvador": "SLV", "nicaragua": "NIC",
    "república dominicana": "DOM", "rep. dominicana": "DOM", "paraguay": "PRY", "cuba": "CUB",
    "venezuela": "VEN", "haití": "HTI", "haiti": "HTI", "uruguay": "URY", "méxico": "MEX",
    "mexico": "MEX", "marruecos": "MAR", "mauritania": "MRT", "senegal": "SEN", "malí": "MLI",
    "mali": "MLI", "níger": "NER", "niger": "NER", "etiopía": "ETH", "etiopia": "ETH",
    "mozambique": "MOZ", "guinea ecuatorial": "GNQ", "nigeria": "NGA", "cabo verde": "CPV",
    "argelia": "DZA", "túnez": "TUN", "tunez": "TUN", "egipto": "EGY", "angola": "AGO",
    "camerún": "CMR", "sudán": "SDN", "sudan": "SDN", "somalia": "SOM", "chad": "TCD",
    "burkina faso": "BFA", "gambia": "GMB", "guinea": "GIN", "kenia": "KEN", "ghana": "GHA",
    "territorios palestinos": "PSE", "palestina": "PSE", "palestinos": "PSE",
    "cisjordania y gaza": "PSE", "jordania": "JOR", "líbano": "LBN", "libano": "LBN",
    "siria": "SYR", "irak": "IRQ", "iraq": "IRQ", "yemen": "YEM", "afganistán": "AFG",
    "afganistan": "AFG", "ucrania": "UKR", "filipinas": "PHL", "bangladés": "BGD",
    "bangladesh": "BGD", "india": "IND", "pakistán": "PAK", "pakistan": "PAK",
    "turquía": "TUR", "turquia": "TUR", "rd congo": "COD", "r.d. congo": "COD",
    "congo": "COD", "tanzania": "TZA", "sudán del sur": "SSD",
}
