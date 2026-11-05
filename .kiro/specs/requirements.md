# Requirements - SistemaTriaje (SOC-Lite)

## 1. Introducción

### 1.1 Propósito
Este documento define los requisitos funcionales y no funcionales del sistema de triaje automático de alertas SOC para PYMEs, que combina orquestación low-code (n8n) con razonamiento LLM (LangChain).

### 1.2 Alcance
SistemaTriaje automatiza la ingesta, enriquecimiento, clasificación y triaje de alertas de seguridad provenientes de Wazuh y OPNsense, reduciendo el MTTT de horas a minutos.

### 1.3 Referencias
- NIST Cybersecurity Framework v1.1
- ISO/IEC 27001:2022
- OWASP ASVS v4.0
- Documentación de Wazuh API
- Documentación de OPNsense

## 2. Requisitos funcionales (formato EARS)

### 2.1 Ingesta de alertas

**REQ-ING-001**: WHEN una alerta es enviada al webhook de n8n desde Wazuh o OPNsense, THEN el sistema SHALL validar la firma/token del webhook en el nodo 1.

**REQ-ING-002**: IF la validación de webhook es exitosa, THEN el sistema SHALL normalizar la alerta a un formato común con campos: external_id, source, rule_id, rule_description, raw_payload, src_ip, dst_ip, agent_name, severity_original, timestamp.

**REQ-ING-003**: IF la alerta tiene un fingerprint duplicado en los últimos 60 minutos, THEN el sistema SHALL marcarla como duplicada y SHOULD NOT procesar el triaje.

**REQ-ING-004**: IF la alerta tiene severidad original inferior a media (nivel 3 en Wazuh), THEN el sistema SHALL filtrarla en el nodo 2 y marcarla como "descartada por baja severidad".

**REQ-ING-005**: WHEN la alerta pasa los filtros del nodo 2, THEN el sistema SHALL persistirla en PostgreSQL con estado "pendiente" en el nodo 3.

**REQ-ING-006**: WHERE el payload del webhook excede 1 MB, THEN el sistema SHALL rechazarlo con código 413.

### 2.2 Enriquecimiento contextual

**REQ-ENR-001**: WHEN el microservicio ai-service recibe una solicitud de triaje, THEN el agente SHALL extraer indicadores (IPs, hashes, dominios) del payload normalizado.

**REQ-ENR-002**: IF se detecta una IP pública en src_ip o dst_ip, THEN el sistema SHALL consultar:
- VirusTotal (reputación de IP)
- AbuseIPDB (reportes de abuso)
- GeoIP (país, ASN, proveedor)

**REQ-ENR-003**: IF se detecta un hash de archivo, THEN el sistema SHALL consultar VirusTotal para obtener el score de detección de malware.

**REQ-ENR-004**: WHERE una API externa (VirusTotal, AbuseIPDB) no responde en 10 segundos, THEN el sistema SHALL aplicar timeout y continuar sin ese enriquecimiento.

**REQ-ENR-005**: IF una consulta de enriquecimiento ya existe en caché de Redis con TTL válido, THEN el sistema SHOULD reutilizar el resultado cacheado.

**REQ-ENR-006**: WHEN el enriquecimiento finaliza, THEN el sistema SHALL persistir los resultados en la tabla enrichment_data vinculada a la alerta.

**REQ-ENR-007**: WHERE SANITIZE_EXTERNAL_DATA=true, THEN el sistema SHALL enmascarar usuarios y hostnames internos antes de enviar a APIs externas.

### 2.3 Clasificación y triaje con LLM

**REQ-TRI-001**: WHEN el agente LangChain procesa una alerta, THEN SHALL invocar las herramientas personalizadas: virustotal_lookup, abuseipdb_check, geoip_lookup, historical_incidents_search, asset_context.

**REQ-TRI-002**: WHEN el agente completa el análisis, THEN SHALL generar un resultado de triaje validado con Pydantic que incluye:
- severity: [alta|media|baja]
- verdict: [verdadero_positivo|falso_positivo|requiere_revision]
- confidence: float [0.0-1.0]
- summary: string (máx 500 caracteres)
- recommended_actions: array de strings
- mitre_techniques: array de objetos {id, name}
- indicators: array de objetos {type, value}
- enrichment: objeto con datos de proveedores

