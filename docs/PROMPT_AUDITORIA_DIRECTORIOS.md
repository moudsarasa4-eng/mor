# Prompt de auditoría — subdominios de dir.ar

## Por qué existe este documento

Se sumaron 13 dominios de la red `dir.ar` (logística, limpieza,
administración de consorcios, catering, gimnasios, tiendas de ropa, salud y
belleza, seguridad del hogar, talleres mecánicos, gráficas e imprentas,
abogados, transporte) como `site:` en las queries automáticas
(`app/keywords.py::plantillas_query`). Varios de esos slugs (ej.
`tiendasderopa.dir.ar`, `saludybelleza.dir.ar`) se adivinaron por patrón, sin
poder verificar contra el sitio real porque WebFetch a `dir.ar` está
bloqueado en el entorno de desarrollo (aunque WebSearch sí funciona). Puede
haber slugs equivocados que nunca traen resultados, gastando presupuesto de
Serper sin avanzar.

## El prompt (para correr en cada auditoría — cada varias tandas, no cada una)

Copiá y pegá esto en una sesión de Claude Code cuando quieras auditar:

```
Auditá los dominios de la red dir.ar que usa el Motor de Jackpots. Pasos:

1. Corré: python3 main.py auditar-directorios
2. Para cada dominio marcado "⚠ SOSPECHOSO" (5+ intentos, 0 resultados en
   total): usá WebSearch con la query site:<dominio> para confirmar si el
   subdominio existe de verdad.
   - Si NO existe: buscá cuál es el slug correcto para ese rubro dentro de
     la red dir.ar (WebSearch "dir.ar <rubro> directorio") y corregilo en
     app/keywords.py::plantillas_query().
   - Si SÍ existe pero no trae resultados con las keywords actuales: no es
     un bug de slug, puede ser que las keywords no calcen con ese rubro —
     revisar si tiene sentido seguir intentando ese dominio para esa
     keyword específica.
3. Para los dominios con intentos=0 todavía: es normal, esperar a que el
   ciclo automático los pruebe (pueden tardar varias corridas en llegar,
   según la prioridad de keywords).
4. Si corregís un slug, agregá un test de regresión en
   tests/test_modulos_nuevos.py (mismo patrón que los tests existentes de
   plantillas_query) y corré la suite completa antes de commitear.
```

## Qué NO hace este audit

No verifica que el contenido de la página sea relevante (eso lo hacen los
filtros de `discovery.py`/`exclusions.py` cuando el resultado llega). Solo
detecta "este dominio nunca trae nada" — que casi siempre significa slug
equivocado, no basura de contenido.

## Dónde vive el código

- `app/auditoria_directorios.py::reporte_dominios()` — junta intentos/
  resultados/nuevas por dominio desde `queries_log`.
- `main.py auditar-directorios` — comando que imprime el reporte formateado.
