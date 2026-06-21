# Metodología y fuentes

Web app **"¿A dónde va la ayuda exterior de España?"** — mapa de la Ayuda Oficial al
Desarrollo (AOD) española, cotejo con el Consejo de Ministros y riesgo de corrupción estimado.

---

## 1. Naturaleza de los datos

Las cifras incluidas en `webapp/data/*.json` son **ilustrativas y representativas**:
reproducen los **patrones públicos** de la AOD española (volumen total ~3.000–4.000 M€,
predominio de la vía multilateral, países socios prioritarios del Plan Director, peso de la
ayuda humanitaria y de las operaciones de deuda), pero **no son la contabilidad oficial
exacta de un ejercicio concreto**. Sirven para demostrar el producto y la metodología.

Para sustituirlas por **datos reales**, ver §4 (fuentes) y §5 (reproducción).

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

## 3. Cotejo con el Consejo de Ministros

El Consejo de Ministros se reúne habitualmente los **martes** y aprueba periódicamente
acuerdos de cooperación (créditos FONPRODE, subvenciones AECID, ayuda humanitaria,
contribuciones multilaterales, operaciones de deuda). En `consejo_ministros.json` cada
acuerdo se compara con los desembolsos registrados:

- `ok` — el importe acordado coincide con el desembolso registrado.
- `parcial` — ejecutado parcialmente o pendiente de justificar.
- `sin_rastro` — acordado pero **sin desembolso trazable** todavía (señal de seguimiento).

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
python3 scripts/build_aid_data.py     # regenera webapp/data/*.json
cd webapp && python3 -m http.server 8000   # abre http://localhost:8000
```

Para datos reales: sustituir las tablas `DESTINOS`, `MULTILATERAL` y `CONSEJO` de
`scripts/build_aid_data.py` por los registros descargados de Info@OD / OCDE-CAD y las
referencias del Consejo de Ministros, manteniendo las columnas (`cpi`, `channel`,
`modality`, `sectores`). El modelo de riesgo recalcula automáticamente.
