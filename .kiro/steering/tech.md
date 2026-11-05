# Technical Steering - SistemaTriaje

## Stack tecnológico obligatorio

| Capa | Tecnología |
|------|------------|
| **Frontend** | React 18 + TypeScript + Vite + TailwindCSS + Recharts |
| **Backend API** | FastAPI (Python 3.12) + SQLAlchemy 2.x (async) + Pydantic v2 + Alembic |
| **Automatización** | n8n (Docker) |
| **IA** | Microservicio LangChain (FastAPI) con agente y herramientas personalizadas; LLM por Ollama local (llama3 / mistral) por defecto; OpenAI opcional vía variable de entorno |
| **Base de datos** | PostgreSQL 16 + Redis (rate-limiting, sesión/blacklist de tokens, colas) |
| **Autenticación** | JWT (access + refresh) + módulo RBAC propio |
| **Reportes** | WeasyPrint (PDF), python-docx (Word), openpyxl (Excel) |
| **Infra** | Docker Compose, GitHub Actions (CI) |
| **HTTP cliente** | httpx (async) |
| **Pruebas** | pytest + pytest-asyncio + httpx; Vitest + Testing Library; Playwright (e2e básico) |

## Convenciones de código

### Python (backend/ai-service)
- **Python 3.12+** requerido
- **Tipado estricto**: usar type hints en todas las funciones, validar con mypy
- **Async por defecto**: usar asyncio, async/await en operaciones I/O
- **Pydantic v2**: validación de entrada/salida, modelos con TypedDict cuando sea apropiado
- **Formato**: black (line-length 100) + ruff para linting
- **Imports**: orden automático con isort
- **Estructura**: capas separadas (routers → services → repositories)
- **Inyección de dependencias**: usar FastAPI Depends()
- **Logging**: logging estructurado JSON con request_id
- **Sin secretos**: usar variables de entorno, nunca hardcodear

### TypeScript (frontend)
- **TypeScript estricto**: `"strict": true` en tsconfig
- **React 18**: componentes funcionales + hooks
- **Naming**: PascalCase para componentes, camelCase para funciones/variables
- **Imports**: paths absolutos con alias (@/ para src/)
- **Estado**: React Query para servidor, useState/Context para local
- **Formato**: Prettier + ESLint
- **Estilos**: TailwindCSS utility-first, clases semánticas cuando se repiten

### SQL
- **Migraciones**: Alembic para cambios de esquema
- **Índices**: crear en columnas de búsqueda frecuente (status, severity, timestamps, IPs)
- **Constraints**: usar checks, foreign keys, unique donde corresponda
- **Triggers**: en db/triggers.sql para lógica de auditoría

### Docker
- **Multi-stage builds**: separar build de runtime
- **Non-root user**: ejecutar servicios con usuario no privilegiado
- **Health checks**: definir para todos los servicios
- **Secrets**: usar secrets de Docker Compose, no variables de entorno para producción

## Gestión de errores

### Backend
- Excepciones personalizadas por dominio (AlertNotFoundError, UnauthorizedError)
- Handler global que traduce a códigos HTTP + JSON estructurado
- Log de errores con contexto completo (traceback en desarrollo)

### Frontend
- Error boundaries para capturar errores de React
- Toasts/notificaciones para errores de usuario
- Logging a consola en desarrollo, servicio de telemetría en producción

## Testing

### Cobertura mínima
- **Backend servicios críticos**: ≥ 80%
- **AI service**: ≥ 80%
- **Frontend componentes críticos**: ≥ 70%

### Estrategia
- **Unit**: lógica de negocio aislada, mocks de DB/externos
- **Integration**: endpoints completos con DB de prueba
- **E2E**: flujos críticos (login → dashboard → detalle alerta)

### Fixtures
- Datos de prueba realistas en fixtures/seeds
- Factories para generar objetos de prueba (factory_boy, faker)

## Seguridad

- **Contraseñas**: Argon2 o bcrypt, política mínima (8 chars, 1 mayúscula, 1 número)
- **JWT**: access token (15 min), refresh token (7 días), blacklist en Redis
- **CORS**: orígenes permitidos explícitos, no wildcard en producción
- **Rate limiting**: Redis, límites por endpoint/usuario
- **Headers de seguridad**: HSTS, X-Frame-Options, CSP básico
- **Validación**: Pydantic para entrada, sanitizar antes de queries
- **SQL**: usar ORM/prepared statements, nunca concatenar strings
- **Principio de mínimo privilegio**: rol de DB sin DDL, sin UPDATE/DELETE en audit_log

## Privacidad y datos sensibles

- **LLM local por defecto**: Ollama (llama3/mistral) para no exfiltrar datos
- **OpenAI opcional**: solo con LLM_PROVIDER=openai, advertir al usuario
- **Enmascaramiento**: sanitizar usuarios/hostnames antes de enviar a APIs externas (opcional, configurable)
- **Logs**: no registrar payloads completos con datos sensibles, solo hashes/referencias

## Performance

- **Caching**: Redis para enriquecimiento (TTL configurable por proveedor)
- **Índices DB**: en todos los filtros comunes
- **Paginación**: obligatoria en listados (cursor o offset)
- **Lazy loading**: componentes pesados en frontend
- **Timeouts**: establecer en todas las llamadas externas (VirusTotal, AbuseIPDB, LLM)
- **Circuit breaker**: en ai-service para proveedores externos

## Observabilidad

- **Logs estructurados**: JSON con timestamp, level, request_id, user_id, mensaje
- **Métricas**: exponer /metrics (Prometheus-compatible opcional para v2)
- **Health checks**: /health (liveness), /ready (readiness con chequeo de DB/Redis)
- **Request ID**: generar en gateway/nginx, propagar en headers

## Variables de entorno

Prefijos por servicio:
- `DB_*`: PostgreSQL
- `REDIS_*`: Redis
- `JWT_*`: autenticación
- `LLM_*`: configuración de LangChain
- `VIRUSTOTAL_*`, `ABUSEIPDB_*`: proveedores de threat intel
- `SLACK_*`, `TELEGRAM_*`: notificaciones
- `TICKETING_*`: integración con ticketing

Siempre proveer `.env.example` completo y comentado.

## Git workflow

- **Branch principal**: `main`
- **Commits**: Conventional Commits en español (feat:, fix:, docs:, test:, chore:)
- **Pre-commit hooks**: ruff, black, prettier, type-check
- **.gitignore**: excluir .env, node_modules, __pycache__, .pytest_cache, dist/, build/, volúmenes Docker, modelos Ollama