**REQ-TRI-003**: WHERE el LLM no responde en 30 segundos o devuelve JSON inválido, THEN el sistema SHALL aplicar el fallback determinístico basado en reglas (mapeo rule_id → severity).

**REQ-TRI-004**: IF el fallback determinístico es usado, THEN el resultado SHALL indicar llm_model="fallback_rules".

**REQ-TRI-005**: WHEN el triaje finaliza, THEN el sistema SHALL persistir el resultado en triage_results y actualizar el estado de la alerta a "triada".

**REQ-TRI-006**: IF la clasificación determina severity="alta" Y verdict="verdadero_positivo", THEN el sistema SHALL ejecutar el nodo 8 (notificación) y nodo 9 (ticketing).

**REQ-TRI-007**: WHERE LLM_PROVIDER=ollama (por defecto), THEN el sistema SHALL usar Ollama local (llama3 o mistral) sin enviar datos fuera del servidor.

**REQ-TRI-008**: WHERE LLM_PROVIDER=openai, THEN el sistema SHALL advertir en logs que los datos de alertas se envían a un proveedor externo.

### 2.4 Notificaciones y ticketing

**REQ-NOT-001**: WHEN una alerta de severidad alta es triada, THEN el sistema SHALL enviar notificación al canal configurado (Slack o Telegram) en el nodo 8.

**REQ-NOT-002**: IF ENABLE_SLACK=false Y ENABLE_TELEGRAM=false, THEN el sistema SHALL ejecutar el nodo 8 en modo dry-run (log sin envío real).

**REQ-NOT-003**: WHEN una alerta de severidad alta es triada, THEN el sistema SHALL crear un ticket en el sistema configurado (osTicket o Redmine) en el nodo 9.

**REQ-NOT-004**: IF ENABLE_TICKETING=false, THEN el sistema SHALL ejecutar el nodo 9 en modo dry-run.

**REQ-NOT-005**: WHEN el ticket es creado exitosamente, THEN el sistema SHALL persistir un incidente en la tabla incidents con ticket_system, ticket_id y status="abierto".

### 2.5 Auditoría

**REQ-AUD-001**: WHEN cualquier request HTTP ingresa al backend, THEN el middleware de auditoría SHALL registrar en audit_log: user_id, role, method, path, status_code, ip, user_agent, request_id, timestamp (UTC).

**REQ-AUD-002**: WHEN un evento crítico ocurre (login, logout, cambio de rol, cambio de severidad/estado de alerta, cambio de estado de incidente, generación de reporte, acceso denegado), THEN el sistema SHALL registrar el evento con detalles JSONB (antes/después).

**REQ-AUD-003**: WHERE n8n ejecuta una acción (ingesta, triaje, notificación, ticketing), THEN n8n SHALL invocar POST /api/audit/external con API key de servicio en el nodo 10.

**REQ-AUD-004**: WHEN se intenta UPDATE o DELETE en audit_log, THEN el trigger PostgreSQL SHALL lanzar excepción y rechazar la operación.

**REQ-AUD-005**: WHEN se inserta un registro en audit_log, THEN el sistema SHALL calcular hash=SHA256(registro + prev_hash) y almacenarlo.

**REQ-AUD-006**: WHEN se solicita GET /audit/verify-chain, THEN el sistema SHALL recalcular la cadena de hashes y reportar si hay manipulación.

### 2.6 RBAC (Control de acceso basado en roles)

**REQ-RBAC-001**: WHEN un usuario autentica exitosamente, THEN el sistema SHALL generar un access_token JWT con claims: user_id, role, exp (15 min), iat, jti.

**REQ-RBAC-002**: WHEN un usuario autentica exitosamente, THEN el sistema SHALL generar un refresh_token con exp (7 días) almacenado en tabla refresh_tokens y en HttpOnly cookie.

**REQ-RBAC-003**: WHEN un token es revocado (logout, cambio de contraseña), THEN el sistema SHALL agregar jti a blacklist de Redis con TTL igual al exp del token.

