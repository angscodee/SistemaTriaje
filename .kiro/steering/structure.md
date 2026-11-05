# Structure Steering - SistemaTriaje

## Estructura de repositorio (monorepo)

```
SistemaTriaje/
├── README.md                          # Documentación principal en español
├── LICENSE                            # MIT
├── .env.example                       # Variables de entorno documentadas
├── .gitignore                         # Excluye secretos, node_modules, __pycache__, etc.
├── docker-compose.yml                 # Stack completo para producción
├── docker-compose.dev.yml             # Perfiles de desarrollo (mock-ticketing, ollama)
├── Makefile                           # Comandos: up, down, seed, test, lint, simulate
├── .github/
│   └── workflows/
│       └── ci.yml                     # Lint, type-check, tests, build, audit
├── .kiro/
│   ├── specs/                         # Requirements, design, tasks
│   └── steering/                      # Product, tech, structure, security
├── docs/
│   ├── ARQUITECTURA.md                # Diagrama Mermaid, flujo de datos
│   ├── API.md                         # Documentación de endpoints (español)
│   ├── DECISIONES.md                  # ADR (Architecture Decision Records)
│   ├── RBAC.md                        # Matriz de permisos por rol
│   ├── SEGURIDAD.md                   # OWASP, NIST CSF, ISO 27001 mapping
│   └── MANUAL_USUARIO.md              # Guía de uso para cada rol
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt               # Pinned versions
│   ├── pyproject.toml                 # Ruff, black, mypy config
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── versions/                  # Migraciones
│   │   └── env.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app, CORS, middleware
│   │   ├── config.py                  # Pydantic Settings
│   │   ├── database.py                # SQLAlchemy async engine/session
│   │   ├── dependencies.py            # Inyección de dependencias
│   │   ├── middleware/
│   │   │   ├── audit.py               # Audit logging middleware
│   │   │   ├── rate_limit.py
│   │   │   └── security_headers.py
│   │   ├── models/                    # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   ├── alert.py
│   │   │   ├── enrichment.py
│   │   │   ├── triage.py
│   │   │   ├── incident.py
│   │   │   └── audit_log.py
│   │   ├── schemas/                   # Pydantic schemas (request/response)
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── alert.py
│   │   │   ├── triage.py
│   │   │   ├── incident.py
│   │   │   └── metrics.py
│   │   ├── routers/                   # Endpoints por dominio
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── alerts.py
│   │   │   ├── triage.py
│   │   │   ├── incidents.py
│   │   │   ├── metrics.py
│   │   │   ├── reports.py
│   │   │   └── audit.py
│   │   ├── services/                  # Lógica de negocio
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── alert_service.py
│   │   │   ├── triage_service.py
│   │   │   ├── incident_service.py
│   │   │   ├── metrics_service.py
│   │   │   ├── report_service.py
│   │   │   └── audit_service.py
│   │   ├── repositories/              # Acceso a datos
│   │   │   ├── user_repository.py
│   │   │   ├── alert_repository.py
│   │   │   ├── triage_repository.py
│   │   │   ├── incident_repository.py
│   │   │   └── audit_repository.py
│   │   ├── core/
│   │   │   ├── security.py            # JWT, password hashing, RBAC
│   │   │   ├── exceptions.py          # Custom exceptions
│   │   │   └── logging.py             # Structured logging
│   │   └── utils/
│   │       ├── pdf_generator.py       # WeasyPrint
│   │       ├── docx_generator.py      # python-docx
│   │       └── excel_generator.py     # openpyxl
│   └── tests/
│       ├── conftest.py                # Fixtures, DB de prueba
│       ├── unit/
│       ├── integration/
│       └── e2e/
├── ai-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app
│   │   ├── config.py
│   │   ├── schemas.py                 # TriageRequest, TriageResponse
│   │   ├── agent.py                   # LangChain agent
│   │   ├── tools/                     # Custom tools
│   │   │   ├── virustotal.py
│   │   │   ├── abuseipdb.py
│   │   │   ├── geoip.py
│   │   │   ├── historical_incidents.py
│   │   │   └── asset_context.py
│   │   ├── prompts/                   # System prompts versionados
│   │   │   └── analyst_v1.txt
│   │   ├── llm.py                     # Factory para Ollama/OpenAI
│   │   ├── cache.py                   # Redis cache
│   │   └── fallback.py                # Rule-based fallback
│   └── tests/
│       ├── conftest.py
│       ├── test_agent.py
│       └── test_tools.py
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf                     # Producción
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── .eslintrc.json
│   ├── .prettierrc
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   ├── client.ts              # Axios/fetch wrapper
│   │   │   └── types.ts               # API types
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Layout.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   ├── auth/
│   │   │   │   └── LoginForm.tsx
│   │   │   ├── alerts/
│   │   │   │   ├── AlertTable.tsx
│   │   │   │   ├── AlertDetail.tsx
│   │   │   │   └── SeverityBadge.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── KPICard.tsx
│   │   │   │   └── Charts.tsx
│   │   │   └── common/
│   │   │       ├── Button.tsx
│   │   │       ├── Modal.tsx
│   │   │       └── Loader.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Alerts.tsx
│   │   │   ├── AlertDetail.tsx
│   │   │   ├── Incidents.tsx
│   │   │   ├── Reports.tsx
│   │   │   ├── AuditLog.tsx
│   │   │   └── Admin.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── usePermissions.ts
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx
│   │   ├── routes/
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── routes.tsx
│   │   ├── utils/
│   │   │   ├── format.ts
│   │   │   └── constants.ts
│   │   └── styles/
│   │       └── globals.css
│   └── tests/
│       ├── unit/
│       └── e2e/
├── n8n/
│   ├── workflows/
│   │   └── soc-lite-triage.json       # Workflow exportado
│   └── credentials.example.md          # Instrucciones de configuración
├── db/
│   ├── init.sql                        # Schema inicial (si no usa Alembic)
│   ├── triggers.sql                    # Triggers de auditoría
│   └── seed.sql                        # Datos de prueba (4 usuarios, 300+ alertas)
├── samples/
│   ├── wazuh_alert_example.json
│   ├── opnsense_alert_example.json
│   └── README.md                       # Descripción de ejemplos
└── scripts/
    ├── seed.py                         # Populate DB con datos de prueba
    ├── simulate_alerts.py              # Envía alertas al webhook de n8n
    └── healthcheck.sh                  # Verifica todos los servicios
```

