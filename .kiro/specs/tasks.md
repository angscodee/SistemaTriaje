# Tasks - SistemaTriaje (SOC-Lite)

## Estado general
- [ ] Proyecto completado

## 1. Infraestructura base y configuración

### 1.1 Configuración de repositorio
- [ ] Crear `.gitignore` completo
- [ ] Crear `LICENSE` (MIT)
- [ ] Crear `.env.example` documentado
- [ ] Crear `Makefile` con comandos: up, down, seed, test, lint, simulate
- [ ] Configurar pre-commit hooks (`.pre-commit-config.yaml`)

### 1.2 Docker Compose
- [ ] Crear `docker-compose.yml` con servicios: postgres, redis, backend, ai-service, frontend, n8n
- [ ] Crear `docker-compose.dev.yml` con perfiles: ollama, mock-ticketing
- [ ] Configurar health checks para todos los servicios
- [ ] Configurar red `soc-network` y volúmenes persistentes

### 1.3 Base de datos
- [ ] Crear script `db/init.sql` (schema SQL básico si no se usa Alembic primero)
- [ ] Crear `db/triggers.sql` con triggers de inmutabilidad de audit_log
- [ ] Crear `db/seed.sql` (o Python) con 4 usuarios (uno por rol) y 300+ alertas sintéticas

## 2. Backend - Auth y RBAC

### 2.1 Estructura base
- [ ] Crear `backend/Dockerfile` (multi-stage con Python 3.12)
- [ ] Crear `backend/requirements.txt` con dependencias pinned
- [ ] Crear `backend/pyproject.toml` (ruff, black, mypy, pytest config)
- [ ] Crear estructura de carpetas: app/{models,schemas,routers,services,repositories,core,middleware,utils}

### 2.2 Configuración y database
- [ ] Crear `app/config.py` (Pydantic Settings para .env)
- [ ] Crear `app/database.py` (SQLAlchemy async engine + session factory)
- [ ] Crear `app/main.py` (FastAPI app, CORS, middlewares, routers)

### 2.3 Modelos de base de datos
- [ ] Crear `app/models/user.py` (User)
- [ ] Crear `app/models/role.py` (Role, Permission, UserRole, RolePermission)
- [ ] Crear `app/models/alert.py` (Alert)
- [ ] Crear `app/models/enrichment.py` (EnrichmentData)
- [ ] Crear `app/models/triage.py` (TriageResult)
- [ ] Crear `app/models/incident.py` (Incident)
- [ ] Crear `app/models/audit_log.py` (AuditLog con prev_hash y hash)
- [ ] Crear tabla `refresh_tokens`

### 2.4 Alembic (migraciones)
- [ ] Configurar `alembic.ini` y `alembic/env.py`
- [ ] Crear migración inicial con todos los modelos
- [ ] Crear migración para triggers de audit_log (ejecutar SQL de db/triggers.sql)
- [ ] Verificar que triggers funcionan (test de UPDATE/DELETE rechazado)

### 2.5 Core de seguridad
- [ ] Crear `app/core/security.py` (hash password con Argon2id, create/verify JWT, blacklist Redis)
- [ ] Crear `app/core/exceptions.py` (excepciones personalizadas: UnauthorizedException, ForbiddenException, etc.)
- [ ] Crear `app/core/logging.py` (logger estructurado JSON con request_id)

### 2.6 Middlewares
- [ ] Crear `app/middleware/request_id.py` (genera UUID si no existe)
- [ ] Crear `app/middleware/audit.py` (registra request/response en audit_log)
- [ ] Crear `app/middleware/rate_limit.py` (Redis counter por IP+endpoint)
- [ ] Crear `app/middleware/security_headers.py` (X-Content-Type-Options, X-Frame-Options, HSTS, CSP)

### 2.7 Dependencies
- [ ] Crear `app/dependencies.py`:
  - `get_db()`: session de DB
  - `get_current_user()`: extrae y valida JWT, verifica blacklist
  - `require_permission(permission: str)`: verifica que user tiene el permiso