**REQ-RBAC-004**: WHERE un endpoint requiere permiso específico, THEN el sistema SHALL verificar que el usuario tiene el permiso vía dependency @require_permission.

**REQ-RBAC-005**: IF el usuario no tiene el permiso requerido, THEN el sistema SHALL responder con 403 Forbidden y registrar el intento en audit_log.

**REQ-RBAC-006**: WHERE el rol es "Administrador", THEN el usuario SHALL tener todos los permisos.

**REQ-RBAC-007**: WHERE el rol es "Analista", THEN el usuario SHALL tener permisos: alerts:read, alerts:write, incidents:read, incidents:write, reports:read, triage:read, triage:write.

**REQ-RBAC-008**: WHERE el rol es "Gestor", THEN el usuario SHALL tener permisos: alerts:read, reports:read, reports:generate.

**REQ-RBAC-009**: WHERE el rol es "Auditor", THEN el usuario SHALL tener permisos: audit:read.

### 2.7 Dashboard y visualizaciones

**REQ-DASH-001**: WHEN un usuario autenticado accede al dashboard, THEN el sistema SHALL mostrar KPIs:
- Total de alertas (último mes)
- Alertas críticas abiertas (count con severity=alta y status!=cerrada)
- MTTT (Mean Time To Triage) en minutos (promedio de triaged_at - received_at)
- % Falsos positivos (count con verdict=falso_positivo / total)

**REQ-DASH-002**: WHEN el dashboard carga, THEN el sistema SHALL mostrar gráfico de línea temporal con alertas por severidad (últimos 7 días).

**REQ-DASH-003**: WHEN el dashboard carga, THEN el sistema SHALL mostrar gráfico de distribución de severidad (pie chart: alta, media, baja).

**REQ-DASH-004**: WHEN el dashboard carga, THEN el sistema SHALL mostrar top 10 IPs origen más frecuentes.

**REQ-DASH-005**: WHEN el dashboard carga, THEN el sistema SHALL mostrar top 10 reglas más disparadas.

**REQ-DASH-006**: WHEN el dashboard carga, THEN el sistema SHALL mostrar tendencia de reducción de ruido (% de alertas descartadas por filtros).

**REQ-DASH-007**: WHERE el usuario configura autorefresco, THEN el dashboard SHALL refrescar datos cada N segundos (configurable).

### 2.8 Gestión de alertas

**REQ-ALRT-001**: WHEN un usuario accede a la vista de alertas, THEN el sistema SHALL mostrar tabla paginada con columnas: ID, fecha, fuente, regla, severidad, estado, IPs origen/destino.

**REQ-ALRT-002**: WHERE el usuario aplica filtros (severidad, estado, fuente, rango de fechas, IP, texto), THEN el sistema SHALL filtrar las alertas en backend con query SQL indexado.

**REQ-ALRT-003**: WHEN el usuario hace clic en una alerta, THEN el sistema SHALL navegar a vista detallada con:
- Payload normalizado y crudo (expandible)
- Datos de enriquecimiento de VirusTotal, AbuseIPDB, GeoIP
- Resumen del LLM
- Veredicto y confianza
- Acciones recomendadas
- Técnicas MITRE
- Línea de tiempo (recibida, triada, notificada, ticket creado)

**REQ-ALRT-004**: IF el usuario tiene permiso alerts:write, THEN el sistema SHALL mostrar botones para: reclasificar severidad, cambiar estado, crear incidente, descartar.

**REQ-ALRT-005**: WHEN el usuario reclasifica una alerta, THEN el sistema SHALL solicitar justificación (textarea obligatorio) y registrar el cambio en audit_log.

### 2.9 Gestión de incidentes

**REQ-INC-001**: WHEN un usuario crea un incidente desde una alerta, THEN el sistema SHALL generar un incidente con: alert_id, title, severity (heredada), status="abierto", created_at.

**REQ-INC-002**: IF el incidente tiene ticket externo asociado, THEN el sistema SHALL almacenar ticket_system y ticket_id.

