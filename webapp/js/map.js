/* map.js — mapa mundial en SVG puro (proyección equirectangular), sin librerías. */
(function (global) {
  "use strict";

  const W = 1000, H = 480;

  // Proyección equirectangular: lon/lat -> coordenadas SVG.
  function project(lng, lat) {
    return [(lng + 180) / 360 * W, (90 - lat) / 180 * H];
  }

  function ringToPath(ring) {
    let d = "";
    for (let i = 0; i < ring.length; i++) {
      const p = project(ring[i][0], ring[i][1]);
      d += (i === 0 ? "M" : "L") + p[0].toFixed(1) + " " + p[1].toFixed(1);
    }
    return d + "Z";
  }

  function featurePath(geom) {
    let d = "";
    if (geom.type === "Polygon") {
      geom.coordinates.forEach(r => { d += ringToPath(r); });
    } else if (geom.type === "MultiPolygon") {
      geom.coordinates.forEach(poly => poly.forEach(r => { d += ringToPath(r); }));
    }
    return d;
  }

  // Dibuja los países base (tierra) a partir del GeoJSON.
  async function drawBase(svg) {
    const res = await fetch("data/world-countries.geo.json");
    const gj = await res.json();
    const ns = "http://www.w3.org/2000/svg";
    const g = document.createElementNS(ns, "g");
    g.setAttribute("id", "land");
    for (const f of gj.features) {
      const path = document.createElementNS(ns, "path");
      path.setAttribute("d", featurePath(f.geometry));
      path.setAttribute("class", "country");
      g.appendChild(path);
    }
    svg.appendChild(g);
  }

  global.WorldMap = { W, H, project, drawBase };
})(window);
