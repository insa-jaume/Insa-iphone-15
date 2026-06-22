# Metodología y fuentes

Web app **"¿A dónde va la ayuda exterior de España?"** — mapa de la Ayuda Oficial al
Desarrollo (AOD) española, cotejo con el Consejo de Ministros y riesgo de corrupción estimado.

---

## 1. Naturaleza de los datos

Hay **dos tipos de datos** en `webapp/data/`:

- 🏛️ **`consejo_ministros_real.json` — DATOS REALES.** Acuerdos de cooperación / ayuda
  exterior extraídos automáticamente de las referencias oficiales del Consejo de Ministros
  en La Moncloa (ver §3). Cada acuerdo enlaza a su fuente.
- 🗺️ **`aid.json` y `categories.json` — ilustrativos.** Reproducen los **patrones públicos**
  de la AOD española (volumen total ~3.000–4.000 M€, predominio de la vía multilateral,
  países socios del Plan Director, peso de la ayuda humanitaria y de las operaciones de
  deuda), pero **no son la contabilidad oficial exacta**. Sirven para el mapa y el desglose
  por categorías. Para sustituirlos por datos reales, ver §4 y §5.

---

## 2. Modelo de riesgo de corrupción

> ⚠️ El "riesgo de corrupción" es un **indicador de vulnerabilidad**: estima la
> *probabilidad de desvío/malversación de los fondos* en función de la gobernanza del país
> receptor y del canal y la modalidad de entrega. **No afirma** que un fondo concreto haya
> sido robado, ni acusa a personas u organizaciones.

Para cada flujo de ayuda se calcula:

```
Riesgo (0–100) = 0,50 · (100 − CPI)          ← gobernanza del receptor
               + 0,30 · riesgo_modalidad      ← cómo se entrega el dinero
               + 0,20 · riesgo_canal           ← por qué vía pasa
```

### (a) Gobernanza del receptor — CPI
**Corruption Perceptions Index** de Transparency International (2023), escala 0 (muy
corrupto) – 100 (muy limpio). `100 − CPI` convierte un país limpio en bajo riesgo.

### (b) Riesgo de la modalidad
| Modalidad | Riesgo | Razón |
|---|---:|---|
| Apoyo presupuestario | 95 | El dinero entra en el presupuesto del receptor: máxima fungibilidad, mínima trazabilidad del destino final |
| Alivio de deuda | 70 | Libera recursos del receptor sin destino finalista verificable |
| Proyecto con justificación | 45 | Hay que justificar el gasto, pero la ejecución ocurre en el país |
| En especie / asistencia técnica | 30 | Se entregan bienes o conocimiento, no efectivo |
| Humanitaria / emergencia | 25 | Control humanitario y entrega finalista |

### (c) Riesgo del canal
| Canal | Riesgo | Razón |
|---|---:|---|
| Estado a Estado | 90 | Pasa por la administración del país receptor |
| Operación de deuda | 65 | — |
| Multilateral marcado | 45 | Gestión por un organismo internacional |
| ONGD / sociedad civil | 35 | Ejecución con auditoría de la organización |
| Agencias ONU / humanitario | 20 | Sistemas de control y rendición de cuentas reforzados |

### Niveles
`bajo` < 40 ≤ `medio` < 55 ≤ `alto` < 70 ≤ `muy_alto`

### Riesgo medio ponderado por euro
Promedio del riesgo de cada destino bilateral **ponderado por su importe en euros**, de
modo que un país que recibe mucho dinero pesa más que uno que recibe poco.

**Limitaciones.** El CPI mide *percepción*, no hechos; los pesos (0,50 / 0,30 / 0,20) son
una elección razonada pero discutible; el modelo ignora salvaguardas concretas del programa
(auditorías externas, condicionalidad, tramos). Es una **señal de dónde mirar**, no una
sentencia.

---

## 3. Consejo de Ministros — datos REALES (scraping de La Moncloa)

