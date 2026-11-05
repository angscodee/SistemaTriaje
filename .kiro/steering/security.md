# Security Steering - SistemaTriaje

## Principios de seguridad (OWASP ASVS nivel 1-2)

### 1. Autenticación y gestión de sesiones

#### Contraseñas
- **OBLIGATORIO**: Argon2id o bcrypt con factor de trabajo apropiado
- **Política mínima**:
  - Longitud ≥ 8 caracteres
  - Al menos 1 letra mayúscula
  - Al menos 1 número
  - Al menos 1 carácter especial (opcional pero recomendado)
- **Bloqueo temporal**: 5 intentos fallidos → bloqueo de 15 minutos por IP + cuenta
- **Nunca** almacenar contraseñas en texto plano, nunca en logs

#### JWT (JSON Web Tokens)
- **Access token**: 15 minutos de vida, solo en memoria del cliente
- **Refresh token**: 7 días de vida, HttpOnly cookie, almacenado en DB
- **Blacklist**: Redis para tokens revocados (logout, cambio de contraseña)
- **Firma**: HS256 o RS256 con clave rotada periódicamente
- **Claims mínimos**: user_id, role, exp, iat, jti (para blacklist)

#### RBAC (Role-Based Access Control)
- **INVARIANTE**: Todos los endpoints deben verificar permisos, nunca confiar en el frontend
- **Modelo**: Users → UserRoles → Roles → RolePermissions → Permissions
- **Permisos granulares**:
  - `alerts:read`, `alerts:write`, `alerts:delete`
  - `incidents:read`, `incidents:write`
  - `reports:read`, `reports:generate`
  - `audit:read`
  - `users:manage`, `roles:manage`, `config:manage`
- **Enforcement**: Decorator/dependency `@require_permission("alerts:write")`
- **Frontend**: Ocultar UI según permisos, pero backend SIEMPRE valida

### 2. Bitácora de auditoría (audit_log) inmutable

#### INVARIANTE CRÍTICO
La tabla `audit_log` **NO PUEDE** ser modificada ni eliminada una vez insertada. Esto es un requisito de cumplimiento (ISO 27001, SOC 2).

#### Implementación
1. **Middleware FastAPI** que registra TODA interacción:
   - Usuario (user_id, role)
   - Acción (método HTTP + path)
   - Recurso (ID del objeto afectado)
   - Resultado (status_code)
   - Contexto (IP, user-agent, timestamp UTC, request_id)
   - Detalles (JSONB con antes/después para cambios críticos)

2. **Triggers PostgreSQL** (en `db/triggers.sql`):
   ```sql
   -- Rechazar UPDATE/DELETE en audit_log
   CREATE OR REPLACE FUNCTION prevent_audit_modification()
   RETURNS TRIGGER AS $$
   BEGIN
     RAISE EXCEPTION 'audit_log es inmutable - operación no permitida';
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER prevent_update_audit
   BEFORE UPDATE ON audit_log
   FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();

   CREATE TRIGGER prevent_delete_audit
   BEFORE DELETE ON audit_log
   FOR EACH ROW EXECUTE FUNCTION prevent_audit_modification();
   ```

3. **Hash encadenado** (blockchain-style):
   - Columna `prev_hash`: hash del registro anterior
   - Columna `hash`: SHA-256(registro actual + prev_hash)
   - Endpoint `GET /audit/verify-chain` para detectar manipulación

4. **Permisos DB**:
   - Rol de aplicación: solo `INSERT` en audit_log
   - Revocar explícitamente `UPDATE`, `DELETE`, `TRUNCATE`

#### Eventos que DEBEN auditarse
- ✅ Login exitoso/fallido
- ✅ Logout
- ✅ Cambio de rol de usuario
- ✅ Cambio de severidad o estado de alerta
- ✅ Cambio de estado de incidente
- ✅ Generación de reportes
- ✅ Acceso denegado (403)
- ✅ Cambios en configuración
- ✅ Acciones de n8n (vía endpoint `/api/audit/external`)

### 3. Protección de datos

#### Datos sensibles
- **Contraseñas**: hash con Argon2id, nunca reversibles
- **Tokens**: en Redis con TTL, limpiar al expirar
- **API keys externas**: en variables de entorno, nunca en código
- **Payloads de alertas**: pueden contener IPs internas, usuarios, rutas de archivos

#### Enmascaramiento (opcional, configurable)
- Antes de enviar a VirusTotal/AbuseIPDB/OpenAI, opcionalmente reemplazar:
  - Usuarios: `user123` → `user_<hash>`
  - Hostnames internos: `server-prod-01` → `host_<hash>`
  - Rutas: `/home/admin/...` → `<path>`
- Variable: `SANITIZE_EXTERNAL_DATA=true|false`

#### LLM y privacidad
- **Por defecto**: Ollama local (llama3/mistral) → datos NO salen del servidor
- **OpenAI**: solo si `LLM_PROVIDER=openai` → **ADVERTIR** al usuario que datos se envían a terceros
- **Prompt injection**: tratar `raw_payload` de alertas como no confiable:
  - Delimitarlo claramente en el prompt
  - Validar salida JSON contra esquema Pydantic
  - Nunca ejecutar acciones derivadas directamente del LLM sin validación

### 4. Seguridad de red y API

#### CORS
- **Desarrollo**: `http://localhost:5173` (Vite dev server)
- **Producción**: dominio específico, NO wildcard `*`
- Configurar en FastAPI: `CORSMiddleware` con `allow_origins` explícito

