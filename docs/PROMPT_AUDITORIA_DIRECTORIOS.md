# Prompt de auditoría — subdominios de dir.ar

## Por qué existe este documento

`app/directorio_dir_ar.py` lee directo y gratis (sin pasar por Serper)
varios subdominios de la red `dir.ar` que siguen el patrón "listado por
ciudad" (`app/directorio_dir_ar.py::DOMINIOS`). Una investigación real
(sept. 2026, ver historial de commits) confirmó cuáles de esos subdominios
existen de verdad y corrigió varios que se habían adivinado por patrón sin
verificar (ej. `limpieza.dir.ar` no existe — es una subcarpeta del dominio
principal, `dir.ar/empresas-limpieza/`, con otra estructura de URL).

Sigue habiendo riesgo: los slugs de subdominio que quedaron en `DOMINIOS`
(catering, gimnasios, tiendasderopa, tallermecanico, graficas) están
confirmados como subdominios reales, pero su patrón interno de URL
(`/ciudad/{slug}.html`, calcado del de logística) NO se pudo verificar
contra el HTML real porque WebFetch a `dir.ar` está bloqueado en el
entorno de desarrollo (aunque WebSearch sí funciona). Puede haber alguno
que use otra estructura interna y por eso nunca traiga resultados.

## El prompt (para correr en cada auditoría — cada varias tandas, no cada una)

Copiá y pegá esto en una sesión de Claude Code cuando quieras auditar:

```
Auditá los dominios de la red dir.ar que lee app/directorio_dir_ar.py. Pasos:

1. Corré: python3 main.py auditar-directorios
2. Para cada dominio marcado "⚠ SOSPECHOSO" (5+ zonas probadas, 0 empresas
   nuevas en total): usá WebSearch con la query site:<dominio> para
   confirmar si el subdominio existe de verdad y qué estructura de URL usa.
   - Si NO existe: buscá cuál es el slug/dominio correcto para ese rubro
     (WebSearch "dir.ar <rubro> directorio") y corregilo en
     app/directorio_dir_ar.py::DOMINIOS.
   - Si existe pero con otra estructura de URL (no /ciudad/{slug}.html):
     no alcanza con cambiar el slug — hace falta ajustar
     buscar_por_zona_y_dominio() para ese dominio específico, o sacarlo de
     DOMINIOS hasta tener un parser dedicado (como se hizo con
     administraciondeconsorcios.dir.ar y abogados.dir.ar, que usan un
     esquema por ficha/localidad muy distinto).
3. Para los dominios con zonas_probadas=0 todavía: es normal, esperar a que
   el ciclo automático los pruebe (pueden tardar varias corridas en
   llegar, según combinaciones_pendientes()).
4. Si corregís un dominio o slug, agregá un test de regresión en
   tests/test_modulos_nuevos.py (mismo patrón que
   test_slug_de_zona_usa_guiones_entre_palabras) y corré la suite completa
   antes de commitear.
```

## Qué NO hace este audit

No verifica que el contenido de la página sea relevante (eso lo hacen los
filtros de `discovery.py`/`exclusions.py` cuando el resultado llega). Solo
detecta "este dominio nunca trae nada" — que casi siempre significa
dominio/slug equivocado o estructura de URL distinta, no basura de
contenido.

## Dónde vive el código

- `app/directorio_dir_ar.py::DOMINIOS` — la lista real de subdominios que
  el crawler lee, y `buscar_por_zona_y_dominio()` que arma la URL.
- `app/auditoria_directorios.py::reporte_dominios()` — junta zonas
  probadas/empresas nuevas por dominio desde `directorio_dir_ar_progress`.
- `main.py auditar-directorios` — comando que imprime el reporte formateado.