### 2.8 Schemas de auth
- [ ] Crear `app/schemas/auth.py` (LoginRequest, LoginResponse, RefreshResponse, UserResponse)
- [ ] Crear `app/schemas/user.py` (UserCreate, UserUpdate, UserOut, UserWithRoles)

### 2.9 Repositories de auth
- [ ] Crear `app/repositories/user_repository.py` (CRUD de usuarios, get_by_email, asignar roles)

### 2.10 Services de auth
- [ ] Crear `app/services/auth_service.py` (login, refresh, logout, verificar contraseña, crear tokens)
- [ ] Crear `app/services/user_service.py` (CRUD, validar política de contraseñas, bloqueo por intentos fallidos)

### 2.11 Routers de auth
- [ ] Crear `app/routers/auth.py` (POST /login, /refresh, /logout, GET /me)
- [ ] Crear `app/routers/users.py` (CRUD con require_permission("users:manage"))

### 2.12 Seed de usuarios y roles
- [ ] Crear `scripts/seed.py`:
  - Crear 4 roles (Administrador, Analista, Gestor, Auditor)
  - Crear permisos granulares (alerts:read, alerts:write, etc.)
  - Mapear permisos a roles
  - Crear 4 usuarios (admin@example.com, analista@example.com, gestor@example.com, auditor@example.com) con password "Demo1234!"

### 2.13 Tests de auth y RBAC
- [ ] Crear `backend/tests/conftest.py` (fixtures: test_db, test_client, auth headers por rol)
- [ ] Crear `backend/tests/unit/services/test_auth_service.py` (hash, verify, tokens)
- [ ] Crear `backend/tests/integration/routers/test_auth_router.py` (login, refresh, logout, 401/403)
- [ ] Crear `backend/tests/integration/routers/test_users_router.py` (CRUD con permisos)
- [ ] Verificar que Gestor recibe 403 en POST /users
- [ ] Verificar que Auditor recibe 403 en GET /alerts

## 3. Backend - Auditoría

### 3.1 Modelo y schema
- [ ] Verificar que `audit_log` tiene columnas: prev_hash, hash
- [ ] Crear `app/schemas/audit.py` (AuditLogOut, AuditLogFilter, ChainVerification)

### 3.2 Repository y service
- [ ] Crear `app/repositories/audit_repository.py` (insert_log, get_logs con filtros, get_last_hash, verify_chain)
- [ ] Crear `app/services/audit_service.py` (calcular hash, verificar integridad de cadena)

### 3.3 Router
- [ ] Crear `app/routers/audit.py`:
  - GET /audit (filtros, paginación) - require_permission("audit:read")
  - GET /audit/verify-chain - require_permission("audit:read")
  - POST /audit/external (API key de servicio para n8n)

### 3.4 Tests
- [ ] Crear `backend/tests/integration/routers/test_audit_router.py`:
  - Verificar que UPDATE audit_log lanza excepción
  - Verificar que DELETE audit_log lanza excepción
  - Verificar que verify-chain detecta manipulación manual de hash
  - Verificar que eventos críticos (login, cambio de rol, cambio de estado de alerta) se registran

## 4. Backend - Alertas y Triaje

### 4.1 Schemas
- [ ] Crear `app/schemas/alert.py` (AlertOut, AlertDetail, AlertFilter, AlertUpdate, AlertIngest)
- [ ] Crear `app/schemas/triage.py` (TriageResultOut, TriageRetry)

### 4.2 Repositories
- [ ] Crear `app/repositories/alert_repository.py` (get_alerts con filtros, get_alert_by_id con enrichment+triage, update_alert, insert_alert)
- [ ] Crear `app/repositories/triage_repository.py` (get_triage, insert_triage)

### 4.3 Services
- [ ] Crear `app/services/alert_service.py` (normalizar alerta, calcular fingerprint, verificar duplicado, filtros complejos)
- [ ] Crear `app/services/triage_service.py` (get triage, retry triage: llamar a ai-service)

