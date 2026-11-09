#!/usr/bin/env node
/*
  Renderiza el prospecto a partir de folleto.html + folleto.json:
    - folleto-whatsapp.png  (1080 × 1350, para mandar como imagen)
    - folleto.pdf           (1 página de 1080 × 1350 px, para mandar como documento)

  Uso:   node render-folleto.js            (desde cualquier carpeta)
         node render-folleto.js --medidas  (además imprime las medidas de cada bloque)

  Las portadas de los demos se leen de las rutas de folleto.json en cada corrida:
  si el archivo existe, se usa; si no, queda el recuadro "EJEMPLO".
*/
"use strict";

const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

const DIR = __dirname;
const HTML = path.join(DIR, "folleto.html");
const DATOS = path.join(DIR, "folleto.json");
const PNG = path.join(DIR, "folleto-whatsapp.png");
const PDF = path.join(DIR, "folleto.pdf");
const ANCHO = 1080;
const ALTO = 1350;
const FUENTES = path.resolve(DIR, "../../plantillas/remotion/public/fonts");
const PESOS = [500, 600, 700, 800, 900];

// Valores de ejemplo: si siguen así, se avisa al final.
const EJEMPLOS = {
  nombre: "Tu Nombre",
  instagram: "@tu.usuario",
  whatsapp: "WhatsApp: tu número",
  foto: "tu-foto.jpg",
};

function salir(msg) {
  console.error("\nERROR: " + msg + "\n");
  process.exit(1);
}

function leerDatos() {
  let txt;
  try {
    txt = fs.readFileSync(DATOS, "utf8");
  } catch (e) {
    salir("No encuentro " + DATOS);
  }
  try {
    return JSON.parse(txt);
  } catch (e) {
    salir("folleto.json tiene un error de formato (" + e.message + ").\n" +
      "Revisá comillas y comas: cada dato va \"entre comillas\" y separado por coma.");
  }
}

// Devuelve la URL file:// de una imagen si existe y no está vacía; si no, null.
function imagen(ruta) {
  if (!ruta || typeof ruta !== "string") return null;
  const abs = path.isAbsolute(ruta) ? ruta : path.resolve(DIR, ruta);
  try {
    const st = fs.statSync(abs);
    if (!st.isFile() || st.size === 0) return null;
  } catch (e) {
    return null;
  }
  return { abs, url: pathToFileURL(abs).href };
}

function linkWhatsApp(valor) {
  const digitos = String(valor || "").replace(/\D/g, "");
  return digitos.length >= 10 ? "https://wa.me/" + digitos : null;
}

function linkInstagram(usuario) {
  const u = String(usuario || "").trim().replace(/^@/, "");
  if (!u || "@" + u === EJEMPLOS.instagram || !/^[A-Za-z0-9._]{1,30}$/.test(u)) return null;
  return "https://www.instagram.com/" + u + "/";
}

function contarPaginas(pdfPath) {
  const crudo = fs.readFileSync(pdfPath).toString("latin1");
  const m = crudo.match(/\/Type\s*\/Page(?!s)/g);
  return m ? m.length : 0;
}