A diferencia del mapa y las categorías (ilustrativos), la sección del **Consejo de
Ministros usa datos REALES** descargados de las referencias oficiales de La Moncloa
(`https://www.lamoncloa.gob.es/consejodeministros/referencias/`) con el script
`scripts/scrape_consejo_ministros.py`. Salida: `webapp/data/consejo_ministros_real.json`.

### Cómo se extrae
1. **Enumeración.** El listado se filtra por mes/año mediante el formulario ASP.NET
   (`SummarySearchByDate`, postback con `__VIEWSTATE`/`__EVENTVALIDATION`). Se recorre
   todo el rango (por defecto 2024-01 → mes actual) y se recogen las URL de cada Consejo.
   Los *slugs* y formatos de fecha varían (`YYYYMMDD-referencia-…`, `refcYYYYMMDD`,
   `DDMMYYYY-…`, `YYMMDD-…`) y el parser los normaliza.
2. **Descarga** de cada referencia (con caché local en `/tmp/cm_cache`).
3. **Extracción en dos niveles**, por unidades de acuerdo (`<h4>`+detalle y `<li>`):
   - Dentro de la sección *“Asuntos Exteriores, Unión Europea y Cooperación”* se acepta
     toda unidad con una **señal fuerte** de ayuda (AECID, FONPRODE, ayuda humanitaria,
     contribución a un organismo internacional, condonación/conversión de deuda, etc.).
   - Fuera de esa sección solo se aceptan unidades cuyo **título** contiene un término
     **inequívoco** (AECID, FONPRODE, UNRWA, ACNUR, UNICEF, FIDA, “marco de asociación
     para el desarrollo”…), para no arrastrar asuntos internos (deuda de las CC.AA.,
     empleo, salvamento marítimo, economía circular…).
4. **Limpieza.** Se descartan nombramientos, tratados, declaraciones institucionales,
   biografías de cargos y el Fondo de la asignación tributaria del IRPF (gasto social
   interno). De cada acuerdo se extraen importes en euros (formato español), instrumento
   (AECID/FONPRODE/Humanitaria/Multilateral/Deuda/Marco país) y país receptor (si se cita
   en el título o al inicio del detalle). Se deduplican los acuerdos que aparecen a la vez
   en la agenda y en la ampliación detallada.

### Limitaciones del scraping
Es una extracción **heurística** sobre texto en lenguaje natural: puede omitir algún
acuerdo redactado de forma atípica o, en casos raros, capturar un importe contextual.
Cada fila enlaza a su **referencia oficial** para verificación. La atribución de país es
el primer país citado en el título/inicio del detalle (puede fallar en textos que listan
varios países). El importe es el mayor euro detectado en el acuerdo.

### Uso del scraper
```bash
python3 scripts/scrape_consejo_ministros.py 2024-01 2026-06
```

---

## 4. Fuentes para datos reales

| Dato | Fuente oficial |
|---|---|
| AOD por país, sector e instrumento | **Info@OD** (DGPOLDES, Mº Asuntos Exteriores) y los datos CRS de la **OCDE-CAD** |
| Programas AECID / FONPRODE | **AECID** (transparencia y memorias) |
| Acuerdos de cooperación de los martes | **La Moncloa → Consejo de Ministros** (referencias semanales) |
| CPI por país | **Transparency International — Corruption Perceptions Index** |
| Operaciones de deuda | Mº de Economía / DGPOLDES |
| Contribuciones multilaterales | Info@OD + organismos (UE, ONU, BM, BID, BAfD) |

---

## 5. Reproducir / actualizar

```bash
python3 scripts/build_aid_data.py            # mapa + categorías (ilustrativos)
python3 scripts/scrape_consejo_ministros.py  # Consejo de Ministros (REAL, La Moncloa)
cd webapp && python3 -m http.server 8000     # abre http://localhost:8000
```

Para datos reales: sustituir las tablas `DESTINOS`, `MULTILATERAL` y `CONSEJO` de
`scripts/build_aid_data.py` por los registros descargados de Info@OD / OCDE-CAD y las
referencias del Consejo de Ministros, manteniendo las columnas (`cpi`, `channel`,
`modality`, `sectores`). El modelo de riesgo recalcula automáticamente.