### 4.4 Routers
- [ ] Crear `app/routers/alerts.py`:
  - GET /alerts (filtros: severity, status, source, date_from, date_to, src_ip, dst_ip, search, paginación)
  - GET /alerts/{id} (detalle con enrichment + triage)
  - PATCH /alerts/{id} (actualizar status/severity con justificación)
  - POST /alerts/ingest (uso interno, API key de servicio)
- [ ] Crear `app/routers/triage.py`:
  - GET /triage/{alert_id}
  - POST /triage/{alert_id}/retry

### 4.5 Tests
- [ ] Crear `backend/tests/unit/services/test_alert_service.py` (calcular fingerprint, detectar duplicados)
- [ ] Crear `backend/tests/integration/routers/test_alerts_router.py`:
  - GET /alerts con filtros
  - GET /alerts/{id} con datos completos
  - PATCH /alerts/{id} registra cambio en audit_log
  - Verificar que Gestor no puede PATCH (403)

## 5. Backend - Incidentes, Métricas y Reportes

### 5.1 Incidentes
- [ ] Crear `app/schemas/incident.py` (IncidentCreate, IncidentUpdate, IncidentOut)
- [ ] Crear `app/repositories/incident_repository.py` (CRUD, filtros)
- [ ] Crear `app/services/incident_service.py` (crear desde alerta, actualizar estado, comentarios)
- [ ] Crear `app/routers/incidents.py` (CRUD con require_permission)
- [ ] Tests básicos de CRUD

### 5.2 Métricas
- [ ] Crear `app/schemas/metrics.py` (SummaryMetrics, TimeSeriesData, TopSource, TopRule)
- [ ] Crear `app/services/metrics_service.py`:
  - get_summary: KPIs (total alertas, críticas abiertas, MTTT, % FP)
  - get_time_series: alertas por severity por día (últimos 7-30 días)
  - get_top_sources: top 10 IPs origen
  - get_top_rules: top 10 reglas
  - get_noise_reduction: % alertas descartadas
- [ ] Crear `app/routers/metrics.py` (todos los endpoints con require_permission("alerts:read"))
- [ ] Tests de cálculo de MTTT y % FP

### 5.3 Reportes
- [ ] Crear `app/utils/pdf_generator.py` (WeasyPrint: generar reporte ejecutivo en PDF)
- [ ] Crear `app/utils/docx_generator.py` (python-docx: reporte en Word)
- [ ] Crear `app/utils/excel_generator.py` (openpyxl: reporte en Excel)
- [ ] Crear `app/services/report_service.py`:
  - generate_executive_summary (KPIs + gráficos + recomendaciones)
  - generate_alert_details (tabla de alertas con triaje)
  - generate_metrics_report (MTTT/FP time series)
- [ ] Crear `app/routers/reports.py`:
  - GET /reports/executive-summary?format=pdf|docx|xlsx
  - GET /reports/alert-details?format=...
  - GET /reports/metrics-report?format=...
  - Registrar generación en audit_log
- [ ] Tests de generación de reportes (verificar que archivos se crean)

### 5.4 Health checks
- [ ] Crear endpoints:
  - GET /health (simple 200 OK)
  - GET /ready (verificar conexión a Postgres y Redis)

## 6. AI Service - Microservicio LangChain

### 6.1 Estructura base
- [ ] Crear `ai-service/Dockerfile`
- [ ] Crear `ai-service/requirements.txt` (langchain, ollama, openai, httpx, redis, pydantic, fastapi, sqlalchemy)
- [ ] Crear `ai-service/pyproject.toml`
- [ ] Crear estructura: app/{tools,prompts}

### 6.2 Configuración
- [ ] Crear `ai-service/app/config.py` (LLM_PROVIDER, OLLAMA_BASE_URL, OPENAI_API_KEY, API keys de proveedores)
- [ ] Crear `ai-service/app/schemas.py` (TriageRequest, TriageResponse con Pydantic v2)

### 6.3 LLM factory
- [ ] Crear `ai-service/app/llm.py`:
  - Factory que retorna Ollama ChatModel o OpenAI ChatModel según LLM_PROVIDER
  - Log de advertencia si usa OpenAI (datos se exfiltran)

