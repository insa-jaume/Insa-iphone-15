#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_standalone.py
===================
Empaqueta la web app en UN SOLO fichero HTML autocontenido (CSS + JS + datos +
mapamundi embebidos), abrible con doble clic sin servidor (file://).

Salida: webapp/dist/index_standalone.html
"""
import os, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "webapp")
DIST = os.path.join(WEB, "dist")

def read(p):
    return open(os.path.join(WEB, p), encoding="utf-8").read()

def main():
    html = read("index.html")
    css = read("css/styles.css")
    mapjs = read("js/map.js")
    appjs = read("js/app.js")
    bundle = {
        "data/aod_real.json": json.loads(read("data/aod_real.json")),
        "data/consejo_ministros_real.json": json.loads(read("data/consejo_ministros_real.json")),
        "data/world-countries.geo.json": json.loads(read("data/world-countries.geo.json")),
    }

    # Quitar enlaces externos a css/js y placeholders
    html = re.sub(r'<link rel="stylesheet" href="css/styles.css">', "", html)
    html = re.sub(r'<script src="js/map.js"></script>', "", html)
    html = re.sub(r'<script src="js/app.js"></script>', "", html)

    shim = (
        "<script>window.__BUNDLE__=" + json.dumps(bundle, ensure_ascii=False) + ";"
        "(function(){const orig=window.fetch;window.fetch=function(u){"
        "if(window.__BUNDLE__[u]!==undefined){return Promise.resolve("
        "{ok:true,json:function(){return Promise.resolve(window.__BUNDLE__[u]);},"
        "text:function(){return Promise.resolve(JSON.stringify(window.__BUNDLE__[u]));}});}"
        "return orig?orig.apply(this,arguments):Promise.reject(new Error('sin red: '+u));};})();"
        "</script>"
    )

    inline = (
        "<style>\n" + css + "\n</style>\n" +
        shim + "\n" +
        "<script>\n" + mapjs + "\n</script>\n" +
        "<script>\n" + appjs + "\n</script>\n"
    )
    # Insertar antes de </body>
    out = html.replace("</body>", inline + "\n</body>")

    os.makedirs(DIST, exist_ok=True)
    path = os.path.join(DIST, "index_standalone.html")
    open(path, "w", encoding="utf-8").write(out)
    print(f"Escrito {path} ({os.path.getsize(path):,} bytes)")

if __name__ == "__main__":
    main()