**REQ-INC-003**: WHERE el usuario tiene permiso incidents:write, THEN SHALL poder cambiar status (abierto → en_progreso → resuelto → cerrado) y agregar comentarios.

**REQ-INC-004**: WHEN el estado cambia a "cerrado", THEN el sistema SHALL registrar closed_at timestamp.

### 2.10 Reportes

**REQ-REP-001**: WHEN un usuario con permiso reports:generate solicita un reporte, THEN el sistema SHALL generar reporte en formato PDF, Word o Excel según lo solicitado.

**REQ-REP-002**: WHERE el tipo de reporte es "resumen ejecutivo", THEN SHALL incluir: KPIs, gráficos de tendencia, top alertas, recomendaciones.

**REQ-REP-003**: WHERE el tipo de reporte es "detalle de alertas", THEN SHALL incluir tabla con todas las alertas del rango de fechas seleccionado con sus detalles de triaje.

**REQ-REP-004**: WHERE el tipo de reporte es "métricas MTTT/FP", THEN SHALL incluir series temporales de MTTT y tasa de falsos positivos.

**REQ-REP-005**: WHEN un reporte es generado, THEN el sistema SHALL registrar el evento en audit_log con user_id y tipo de reporte.

### 2.11 Administración de usuarios y roles

**REQ-USR-001**: WHERE el usuario tiene permiso users:manage, THEN SHALL poder crear, editar, desactivar usuarios.

**REQ-USR-002**: WHEN se crea un usuario, THEN el sistema SHALL validar que la contraseña cumple la política (≥8 chars, 1 mayúscula, 1 número).

**REQ-USR-003**: WHEN se crea un usuario, THEN el sistema SHALL hashear la contraseña con Argon2id antes de persistir.

**REQ-USR-004**: WHERE el usuario tiene permiso roles:manage, THEN SHALL poder asignar/remover roles de usuarios.

**REQ-USR-005**: WHEN se cambia el rol de un usuario, THEN el sistema SHALL registrar el evento en audit_log con detalles del cambio.

## 3. Requisitos no funcionales

### 3.1 Rendimiento

**REQ-NFR-001**: El tiempo de triaje completo (ingesta → enriquecimiento → clasificación → persistencia) SHALL NOT exceder 30 segundos para el 95% de las alertas.

**REQ-NFR-002**: El MTTT (Mean Time To Triage) SHALL ser inferior a 5 minutos en promedio.

**REQ-NFR-003**: El backend SHALL responder a queries de dashboard en menos de 2 segundos para datasets de hasta 100,000 alertas.

**REQ-NFR-004**: El sistema SHALL soportar ingesta concurrente de al menos 100 alertas/minuto sin degradación.

### 3.2 Disponibilidad

**REQ-NFR-005**: Los servicios críticos (backend, ai-service, postgres, redis) SHALL tener health checks configurados con timeouts de 5 segundos.

**REQ-NFR-006**: IF un proveedor externo (VirusTotal, AbuseIPDB) no está disponible, THEN el sistema SHALL continuar operando con enriquecimiento parcial.

**REQ-NFR-007**: IF el LLM no responde, THEN el sistema SHALL aplicar fallback determinístico sin interrumpir el flujo.

### 3.3 Seguridad

**REQ-NFR-008**: Todas las contraseñas SHALL ser hasheadas con Argon2id con factor de trabajo mínimo de 2.

**REQ-NFR-009**: Todos los endpoints protegidos SHALL validar JWT en cada request.

**REQ-NFR-010**: La tabla audit_log SHALL ser inmutable (sin UPDATE/DELETE) con verificación por triggers.

**REQ-NFR-011**: El sistema SHALL implementar rate limiting con límite de 100 req/min por IP para endpoints GET y 20 req/min para POST/PUT/DELETE.

**REQ-NFR-012**: El sistema SHALL configurar headers de seguridad: X-Content-Type-Options, X-Frame-Options, HSTS, CSP.

**REQ-NFR-013**: El sistema SHALL usar CORS con orígenes explícitos (no wildcard en producción).

### 3.4 Escalabilidad

