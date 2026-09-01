# Motor de Jackpots — B2B Labor Intelligence (curado, no masivo)

Herramienta de apoyo para búsqueda de empleo dirigida: identifica empresas serias
zona por zona, con revisión humana en cada paso, y genera los emails de postulación
espontánea a partir de los CVs reales de Marco. No busca, envía ni automatiza nada
sin aprobación explícita — es intencionalmente de bajo volumen (2-4 empresas por zona).

## Estructura
- `cvs/` — PDFs de los 4 CVs (`cv_limpieza.pdf`, `cv_administrativo.pdf`, `cv_atencion_cliente.pdf`, `cv_logistica.pdf`) + `.txt` extraídos.
- `engine/estado.py` — gestiona `progreso.json`: zonas auditadas, empresas jackpot/descartadas, evita duplicados.
- `engine/leer_cvs.py` — extrae texto de los PDFs a `.txt`.
- `engine/generar_email.py` — genera el `.md` final en `outreach/` para una empresa YA aprobada, usando un fragmento de experiencia copiado literal del CV (nunca inventado).
- `outreach/` — un `.md` por empresa con el email listo para copiar y enviar a mano.
- `progreso.json` / `progreso.md` — estado del proceso, para retomar entre sesiones.

## Flujo de trabajo
1. `python3 engine/leer_cvs.py` — una vez, para tener el texto de los CVs disponible.
2. Por cada zona (`python3 engine/estado.py siguiente-zona`):
   - Investigación manual/asistida de empresas candidatas (fuera de este motor, con revisión).
   - Para cada empresa que el usuario aprueba, registrarla:
     ```
     python3 engine/estado.py agregar-empresa --zona ... --nombre ... --rubro ... \
       --estado jackpot --motivo "..." --fuente "..." --contacto "..." --cv ...
     ```
   - Generar el email solo para las aprobadas:
     ```
     python3 engine/generar_email.py --empresa ... --rubro ... --zona ... \
       --motivo-seriedad ... --fuente ... --contacto ... --cv ... \
       --experiencia-file cvs/experiencia_<rubro>_snippet.txt
     ```
   - Marcar la zona como auditada: `python3 engine/estado.py marcar-zona "Nombre Zona"`
3. Revisar y enviar cada email de `outreach/` manualmente (o crear el borrador en Gmail a pedido, nunca en loop automático).

## Reglas duras
- Nunca se inventa ni asume contacto: solo lo verificado y citado.
- Nunca se rastrea contacto personal de individuos, solo email/teléfono a nivel empresa.
- Nunca se infla experiencia: el texto de experiencia en el email viene de un archivo que el usuario/Claude copia literal del CV.
- Empresa con señales de despidos/achique activo → se descarta y se documenta el motivo.
- Homónimos de otra provincia/país → se descartan y se aclara el motivo.