(async () => {
  const conMedidas = process.argv.includes("--medidas");
  const d = leerDatos();
  const avisos = [];

  for (const w of PESOS) {
    const f = path.join(FUENTES, "inter-latin-" + w + "-normal.woff2");
    if (!fs.existsSync(f)) salir("Falta la fuente " + f + " (el HTML la carga con @font-face).");
  }

  // Foto / logo
  const foto = imagen(d.foto);
  if (d.foto && !foto) avisos.push("Foto: no encontré \"" + d.foto + "\" → uso las iniciales.");

  // Demos: se toman solos cuando aparecen
  const demos = (Array.isArray(d.demos) ? d.demos : []).map((x) => {
    const img = imagen(x && x.imagen);
    return { rubro: x && x.rubro, imagen: x && x.imagen, src: img ? img.url : null };
  });
  const demosOk = demos.filter((x) => x.src).length;

  const datosPagina = Object.assign({}, d, {
    fotoSrc: foto ? foto.url : null,
    demos,
    whatsappHref: linkWhatsApp(d.whatsapp_link),
    instagramHref: linkInstagram(d.instagram),
  });

  const browser = await chromium.launch();
  let problemas = [];
  let medidas = null;
  try {
    const page = await browser.newPage({ viewport: { width: ANCHO, height: ALTO }, deviceScaleFactor: 1 });
    page.on("pageerror", (e) => avisos.push("Error en la página: " + e.message));
    await page.goto(pathToFileURL(HTML).href, { waitUntil: "load" });

    const avisosPagina = await page.evaluate((datos) => window.aplicarDatos(datos), datosPagina);
    avisos.push(...avisosPagina);

    // Las 5 variantes de Inter tienen que estar cargadas (si no, el PNG sale con otra letra).
    const fuentes = await page.evaluate(async (pesos) => {
      await Promise.all(pesos.map((w) => document.fonts.load(w + ' 40px "Inter Folleto"')));
      await document.fonts.ready;
      return pesos.map((w) => {
        const f = [...document.fonts].find((x) => x.family.replace(/"/g, "") === "Inter Folleto" && String(x.weight) === String(w));
        return { w, ok: !!f && f.status === "loaded" };
      });
    }, PESOS);
    const malas = fuentes.filter((f) => !f.ok).map((f) => f.w);
    if (malas.length) salir("No cargaron estas variantes de Inter: " + malas.join(", ") + ". Revisá la carpeta " + FUENTES);

    await page.evaluate((n) => { document.title = (n && n !== "Tu Nombre" ? n + " · " : "") + "Reels para tu negocio"; }, d.nombre);

    problemas = await page.evaluate(() => window.chequearDiseno());
    if (conMedidas) medidas = await page.evaluate(() => window.medidas());

    await page.screenshot({ path: PNG, clip: { x: 0, y: 0, width: ANCHO, height: ALTO }, animations: "disabled" });

    await page.pdf({
      path: PDF,
      width: ANCHO + "px",
      height: ALTO + "px",
      printBackground: true,
      preferCSSPageSize: true,
      pageRanges: "1",
      margin: { top: "0", right: "0", bottom: "0", left: "0" },
    });
  } finally {
    await browser.close();
  }

  const paginas = contarPaginas(PDF);
  if (paginas !== 1) problemas.push("El PDF salió con " + paginas + " páginas (tiene que ser 1).");

  // ---- Informe ----
  console.log("\nListo:");
  console.log("  " + PNG + "  (" + ANCHO + "×" + ALTO + ")");
  console.log("  " + PDF + "  (" + paginas + " página)");
  console.log("\nDemos: " + demosOk + " de " + demos.length + " con imagen" +
    (demosOk < demos.length ? " (los que faltan quedan como recuadro EJEMPLO):" : "."));
  demos.forEach((x) => console.log("  " + (x.src ? "[imagen]  " : "[recuadro]") + " " + (x.rubro || "") + " ← " + (x.imagen || "(sin ruta)")));

  const deEjemplo = Object.keys(EJEMPLOS).filter((k) => String(d[k] || "").trim() === EJEMPLOS[k]);
  if (deEjemplo.length) {
    console.log("\nDATOS DE EJEMPLO (cambialos en folleto.json antes de mandar): " + deEjemplo.join(", "));
  }
  if (!datosPagina.whatsappHref) console.log("Opcional: completá \"whatsapp_link\" (ej. 5491123456789) para que el PDF abra el chat al tocar.");
  if (avisos.length) {
    console.log("\nAvisos:");
    avisos.forEach((a) => console.log("  - " + a));
  }
  if (problemas.length) {
    console.log("\nREVISAR DISEÑO:");
    problemas.forEach((p) => console.log("  - " + p));
  } else {
    console.log("\nRevisión automática: nada cortado ni fuera de la hoja.");
  }
  if (medidas) console.log("\nMedidas:", JSON.stringify(medidas, null, 1));
  console.log("");
})().catch((e) => salir(e && e.stack ? e.stack : String(e)));