## Principios organizacionales

### Separación de capas
- **Routers**: solo validación de entrada (Pydantic) y respuesta HTTP
- **Services**: lógica de negocio, orquestación entre repositorios
- **Repositories**: queries SQL, interacción con DB
- **Models**: definición de schema SQLAlchemy
- **Schemas**: contratos de API (request/response Pydantic)

### Inyección de dependencias
Usar FastAPI `Depends()` para:
- Sesiones de DB
- Servicios
- Usuario actual
- Verificación de permisos

### Configuración centralizada
- `config.py` con Pydantic Settings lee `.env`
- Validación en startup, no en runtime
- Defaults seguros (modo restrictivo)

### Nombres de archivos
- **Python**: snake_case.py
- **TypeScript/React**: PascalCase.tsx para componentes, camelCase.ts para utils
- **SQL**: snake_case.sql
- **Docs**: UPPERCASE.md para documentación principal, lowercase.md para técnica

### Imports
- **Python**: absolutos desde app/ (ej: `from app.models.user import User`)
- **TypeScript**: alias `@/` para src/ (ej: `import { Button } from '@/components/common'`)

## Testing

### Estructura de tests
Espejo de estructura de código:
```
backend/tests/
├── unit/services/       # Lógica de negocio aislada
├── integration/routers/ # Endpoints completos con DB
└── e2e/                 # Flujos completos
```

### Fixtures compartidos
- `conftest.py` en raíz de tests
- DB de prueba con datos conocidos
- Mocks de servicios externos (VirusTotal, LLM)

## Docker

### Naming de servicios
- `postgres`: base de datos
- `redis`: cache y colas
- `backend`: API FastAPI
- `ai-service`: microservicio LangChain
- `frontend`: nginx con build de React
- `n8n`: orquestador
- `ollama`: LLM local (perfil opcional)
- `mock-ticketing`: mock de osTicket (perfil dev)

### Volúmenes
- `postgres_data`: persistencia de DB
- `redis_data`: persistencia de cache
- `n8n_data`: workflows y configuración
- `ollama_models`: modelos descargados (no en .gitignore si se quiere persistir)

### Redes
- `soc-network`: red interna para comunicación entre servicios
- Exponer solo frontend (80/443), n8n (5678) y backend (8000) para desarrollo