### 6.4 Cache
- [ ] Crear `ai-service/app/cache.py` (wrapper de Redis con TTL configurable por proveedor)

### 6.5 Herramientas personalizadas
- [ ] Crear `ai-service/app/tools/virustotal.py` (@tool, cache Redis, timeout 10s, mock si no API key)
- [ ] Crear `ai-service/app/tools/abuseipdb.py` (@tool, cache Redis, timeout 5s, mock si no API key)
- [ ] Crear `ai-service/app/tools/geoip.py` (@tool, MaxMind GeoLite2 o ip-api, cache Redis, timeout 3s)
- [ ] Crear `ai-service/app/tools/historical_incidents.py` (@tool, query a Postgres por indicadores similares)
- [ ] Crear `ai-service/app/tools/asset_context.py` (@tool, leer de tabla o JSON, cache Redis)

### 6.6 Fallback determinístico
- [ ] Crear `ai-service/app/fallback.py` (mapeo rule_level → severity, reglas conocidas de FP)

### 6.7 Agente LangChain
- [ ] Crear `ai-service/app/prompts/analyst_v1.txt` (system prompt de analista SOC)
- [ ] Crear `ai-service/app/agent.py`:
  - Cargar prompt
  - Inicializar agente con herramientas
  - Ejecutar agente con timeout 30s
  - Validar output JSON contra TriageResponse schema
  - Si falla: aplicar fallback
  - Sanitizar datos si SANITIZE_EXTERNAL_DATA=true

### 6.8 FastAPI app
- [ ] Crear `ai-service/app/main.py`:
  - POST /triage (recibe TriageRequest, retorna TriageResponse)
  - GET /health
  - GET /ready

### 6.9 Tests
- [ ] Crear `ai-service/tests/conftest.py` (mocks de herramientas, fake LLM)
- [ ] Crear `ai-service/tests/test_tools.py` (cada herramienta con mock de APIs externas)
- [ ] Crear `ai-service/tests/test_agent.py` (agente con LLM fake, verificar output Pydantic)
- [ ] Crear `ai-service/tests/test_fallback.py` (verificar mapeo de reglas)

## 7. n8n Workflow

### 7.1 Diseño del workflow
- [ ] Crear workflow en n8n UI con 10 nodos según diseño
- [ ] Nodo 1: Webhook con validación de X-Webhook-Token
- [ ] Nodo 2: IF con condiciones (fingerprint no duplicado, severity >= media)
- [ ] Nodo 3: Postgres INSERT en alerts
- [ ] Nodo 4: HTTP Request a ai-service POST /triage
- [ ] Nodo 6: Switch por severity
- [ ] Nodo 7: Postgres INSERT en triage_results + UPDATE alerts
- [ ] Nodo 8: Slack/Telegram (condicional, dry-run si no credenciales)
- [ ] Nodo 9: HTTP Request a ticketing (osTicket/Redmine o mock)
- [ ] Nodo 10: HTTP Request a backend POST /api/audit/external
- [ ] Error Trigger: captura errores, registra en audit_log, marca alerta en_triaje

### 7.2 Exportar y documentar
- [ ] Exportar workflow a `n8n/workflows/soc-lite-triage.json`
- [ ] Crear `n8n/credentials.example.md` con instrucciones de configuración de credenciales (Postgres, Slack, Telegram, osTicket, Redmine)

### 7.3 Mock de ticketing para dev
- [ ] Configurar mockserver en docker-compose.dev.yml con expectativas para osTicket/Redmine API

## 8. Frontend - React

### 8.1 Estructura base
- [ ] Crear `frontend/Dockerfile` (multi-stage: build con node, serve con nginx)
- [ ] Crear `frontend/nginx.conf` (SPA routing, security headers)
- [ ] Crear `frontend/package.json` (React 18, TypeScript, Vite, TailwindCSS, Recharts, React Query, React Router)
- [ ] Crear `frontend/tsconfig.json` (strict: true)
- [ ] Crear `frontend/vite.config.ts` (alias @/ para src/)
- [ ] Crear `frontend/tailwind.config.js` (tema oscuro por defecto, colores personalizados)
- [ ] Crear `frontend/.eslintrc.json` y `.prettierrc`

