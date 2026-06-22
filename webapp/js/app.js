/* app.js — carga de datos y render de la web app de ayuda exterior de España. */
(function () {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";
  const RISK_COLOR = {
    bajo: "var(--r-bajo)", medio: "var(--r-medio)",
    alto: "var(--r-alto)", muy_alto: "var(--r-muy_alto)",
  };
  const RISK_HEX = { bajo: "#2ea043", medio: "#d4a017", alto: "#e8590c", muy_alto: "#d1242f" };
  const RISK_LABEL = { bajo: "Bajo", medio: "Medio", alto: "Alto", muy_alto: "Muy alto" };

  const eur = n => new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);
  const eurM = n => (n >= 1e9 ? (n / 1e9).toLocaleString("es-ES", { maximumFractionDigits: 2 }) + " mil M€"
    : (n / 1e6).toLocaleString("es-ES", { maximumFractionDigits: 1 }) + " M€");
  const $ = sel => document.querySelector(sel);

  let AID, CATS, CM;

  async function main() {
    [AID, CATS, CM] = await Promise.all([
      fetch("data/aid.json").then(r => r.json()),
      fetch("data/categories.json").then(r => r.json()),
      fetch("data/consejo_ministros_real.json").then(r => r.json()),
    ]);

    $("#ej").textContent = AID.ejercicio;
    $("#disclaimer").innerHTML =
      "ℹ️ La sección del <b>Consejo de Ministros es de datos REALES</b>, extraídos de las referencias de La Moncloa. " +
      "El mapa y las categorías usan cifras <b>ilustrativas</b> de los patrones de la AOD. El “riesgo de corrupción” es un " +
      "<b>indicador de vulnerabilidad estimado</b> (probabilidad de desvío por gobernanza y canal), no una acusación. Ver metodología.";

    renderKPIs();
    await renderMap();
    renderCategories();
    renderConsejoControls();
    renderConsejo();
  }

  /* ---------------- KPIs ---------------- */
  function renderKPIs() {
    const k = [
      { v: eurM(AID.total_aod), l: "AOD total ilustrativa (ej. " + AID.ejercicio + ")" },
      { v: CM.n_acuerdos, l: "Acuerdos reales de cooperación del Consejo de Min." },
      { v: eurM(CM.total_eur_identificado), l: "€ reales identificados (" + CM.rango.desde + "→" + CM.rango.hasta + ")" },
      { v: AID.riesgo_medio_ponderado + "/100", l: "Riesgo medio ponderado por €", risk: true },
    ];
    $("#kpis").innerHTML = k.map(x =>
      `<div class="kpi"><div class="v${x.risk ? " risk" : ""}">${x.v}</div><div class="l">${x.l}</div></div>`
    ).join("");
  }

  /* ---------------- Mapa ---------------- */
  async function renderMap() {
    const svg = $("#map");
    await WorldMap.drawBase(svg);

    const maxEur = Math.max(...AID.destinos.map(d => d.eur));
    const rOf = e => 4 + 26 * Math.sqrt(e / maxEur); // radio por raíz del importe

    const g = document.createElementNS(NS, "g");
    g.setAttribute("id", "bubbles");
    // mayor primero para que las pequeñas queden encima y sean clicables
    [...AID.destinos].sort((a, b) => b.eur - a.eur).forEach(d => {
      const [x, y] = WorldMap.project(d.lng, d.lat);
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("cx", x); c.setAttribute("cy", y);
      c.setAttribute("r", rOf(d.eur));
      c.setAttribute("class", "bubble");
      c.setAttribute("fill", RISK_HEX[d.nivel]);
      c.dataset.iso = d.iso;
      c.addEventListener("mousemove", e => showTip(e, d));
      c.addEventListener("mouseleave", hideTip);
      c.addEventListener("click", () => selectCountry(d.iso));
      g.appendChild(c);
    });
    svg.appendChild(g);
  }

  function showTip(e, d) {
    const t = $("#tip");
    t.style.display = "block";
    t.style.left = Math.min(e.clientX + 14, window.innerWidth - 250) + "px";
    t.style.top = (e.clientY + 14) + "px";
    t.innerHTML =
      `<b>${d.name}</b><br>${eur(d.eur)}<br>` +
      `Riesgo: ${d.riesgo}/100 (${RISK_LABEL[d.nivel]})` +
      `<div class="riskbar"><i style="width:${d.riesgo}%;background:${RISK_HEX[d.nivel]}"></i></div>`;
  }
  function hideTip() { $("#tip").style.display = "none"; }

  /* ---------------- Panel de detalle ---------------- */
  function selectCountry(iso) {
    document.querySelectorAll("#bubbles .bubble").forEach(b =>
      b.classList.toggle("sel", b.dataset.iso === iso));
    const d = AID.destinos.find(x => x.iso === iso);
    if (!d) return;

    const CH = { estado: "Estado a Estado", ong: "ONGD / sociedad civil", multi_ear: "Multilateral marcado", un_human: "Agencias ONU / humanitario", deuda: "Operación de deuda" };
    const MO = { apoyo_presup: "Apoyo presupuestario", proyecto: "Proyecto con justificación", humanitaria: "Humanitaria / emergencia", especie: "En especie / asistencia técnica", deuda: "Alivio de deuda" };
    const SL = {
      humanitaria: "Ayuda humanitaria", salud: "Salud", educacion: "Educación", gobernanza: "Gobernanza",
      agua: "Agua y saneam.", desarrollo_rural: "Desarrollo rural", seguridad_alimentaria: "Seg. alimentaria",
      medio_ambiente: "Medio ambiente", genero: "Igualdad de género", paz: "Construcción de paz",
      migracion: "Migración", pesca: "Pesca",
    };

    const sectores = Object.entries(d.sectores).sort((a, b) => b[1] - a[1]).map(([s, f]) =>
      `<div class="sbar"><span class="nm">${SL[s] || s}</span>
        <span class="track"><i style="width:${(f * 100).toFixed(0)}%"></i></span>
        <span class="pc">${(f * 100).toFixed(0)}%</span></div>`).join("");

    $("#detail").innerHTML =
      `<div class="det-h"><h2 style="margin:0">${d.name}</h2>
        <span class="amt">${eur(d.eur)}</span></div>
      <div style="margin:6px 0 12px">
        <span class="badge" style="background:${RISK_HEX[d.nivel]}">Riesgo ${d.riesgo}/100 · ${RISK_LABEL[d.nivel]}</span>
      </div>
      <div class="det-row"><span>CPI receptor (Transp. Int. 2023)</span><b>${d.cpi}/100</b></div>
      <div class="det-row"><span>Canal de entrega</span><b>${CH[d.channel]}</b></div>
      <div class="det-row"><span>Modalidad</span><b>${MO[d.modality]}</b></div>
      <div class="sectors"><div class="sub" style="margin:12px 0 4px">Sectores de gasto</div>${sectores}</div>
      <div class="sub" style="margin-top:12px">Acuerdos del Consejo de Ministros para ${d.name}:</div>
      ${consejoFor(iso)}`;
    $("#detail").scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function consejoFor(iso) {
    const items = CM.acuerdos.filter(a => a.iso === iso);
    if (!items.length) return `<div class="sub">— sin acuerdos reales registrados para este país —</div>`;
    return items.map(a =>
      `<div class="det-row"><span><a href="${a.url}" target="_blank" rel="noopener">${a.fecha}</a> · ${a.titulo.slice(0, 90)}</span>
        <b>${a.eur ? eur(a.eur) : "—"}</b></div>`).join("");
  }

  /* ---------------- Categorías ---------------- */
  function renderCategories() {
    const max = Math.max(...CATS.categorias.map(c => c.eur));
    $("#cats").innerHTML = CATS.categorias.map(c =>
      `<div class="catbar">
        <span class="nm">${c.label}</span>
        <span class="track"><i style="width:${(c.eur / max * 100).toFixed(1)}%"></i></span>
        <span class="val">${eurM(c.eur)}</span>
      </div>`).join("");
  }

  /* ---------------- Consejo de Ministros (tabla) — datos reales ---------------- */
  let cmFilter = "all", cmSort = { key: "fecha", dir: -1 };

  function riskOf(iso) {
    const d = AID.destinos.find(x => x.iso === iso);
    return d ? d : null;
  }

  function renderConsejoControls() {
    // chips dinámicos por instrumento + nota de fuente
    const insts = [...new Set(CM.acuerdos.map(a => a.instrumento))].sort();
    $("#cm-filters").innerHTML =
      `<span class="chip on" data-f="all">Todos (${CM.acuerdos.length})</span>` +
      insts.map(i => `<span class="chip" data-f="${i}">${i} (${CM.acuerdos.filter(a => a.instrumento === i).length})</span>`).join("");
    $("#cm-sub").innerHTML +=
      ` <br><b>${CM.n_referencias}</b> referencias analizadas · <b>${CM.n_acuerdos}</b> acuerdos de cooperación ` +
      `(<b>${CM.n_acuerdos_con_importe}</b> con importe) · <b>${eurM(CM.total_eur_identificado)}</b> identificados. ` +
      `Descargado el ${(CM.descargado || "").slice(0, 10)} con <code>scripts/scrape_consejo_ministros.py</code>.`;
  }

  function renderConsejo() {
    const tbody = $("#cm-table tbody");
    let rows = CM.acuerdos.slice();
    if (cmFilter !== "all") rows = rows.filter(r => r.instrumento === cmFilter);
    rows.sort((a, b) => {
      let va = cmSort.key === "riesgo" ? (riskOf(a.iso)?.riesgo ?? -1) : a[cmSort.key];
      let vb = cmSort.key === "riesgo" ? (riskOf(b.iso)?.riesgo ?? -1) : b[cmSort.key];
      if (va == null) va = (typeof vb === "number" ? -1 : ""); if (vb == null) vb = (typeof va === "number" ? -1 : "");
      return (va > vb ? 1 : va < vb ? -1 : 0) * cmSort.dir;
    });
    tbody.innerHTML = rows.map(r => {
      const d = riskOf(r.iso);
      const riesgo = d ? `<span class="mini" style="background:${RISK_HEX[d.nivel]};color:#0a0f16">${d.riesgo}</span>` : "—";
      return `<tr>
        <td><a href="${r.url}" target="_blank" rel="noopener" title="Ver referencia oficial">${r.fecha || "—"}</a></td>
        <td><span class="tag">${r.instrumento}</span></td>
        <td title="${(r.detalle || r.titulo).replace(/"/g, "&quot;").slice(0, 280)}">${r.titulo}</td>
        <td>${r.pais || "—"}</td>
        <td class="num">${r.eur ? eur(r.eur) : "—"}</td>
        <td class="num">${riesgo}</td>
      </tr>`;
    }).join("");
  }

  $("#cm-filters").addEventListener("click", e => {
    const chip = e.target.closest(".chip"); if (!chip) return;
    cmFilter = chip.dataset.f;
    document.querySelectorAll("#cm-filters .chip").forEach(c => c.classList.toggle("on", c === chip));
    renderConsejo();
  });
  $("#cm-table thead").addEventListener("click", e => {
    const th = e.target.closest("th"); if (!th) return;
    const key = th.dataset.s;
    cmSort.dir = (cmSort.key === key) ? -cmSort.dir : 1;
    cmSort.key = key;
    renderConsejo();
  });

  main().catch(err => {
    console.error(err);
    $("#disclaimer").innerHTML = "❌ Error cargando los datos: " + err.message;
  });
})();