**REQ-NFR-014**: La base de datos SHALL usar índices en columnas de búsqueda frecuente: status, severity, received_at, src_ip, dst_ip, fingerprint.

**REQ-NFR-015**: El sistema SHALL implementar paginación obligatoria en todos los listados con límite máximo de 100 items por página.

**REQ-NFR-016**: El cache de Redis SHALL tener TTL configurable por tipo de enriquecimiento (default: VirusTotal 24h, AbuseIPDB 12h, GeoIP 7d).

### 3.5 Observabilidad

**REQ-NFR-017**: Todos los logs SHALL ser estructurados en formato JSON con campos: timestamp, level, request_id, user_id, message, context.

**REQ-NFR-018**: El sistema SHALL exponer endpoints /health (liveness) y /ready (readiness con chequeo de DB y Redis).

**REQ-NFR-019**: Cada request HTTP SHALL tener un request_id único propagado en headers y logs.

### 3.6 Usabilidad

**REQ-NFR-020**: La interfaz de usuario SHALL ser responsive (desktop, tablet, mobile).

**REQ-NFR-021**: La interfaz SHALL cumplir con WCAG 2.1 nivel AA en cuanto a accesibilidad.

**REQ-NFR-022**: La interfaz SHALL ofrecer modo oscuro por defecto con opción de alternancia.

**REQ-NFR-023**: Todos los textos de UI, mensajes y documentación SHALL estar en español.

### 3.7 Mantenibilidad

**REQ-NFR-024**: El código SHALL tener cobertura de tests ≥80% en servicios críticos del backend y ai-service.

**REQ-NFR-025**: El código Python SHALL pasar validación de mypy (type checking) sin errores.

**REQ-NFR-026**: El código TypeScript SHALL compilar con "strict": true sin errores.

**REQ-NFR-027**: Todas las migraciones de base de datos SHALL ser versionadas con Alembic.

## 4. Datos semilla (seed)

**REQ-SEED-001**: El sistema SHALL incluir script de seed que crea 4 usuarios (uno por rol: admin@example.com, analista@example.com, gestor@example.com, auditor@example.com) con contraseña "Demo1234!".

**REQ-SEED-002**: El script de seed SHALL crear al menos 300 alertas sintéticas con distribución realista: 80% baja/FP, 15% media, 5% alta.

**REQ-SEED-003**: Las alertas de seed SHALL incluir variedad de fuentes (Wazuh, OPNsense), reglas (SSH brute force, malware detection, port scan, failed login) e IPs.

## 5. Criterios de aceptación del sistema completo

El sistema se considera completo y listo para entrega cuando:

1. ✅ `docker compose up` levanta todos los servicios sin errores
2. ✅ `make seed` popula la base de datos con usuarios y alertas de prueba
3. ✅ `make simulate` envía alertas al webhook de n8n y estas atraviesan los 10 nodos del flujo
4. ✅ Las alertas aparecen en el dashboard con datos de triaje y enriquecimiento
5. ✅ Las alertas de severidad alta disparan notificación (real o dry-run) y ticket (real o mock)
6. ✅ Los duplicados y alertas de severidad < media son filtrados correctamente
7. ✅ Cada rol (Admin, Analista, Gestor, Auditor) solo accede a lo permitido (verificado con tests automáticos)
8. ✅ Intentos de UPDATE/DELETE en audit_log son rechazados (verificado con tests automáticos)
9. ✅ GET /audit/verify-chain detecta manipulación si se modifica manualmente un hash
10. ✅ Los reportes PDF, Word y Excel se generan y descargan correctamente
11. ✅ Si el LLM falla, el fallback por reglas produce un triaje válido
12. ✅ Todos los tests (backend, ai-service, frontend) pasan con cobertura ≥80% en servicios críticos
13. ✅ CI (GitHub Actions) ejecuta lint, type-check, tests y build exitosamente
14. ✅ README completo en español con instrucciones de instalación en 5 pasos y credenciales de demo
15. ✅ Documentación completa en docs/ (ARQUITECTURA, API, DECISIONES, RBAC, SEGURIDAD, MANUAL_USUARIO)