### 8.2 API Client
- [ ] Crear `src/api/client.ts` (axios con interceptores para access_token y refresh)
- [ ] Crear `src/api/types.ts` (tipos de API: Alert, Triage, User, Incident, Metrics)

### 8.3 Contextos y hooks
- [ ] Crear `src/contexts/AuthContext.tsx` (user, login, logout, hasPermission)
- [ ] Crear `src/hooks/useAuth.ts` (consume AuthContext)
- [ ] Crear `src/hooks/usePermissions.ts` (verifica permisos para renderizado condicional)

### 8.4 Componentes comunes
- [ ] Crear `src/components/common/Button.tsx`
- [ ] Crear `src/components/common/Modal.tsx`
- [ ] Crear `src/components/common/Loader.tsx`
- [ ] Crear `src/components/common/Toast.tsx` (notificaciones)

### 8.5 Layout
- [ ] Crear `src/components/layout/Layout.tsx` (contenedor con sidebar + header)
- [ ] Crear `src/components/layout/Sidebar.tsx` (navegación, ocultar items según permisos)
- [ ] Crear `src/components/layout/Header.tsx` (usuario actual, botón de logout, toggle theme)

### 8.6 Componentes de autenticación
- [ ] Crear `src/components/auth/LoginForm.tsx` (formulario de login)

### 8.7 Páginas
- [ ] Crear `src/pages/Login.tsx`
- [ ] Crear `src/pages/Dashboard.tsx` (KPIs + gráficos con Recharts)
- [ ] Crear `src/pages/Alerts.tsx` (tabla con filtros y paginación)
- [ ] Crear `src/pages/AlertDetail.tsx` (detalle completo con tabs: info, enrichment, triaje, timeline)
- [ ] Crear `src/pages/Incidents.tsx` (lista de incidentes)
- [ ] Crear `src/pages/Reports.tsx` (selector de tipo y formato, botón de descarga)
- [ ] Crear `src/pages/AuditLog.tsx` (tabla de audit_log con filtros, botón verify-chain)
- [ ] Crear `src/pages/Admin.tsx` (gestión de usuarios y roles)

### 8.8 Componentes específicos
- [ ] Crear `src/components/alerts/AlertTable.tsx` (tabla con paginación)
- [ ] Crear `src/components/alerts/AlertDetail.tsx` (vista detallada)
- [ ] Crear `src/components/alerts/SeverityBadge.tsx` (badge con color según severity)
- [ ] Crear `src/components/dashboard/KPICard.tsx` (tarjeta de métrica)
- [ ] Crear `src/components/dashboard/Charts.tsx` (gráficos con Recharts)

### 8.9 Rutas
- [ ] Crear `src/routes/ProtectedRoute.tsx` (verifica autenticación y permisos)
- [ ] Crear `src/routes/routes.tsx` (definición de rutas con protección)

### 8.10 App principal
- [ ] Crear `src/App.tsx` (Router + AuthContext provider + React Query provider)
- [ ] Crear `src/main.tsx` (punto de entrada)
- [ ] Crear `src/styles/globals.css` (Tailwind imports + estilos globales)

### 8.11 Tests
- [ ] Crear `frontend/tests/unit/` con tests de componentes críticos (AlertTable, SeverityBadge)
- [ ] Crear `frontend/tests/e2e/` con Playwright: login → dashboard → alerts → alert detail

## 9. Scripts y utilidades

### 9.1 Seed
- [ ] Completar `scripts/seed.py`:
  - Crear 300+ alertas sintéticas con distribución 80% baja/FP, 15% media, 5% alta
  - Variedad de fuentes (Wazuh, OPNsense), reglas (SSH brute force, malware, port scan)
  - IPs realistas (algunas públicas, algunas internas)
  - Timestamps distribuidos en últimos 30 días

