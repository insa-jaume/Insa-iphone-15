/* app.js — web app de la AOD española con DATOS REALES (multi-año). */
(function () {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";
  const RISK_HEX = { bajo: "#2ea043", medio: "#d4a017", alto: "#e8590c", muy_alto: "#d1242f", n_d: "#5a6473" };
  const RISK_LABEL = { bajo: "Bajo", medio: "Medio", alto: "Alto", muy_alto: "Muy alto", n_d: "s/d" };

  const SECTOR_LABEL = {
    salud: "Salud y población", educacion: "Educación", educación: "Educación",
    gobernanza: "Gobierno y sociedad civil", "gobierno y sociedad civil": "Gobierno y sociedad civil",
    agua: "Agua y saneamiento", "agua y saneamiento": "Agua y saneamiento",
    humanitaria: "Acción humanitaria", "accion humanitaria": "Acción humanitaria",
    multisectorial: "Multisectorial", educación_básica: "Educación",
    "desarrollo rural": "Agricultura y desarrollo rural", desarrollo_rural: "Agricultura y desarrollo rural",
    "medio ambiente": "Medio ambiente y clima", medio_ambiente: "Medio ambiente y clima",
    genero: "Igualdad de género", "infraestructuras sociales": "Infraestructuras sociales",
    "refugiados en donante": "Refugiados en España", "costes administrativos": "Costes administrativos",
  };

  const eur = n => n == null ? "—" : new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);
  const eurM = n => n == null ? "s/d" : (n >= 1e9 ? (n / 1e9).toLocaleString("es-ES", { maximumFractionDigits: 2 }) + " mil M€"
    : (n / 1e6).toLocaleString("es-ES", { maximumFractionDigits: 1 }) + " M€");
  const $ = s => document.querySelector(s);
  const $$ = s => document.querySelectorAll(s);

  let AOD, CM, YEAR, baseDrawn = false;

  async function main() {
    [AOD, CM] = await Promise.all([
      fetch("data/aod_real.json").then(r => r.json()),
      fetch("data/consejo_ministros_real.json").then(r => r.json()),
    ]);

    $("#disclaimer").innerHTML =
      "✅ <b>Datos REALES</b> de la AOD española (DGPOLDES / Info@OD / OCDE-CAD / AECID) y del Consejo de Ministros (La Moncloa). " +
      "El <b>riesgo de corrupción = 100 − CPI</b> (Transparency International): indicador de vulnerabilidad de gobernanza, no una acusación.";

    // año por defecto: el más reciente con datos de países
    const conDatos = AOD.anios.filter(y => (AOD.por_anio[String(y)]?.paises || []).length);
    YEAR = conDatos.length ? Math.max(...conDatos) : Math.max(...AOD.anios);

    renderYears();
    await renderMapBase();
    renderConsejoControls();
    renderCasos();
    setYear(YEAR);
  }

  function yd(y) { return AOD.por_anio[String(y)] || {}; }

  /* ---------------- Selector de año ---------------- */
  function renderYears() {
    $("#years").innerHTML = AOD.anios.map(y => {
      const pre = yd(y).preliminar ? " <span class='prelim'>prelim.</span>" : "";
      return `<button class="ytab" data-y="${y}">${y}${pre}</button>`;
    }).join("");
    $("#years").addEventListener("click", e => {
      const b = e.target.closest(".ytab"); if (!b) return;
      setYear(+b.dataset.y);
    });
  }

  function setYear(y) {
    YEAR = y;
    $$(".ytab").forEach(b => b.classList.toggle("on", +b.dataset.y === y));
    $$(".yr").forEach(s => s.textContent = y);
    renderKPIs(); renderBubbles(); renderCats(); renderMulti(); renderConsejo();
    $("#detail").innerHTML = `<div class="empty">Selecciona un país en el mapa para ver su importe real (${y}), el CPI y el riesgo de corrupción.</div>`;
  }

  /* ---------------- KPIs ---------------- */
  function renderKPIs() {
    const d = yd(YEAR);
    const k = [
      { v: eurM(d.total_eur), l: `AOD total ${YEAR}${d.preliminar ? " (prelim.)" : ""}` },
      { v: d.pct_rnb != null ? d.pct_rnb.toLocaleString("es-ES") + "%" : "s/d", l: "% de la Renta Nacional Bruta" },
      { v: d.bilateral_eur != null ? eurM(d.bilateral_eur) : "s/d", l: "Bilateral · " + (d.multilateral_eur != null ? eurM(d.multilateral_eur) + " multilateral" : "—") },
      { v: d.riesgo_medio_ponderado != null ? d.riesgo_medio_ponderado + "/100" : "s/d", l: "Riesgo medio ponderado por €", risk: true },
    ];
    $("#kpis").innerHTML = k.map(x =>
      `<div class="kpi"><div class="v${x.risk ? " risk" : ""}">${x.v}</div><div class="l">${x.l}</div></div>`).join("");
  }

  /* ---------------- Mapa ---------------- */
  async function renderMapBase() {
    if (baseDrawn) return;
    await WorldMap.drawBase($("#map"));
    const g = document.createElementNS(NS, "g"); g.setAttribute("id", "bubbles");
    $("#map").appendChild(g);
    baseDrawn = true;
  }

  function renderBubbles() {
    const g = $("#bubbles"); g.innerHTML = "";
    const paises = (yd(YEAR).paises || []).filter(p => p.eur);
    if (!paises.length) return;
    const maxEur = Math.max(...paises.map(p => p.eur));
    const rOf = e => 4 + 26 * Math.sqrt(e / maxEur);
    [...paises].sort((a, b) => b.eur - a.eur).forEach(d => {
      const [x, y] = WorldMap.project(d.lng, d.lat);
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("cx", x); c.setAttribute("cy", y); c.setAttribute("r", rOf(d.eur));
      c.setAttribute("class", "bubble"); c.setAttribute("fill", RISK_HEX[d.nivel] || RISK_HEX.n_d);
      c.dataset.iso = d.iso;
      c.addEventListener("mousemove", e => showTip(e, d));
      c.addEventListener("mouseleave", hideTip);
      c.addEventListener("click", () => selectCountry(d.iso));
      g.appendChild(c);
    });
  }

  function showTip(e, d) {
    const t = $("#tip"); t.style.display = "block";
    t.style.left = Math.min(e.clientX + 14, window.innerWidth - 250) + "px";
    t.style.top = (e.clientY + 14) + "px";
    t.innerHTML = `<b>${d.name}</b><br>${eur(d.eur)} (${YEAR})<br>` +
      (d.cpi != null ? `CPI ${d.cpi} · riesgo ${d.riesgo}/100 (${RISK_LABEL[d.nivel]})
        <div class="riskbar"><i style="width:${d.riesgo}%;background:${RISK_HEX[d.nivel]}"></i></div>` : "CPI no disponible");
  }
  function hideTip() { $("#tip").style.display = "none"; }

  function selectCountry(iso) {
    $$("#bubbles .bubble").forEach(b => b.classList.toggle("sel", b.dataset.iso === iso));
    const d = (yd(YEAR).paises || []).find(x => x.iso === iso);
    if (!d) return;
    $("#detail").innerHTML =
      `<div class="det-h"><h2 style="margin:0">${d.name}</h2><span class="amt">${eur(d.eur)}</span></div>
       <div style="margin:6px 0 12px">
         ${d.cpi != null ? `<span class="badge" style="background:${RISK_HEX[d.nivel]}">Riesgo ${d.riesgo}/100 · ${RISK_LABEL[d.nivel]}</span>` : `<span class="tag">CPI no disponible</span>`}
       </div>
       <div class="det-row"><span>Año</span><b>${YEAR}</b></div>
       <div class="det-row"><span>AOD bilateral recibida</span><b>${eur(d.eur)}</b></div>
       <div class="det-row"><span>CPI (Transparency Int.)</span><b>${d.cpi != null ? d.cpi + "/100" : "—"}</b></div>
       <div class="det-row"><span>Riesgo de corrupción (100−CPI)</span><b>${d.riesgo != null ? d.riesgo + "/100" : "—"}</b></div>
       <div class="sub" style="margin-top:12px">Acuerdos reales del Consejo de Ministros para ${d.name}:</div>
       ${consejoFor(iso)}`;
    $("#detail").scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function consejoFor(iso) {
    const items = CM.acuerdos.filter(a => a.iso === iso);
    if (!items.length) return `<div class="sub">— sin acuerdos reales registrados —</div>`;
    return items.map(a =>
      `<div class="det-row"><span><a href="${a.url}" target="_blank" rel="noopener">${a.fecha || "—"}</a> · ${(a.titulo || "").slice(0, 90)}</span>
        <b>${a.eur ? eur(a.eur) : "—"}</b></div>`).join("");
  }

  /* ---------------- Categorías / sectores ---------------- */
  function renderCats() {
    const secs = (yd(YEAR).sectores || []).map(s => ({
      label: s.label || SECTOR_LABEL[(s.sector || "").toLowerCase()] || s.sector,
      eur: s.eur, pct: s.pct,
    })).filter(s => s.eur != null || s.pct != null);
    if (!secs.length) { $("#cats").innerHTML = `<div class="sub">Sin desglose sectorial publicado para ${YEAR}.</div>`; return; }
    const useEur = secs.some(s => s.eur != null);
    secs.sort((a, b) => (useEur ? (b.eur || 0) - (a.eur || 0) : (b.pct || 0) - (a.pct || 0)));
    const max = useEur ? Math.max(...secs.map(s => s.eur || 0)) : Math.max(...secs.map(s => s.pct || 0));
    $("#cats").innerHTML = secs.map(s => {
      const val = useEur ? (s.eur || 0) : (s.pct || 0);
      const txt = s.eur != null ? eurM(s.eur) : (s.pct != null ? s.pct + "%" : "");
      return `<div class="catbar"><span class="nm">${s.label}</span>
        <span class="track"><i style="width:${(val / max * 100).toFixed(1)}%"></i></span>
        <span class="val">${txt}</span></div>`;
    }).join("");
  }

  /* ---------------- Multilateral ---------------- */
  function renderMulti() {
    const ms = (yd(YEAR).multilateral || []).filter(m => m.eur != null);
    if (!ms.length) { $("#multi").innerHTML = `<div class="sub">Sin desglose multilateral para ${YEAR}.</div>`; return; }
    ms.sort((a, b) => (b.eur || 0) - (a.eur || 0));
    const max = Math.max(...ms.map(m => m.eur));
    $("#multi").innerHTML = ms.map(m =>
      `<div class="catbar"><span class="nm">${m.name}</span>
        <span class="track"><i style="width:${(m.eur / max * 100).toFixed(1)}%;background:linear-gradient(90deg,#2f81f7,#1f6feb)"></i></span>
        <span class="val">${eurM(m.eur)}</span></div>`).join("");
  }

  /* ---------------- Casos reales de fraude ---------------- */
  function renderCasos() {
    const casos = (AOD.gobernanza?.casos || []);
    if (!casos.length) { $("#casos-card").style.display = "none"; return; }
    $("#casos").innerHTML = casos.map(c =>
      `<div class="caso">
        <div class="caso-h">${c.anio ? `<span class="tag">${c.anio}</span> ` : ""}<b>${c.titulo}</b></div>
        <div class="caso-b">${c.resumen || ""}</div>
        ${c.fuente ? `<a href="${c.fuente}" target="_blank" rel="noopener">fuente ↗</a>` : ""}
      </div>`).join("");
  }

  /* ---------------- Consejo de Ministros ---------------- */
  let cmFilter = "all", cmSort = { key: "fecha", dir: -1 };
  function cpiOf(iso) { return AOD.gobernanza?.cpi?.[iso]; }
  function riskOf(iso) { const c = cpiOf(iso); return c == null ? null : Math.round(100 - c); }
  function riskNivel(r) { return r == null ? "n_d" : r >= 70 ? "muy_alto" : r >= 55 ? "alto" : r >= 40 ? "medio" : "bajo"; }

  function renderConsejoControls() {
    const insts = [...new Set(CM.acuerdos.map(a => a.instrumento))].sort();
    $("#cm-filters").innerHTML =
      `<span class="chip on" data-f="all">Todos (${CM.acuerdos.length})</span>` +
      insts.map(i => `<span class="chip" data-f="${i}">${i} (${CM.acuerdos.filter(a => a.instrumento === i).length})</span>`).join("");
    $("#cm-sub").innerHTML +=
      ` <br><b>${CM.n_referencias}</b> referencias analizadas · <b>${CM.n_acuerdos}</b> acuerdos de cooperación ` +
      `(<b>${CM.n_acuerdos_con_importe}</b> con importe). Descargado el ${(CM.descargado || "").slice(0, 10)}.`;
    $("#cm-filters").addEventListener("click", e => {
      const chip = e.target.closest(".chip"); if (!chip) return;
      cmFilter = chip.dataset.f;
      $$("#cm-filters .chip").forEach(c => c.classList.toggle("on", c === chip));
      renderConsejo();
    });
    $("#cm-table thead").addEventListener("click", e => {
      const th = e.target.closest("th"); if (!th) return;
      const key = th.dataset.s;
      cmSort.dir = (cmSort.key === key) ? -cmSort.dir : 1; cmSort.key = key;
      renderConsejo();
    });
  }

  function renderConsejo() {
    const tbody = $("#cm-table tbody");
    let rows = CM.acuerdos.slice();
    if (cmFilter !== "all") rows = rows.filter(r => r.instrumento === cmFilter);
    rows.sort((a, b) => {
      let va = cmSort.key === "riesgo" ? (riskOf(a.iso) ?? -1) : a[cmSort.key];
      let vb = cmSort.key === "riesgo" ? (riskOf(b.iso) ?? -1) : b[cmSort.key];
      if (va == null) va = (typeof vb === "number" ? -1 : ""); if (vb == null) vb = (typeof va === "number" ? -1 : "");
      return (va > vb ? 1 : va < vb ? -1 : 0) * cmSort.dir;
    });
    tbody.innerHTML = rows.map(r => {
      const rk = riskOf(r.iso);
      const riesgo = rk != null ? `<span class="mini" style="background:${RISK_HEX[riskNivel(rk)]};color:#0a0f16">${rk}</span>` : "—";
      return `<tr>
        <td><a href="${r.url}" target="_blank" rel="noopener" title="Ver referencia oficial">${r.fecha || "—"}</a></td>
        <td><span class="tag">${r.instrumento}</span></td>
        <td title="${((r.detalle || r.titulo) || "").replace(/"/g, "&quot;").slice(0, 280)}">${r.titulo}</td>
        <td>${r.pais || "—"}</td>
        <td class="num">${r.eur ? eur(r.eur) : "—"}</td>
        <td class="num">${riesgo}</td>
      </tr>`;
    }).join("");
  }

  main().catch(err => {
    console.error(err);
    $("#disclaimer").innerHTML = "❌ Error cargando los datos: " + err.message;
  });
})();
