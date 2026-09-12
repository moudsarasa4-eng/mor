# Electricista OS — Backend (FastAPI + SQLite)

Backend real para el dashboard de Marco. Implementa exactamente el contrato que
el dashboard espera, con datos persistidos, login por JWT y datos de ejemplo
sembrados en la primera corrida. Además **sirve el propio dashboard**, así que
con un solo comando tenés todo funcionando.

## Poner en marcha (una vez)

```bash
cd <raíz del repo>
python3 -m venv .venv-eos
source .venv-eos/bin/activate            # Windows: .venv-eos\Scripts\activate
pip install -r electricista_os/requirements.txt
```

## Correr

```bash
source .venv-eos/bin/activate
uvicorn electricista_os.main:app --reload
```

Abrí **http://127.0.0.1:8000** — carga el dashboard. Entrá en la pestaña
**Conexión** e iniciá sesión:

- Usuario: `marco`  ·  Contraseña: `electricista`  (cambialos con `EOS_USER` / `EOS_PASSWORD`)

La documentación interactiva de la API queda en **http://127.0.0.1:8000/docs**.

## Qué expone (contrato del dashboard)

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/auth/login` | Login (form `username`/`password`) → `{access_token, token_type}` |
| GET | `/empresa/configuracion` | Config de la empresa (margen, precio visita, garantía) |
| GET | `/prospectos` | Lista de prospectos (con diagnóstico y escenarios) |
| POST | `/prospectos/procesar` | Clasifica un texto de WhatsApp y crea el prospecto |
| POST | `/prospectos` | Alta manual (nombre/teléfono desde el intake) |
| GET | `/trabajos` | Trabajos con `insumos_usados` anidados |
| GET | `/gastos-operativos` | Gastos del mes |
| GET | `/insumos` | Stock de insumos |
| GET | `/agenda` | Visitas agendadas |
| POST | `/agenda` | Agendar visita (resuelve cliente/trabajo por id) |
| PATCH | `/agenda/{id}/estado` | Cambiar estado de una visita |
| GET | `/diagnostico/escenarios` | Escenarios para la pestaña Escenarios |
| POST | `/diagnostico/prompt` | Genera el prompt del escenario elegido |
| POST | `/trabajos/{id}/facturar` | Facturación (hoy **simulada**, CAE marcado) |

Todas las rutas de datos requieren el token (Bearer). Sin token o con token
vencido devuelven **401**, y el dashboard muestra el aviso de "sesión vencida".

## Seguridad

- Contraseñas hasheadas con PBKDF2 (stdlib), tokens JWT HS256 (stdlib) — sin
  dependencias de crypto externas.
- Seteá `EOS_SECRET_KEY` en producción para que los tokens sobrevivan reinicios.

## Pendiente (documentado, no bloquea)

- **Facturación fiscal real** (ARCA / TusFacturasAPP): hoy `POST /trabajos/{id}/facturar`
  devuelve un CAE simulado marcado como tal.
- **Ingreso automático de WhatsApp**: el intake es manual mejorado; la API oficial
  (WhatsApp Cloud) o un puente se agregan encima de `POST /prospectos/procesar`.