### 9.2 Simulación de alertas
- [ ] Crear `scripts/simulate_alerts.py`:
  - Generar ráfagas de alertas de ejemplo (Wazuh y OPNsense JSON)
  - Enviar a webhook de n8n con X-Webhook-Token
  - Casos: alerta crítica (malware hash conocido), alerta media (SSH brute force), alerta baja (failed login), duplicado

### 9.3 Healthcheck
- [ ] Crear `scripts/healthcheck.sh`:
  - Verificar que todos los servicios responden (curl a /health o /ready)
  - Exit code 0 si todos OK, 1 si alguno falla

### 9.4 Makefile
- [ ] Completar Makefile:
  - `make up`: docker compose up -d
  - `make down`: docker compose down
  - `make seed`: ejecutar seed en container de backend
  - `make migrate`: ejecutar alembic upgrade head
  - `make test`: ejecutar pytest en backend y ai-service, vitest en frontend
  - `make lint`: ruff, black, eslint, prettier
  - `make simulate`: ejecutar simulate_alerts.py

## 10. Documentación

### 10.1 Documentos técnicos
- [ ] Crear `docs/ARQUITECTURA.md` (diagrama Mermaid, descripción de componentes, flujo de datos)
- [ ] Crear `docs/API.md` (documentación de endpoints en español, ejemplos de request/response)
- [ ] Crear `docs/DECISIONES.md` (ADR de las decisiones de diseño)
- [ ] Crear `docs/RBAC.md` (matriz de permisos por rol)
- [ ] Crear `docs/SEGURIDAD.md` (OWASP, NIST CSF, ISO 27001 mapping, políticas de seguridad)

### 10.2 Manual de usuario
- [ ] Crear `docs/MANUAL_USUARIO.md`:
  - Guía de uso para cada rol (Administrador, Analista, Gestor, Auditor)
  - Screenshots de dashboard, alertas, reportes
  - Flujos comunes: triaje manual, escalación a incidente, generación de reporte

### 10.3 README
- [ ] Crear `README.md` (español):
  - Descripción del problema y solución
  - Diagrama de arquitectura (Mermaid)
  - Requisitos (Docker, Docker Compose, git)
  - Instalación en 5 pasos
  - Uso (credenciales de demo, cómo simular alertas)
  - Tabla de roles y permisos
  - Flujo n8n (descripción de nodos)
  - Variables de entorno
  - Capturas de pantalla (dashboard, alertas, detalle)
  - Roadmap (v2: respuesta automática, más fuentes, ML)
  - Licencia (MIT)

### 10.4 Samples
- [ ] Crear `samples/wazuh_alert_example.json` (alerta de ejemplo de Wazuh)
- [ ] Crear `samples/opnsense_alert_example.json` (alerta de ejemplo de OPNsense)
- [ ] Crear `samples/README.md` (descripción de alertas de ejemplo)

## 11. CI/CD

### 11.1 GitHub Actions
- [ ] Crear `.github/workflows/ci.yml`:
  - Job 1 (backend): ruff, black, mypy, pytest con coverage
  - Job 2 (ai-service): ruff, black, mypy, pytest con coverage
  - Job 3 (frontend): eslint, prettier, tsc, vitest
  - Job 4 (security): pip-audit, npm audit
  - Job 5 (build): docker build de backend, ai-service, frontend
  - Trigger: push a main, pull requests

## 12. Verificación y entrega

### 12.1 Tests de integración end-to-end
- [ ] Verificar que `docker compose up` levanta todos los servicios sin errores
- [ ] Verificar que `make migrate` ejecuta migraciones correctamente
- [ ] Verificar que `make seed` crea usuarios y alertas
- [ ] Verificar que `make simulate` envía alertas al webhook de n8n
- [ ] Verificar que alertas atraviesan los 10 nodos del flujo n8n
- [ ] Verificar que alertas aparecen en el dashboard con triaje y enriquecimiento
- [ ] Verificar que alertas de severidad alta disparan notificación (dry-run o real)
- [ ] Verificar que alertas de severidad alta crean ticket (mock o real)
- [ ] Verificar que duplicados y alertas de severidad < media son filtrados