#### Rate limiting
- **Redis** para contador de requests por:
  - IP + endpoint: 100 req/min para GET, 20 req/min para POST/PUT/DELETE
  - Usuario autenticado: límites más altos
- **429 Too Many Requests** con header `Retry-After`

#### Headers de seguridad
```python
# Middleware en FastAPI
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
response.headers["Content-Security-Policy"] = "default-src 'self'"
```

#### Webhooks (n8n ingesta)
- **Firma HMAC** o token secreto en header `X-Webhook-Token`
- Validar en nodo 1 del workflow n8n
- Límite de tamaño: 1 MB por payload
- Timeout: 30 segundos

### 5. Validación de entrada

#### Backend
- **Pydantic v2**: validar TODOS los request bodies/query params
- **Constraints**: max_length, regex patterns, enum values
- **Sanitización**: escapar caracteres especiales antes de queries
- **SQLAlchemy**: usar ORM o prepared statements, NUNCA concatenar SQL strings

#### Frontend
- **Client-side validation**: UX, no seguridad
- **Backend validation**: siempre repetir, nunca confiar en frontend

### 6. Gestión de dependencias

#### Actualizaciones
- **Pinned versions**: `requirements.txt` con versiones exactas
- **Escaneo**: `pip-audit`, `npm audit` en CI
- **Dependabot/Renovate**: PR automáticos de actualizaciones de seguridad

#### Proveedores externos
- **Timeouts**: 10s para VirusTotal, 5s para AbuseIPDB, 30s para LLM
- **Circuit breaker**: 5 fallos consecutivos → abrir circuito por 60s
- **Fallback**: si proveedor falla, continuar con lógica determinista
- **No bloquear**: enriquecimiento es best-effort, no crítico para triaje

### 7. Base de datos

#### Principio de mínimo privilegio
```sql
-- Rol de aplicación (no admin)
CREATE ROLE soc_app WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE soctriaje TO soc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO soc_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO soc_app;

-- Excepciones
REVOKE UPDATE, DELETE, TRUNCATE ON audit_log FROM soc_app;
GRANT INSERT ON audit_log TO soc_app;
```

#### Backups
- **Diarios**: `pg_dump` con cifrado
- **Retención**: 30 días
- **Prueba de restauración**: mensual

#### Cifrado
- **En tránsito**: TLS 1.2+ para todas las conexiones (DB, Redis, APIs externas)
- **En reposo**: cifrado de volúmenes Docker (opcional, recomendado en producción)

### 8. Cumplimiento y mapeo a estándares

#### NIST Cybersecurity Framework
- **DE.AE-2**: Analizar eventos detectados → clasificación LLM
- **DE.AE-3**: Correlacionar datos de eventos → enriquecimiento contextual
- **DE.AE-4**: Determinar impacto de eventos → severidad y acciones recomendadas
- **DE.CM-7**: Monitoreo de actividades no autorizadas → audit_log

#### ISO 27001:2022
- **A.8.15 (Logging)**: audit_log inmutable con todos los eventos de acceso
- **A.5.24 (Security incident management)**: flujo completo de alerta → triaje → incidente
- **A.5.33 (Protection of records)**: inmutabilidad y verificación de integridad

#### SOC 2 (Trust Services Criteria)
- **CC6.1**: Accountability → RBAC + audit_log
- **CC6.6**: Logical access controls → autenticación JWT + permisos
- **CC7.2**: Detection of anomalies → clasificación automática de alertas

### 9. Respuesta a incidentes de seguridad

#### Si se detecta compromiso
1. **Revocar tokens**: blacklist en Redis
2. **Bloquear usuario**: `is_active=false`
3. **Auditar**: revisar `audit_log` para entender alcance
4. **Notificar**: alertar a administradores
5. **Rotar secretos**: JWT keys, API keys externas
6. **Investigar**: analizar logs, DB, payloads

#### Disclosure responsable
- Contacto: [correo del responsable]
- No publicar vulnerabilidades sin dar tiempo a parchear (90 días)

### 10. Testing de seguridad

#### Casos de prueba obligatorios
- ✅ Usuario sin permisos recibe 403 en endpoints protegidos
- ✅ Token expirado recibe 401
- ✅ Token revocado (blacklist) recibe 401
- ✅ Intentos de SQL injection en filtros de búsqueda
- ✅ Intentos de UPDATE/DELETE en audit_log fallan
- ✅ verify-chain detecta registro manipulado
- ✅ Rate limit bloquea tras exceder límite
- ✅ Contraseñas débiles son rechazadas
- ✅ Prompt injection en alert payload no altera comportamiento del LLM

#### Herramientas (opcional v2)
- OWASP ZAP / Burp Suite: escaneo automatizado
- Bandit / Safety: análisis estático de código Python
- npm audit / Snyk: vulnerabilidades en dependencias JS

---

## Checklist de seguridad pre-deploy

- [ ] `.env.example` completo, `.env` real en `.gitignore`
- [ ] Ningún secreto hardcodeado en código
- [ ] CORS configurado con orígenes específicos
- [ ] Rate limiting activo
- [ ] Headers de seguridad configurados
- [ ] audit_log con triggers de protección
- [ ] Permisos DB con principio de mínimo privilegio
- [ ] Tests de RBAC pasando
- [ ] Webhooks con validación de firma
- [ ] Timeouts en todas las llamadas externas
- [ ] LLM por defecto es Ollama local
- [ ] Contraseñas con Argon2id/bcrypt
- [ ] JWT con refresh token en HttpOnly cookie
- [ ] CI ejecuta pip-audit y npm audit