### 12.2 Tests de seguridad y RBAC
- [ ] Verificar que cada rol solo accede a lo permitido (Gestor: solo dashboards/reportes; Auditor: solo bitácora)
- [ ] Verificar que intentos de UPDATE/DELETE en audit_log son rechazados (test automático)
- [ ] Verificar que GET /audit/verify-chain detecta manipulación si se modifica manualmente un hash
- [ ] Verificar que eventos críticos (login, cambio de rol, cambio de estado de alerta) se registran en audit_log

### 12.3 Tests de reportes y fallback
- [ ] Verificar que reportes PDF, Word y Excel se generan y descargan correctamente
- [ ] Verificar que si el LLM falla (simular timeout), el fallback por reglas produce un triaje válido con llm_model="fallback_rules"

### 12.4 Cobertura de tests
- [ ] Verificar que cobertura de tests en backend servicios críticos ≥ 80%
- [ ] Verificar que cobertura de tests en ai-service ≥ 80%
- [ ] Verificar que tests de frontend componentes críticos pasan

### 12.5 CI y calidad de código
- [ ] Verificar que CI (GitHub Actions) ejecuta lint, type-check, tests y build exitosamente
- [ ] Verificar que no hay errores de mypy en backend/ai-service
- [ ] Verificar que no hay errores de tsc en frontend

### 12.6 Documentación completa
- [ ] Verificar que README está completo en español con:
  - Descripción del problema
  - Arquitectura (diagrama Mermaid)
  - Requisitos
  - Instalación en 5 pasos
  - Uso (credenciales de demo: admin@example.com / Demo1234!)
  - Tabla de roles y permisos
  - Flujo n8n
  - Variables de entorno
  - Roadmap
  - Licencia (MIT)
- [ ] Verificar que todos los documentos en docs/ están completos

### 12.7 Publicación en GitHub
- [ ] Inicializar repositorio git: `git init`
- [ ] Crear `.gitignore` si aún no existe
- [ ] Primer commit: `git add . && git commit -m "feat: proyecto inicial SistemaTriaje (SOC-Lite)"`
- [ ] Configurar remote: `git remote add origin https://github.com/angscodee/SistemaTriaje.git`
- [ ] Push inicial: `git branch -M main && git push -u origin main`
- [ ] Commits incrementales tras cada hito mayor (infra, backend, ai-service, n8n, frontend, docs)

### 12.8 Entrega final
- [ ] Verificar con `git status` que no hay cambios sin commit
- [ ] Verificar con `git log --oneline` que todos los commits están presentes
- [ ] Generar resumen final:
  - Qué se construyó (componentes principales)
  - Cómo levantarlo (5 pasos desde README)
  - Credenciales de demo
  - Limitaciones conocidas (p. ej. LLM local requiere GPU para mejor performance)
  - Próximos pasos (roadmap v2)

---

## Orden de ejecución sugerido

1. Infraestructura base (1.1-1.3): gitignore, docker-compose, db/triggers.sql
2. Backend - Auth y RBAC (2.1-2.13): estructura, modelos, alembic, auth, tests
3. Backend - Auditoría (3.1-3.4): audit_log, triggers, verify-chain, tests
4. Backend - Alertas y Triaje (4.1-4.5): modelos, schemas, routers, tests
5. Backend - Incidentes, Métricas, Reportes (5.1-5.4): CRUD, métricas, PDF/Word/Excel
6. AI Service (6.1-6.9): herramientas, agente, fallback, tests
7. n8n Workflow (7.1-7.3): diseño, exportar, mock ticketing
8. Frontend (8.1-8.11): estructura, auth, dashboard, alertas, reportes, tests
9. Scripts (9.1-9.4): seed, simulate, healthcheck, Makefile
10. Documentación (10.1-10.4): ARQUITECTURA, API, RBAC, SEGURIDAD, MANUAL_USUARIO, README, samples
11. CI/CD (11.1): GitHub Actions
12. Verificación y entrega (12.1-12.8): tests e2e, RBAC, reportes, publicación en GitHub

**Nota**: Cada sección puede tener commits incrementales. No esperar a terminar todo para hacer el primer push.
