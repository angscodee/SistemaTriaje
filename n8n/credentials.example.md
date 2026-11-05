# Configuración de credenciales de n8n

## Importar el workflow

1. Accede a n8n: http://localhost:5678
2. Credenciales: admin / (ver N8N_BASIC_AUTH_PASSWORD en .env)
3. Click en "Workflows" → "Import from File"
4. Selecciona `n8n/workflows/soc-lite-triage.json`

## Configurar credenciales

### PostgreSQL

**Nodo**: "PostgreSQL - Insert Alert" y "PostgreSQL - Save Triage"

- Host: `postgres`
- Port: `5432`
- Database: `soctriaje`
- User: `soc_app`
- Password: (ver DB_PASSWORD en .env)
- SSL: Disabled

### Variables de entorno

En n8n, ve a Settings → Environment Variables:

```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
TICKETING_API_URL=http://mock-ticketing:1080/api/tickets
TICKETING_API_KEY=dev_mock_api_key
SERVICE_API_KEY=dev_service_api_key_change_in_prod
```

### Modo dry-run (sin notificaciones reales)

Si no tienes Slack/Telegram configurado, el workflow funcionará en modo "dry-run":
- Los nodos de notificación intentarán enviar pero fallarán silenciosamente
- Los logs mostrarán el error pero el flujo continuará
- Los tickets se crearán en el mock-ticketing (solo en desarrollo)

## Activar el workflow

1. Una vez importado y configuradas las credenciales
2. Click en el toggle "Active" en la esquina superior derecha
3. El webhook estará disponible en: `http://localhost:5678/webhook/soc-alert`

## Probar el workflow

Ejecuta desde el host:

```bash
# Simular alertas
make simulate

# O manualmente:
python scripts/simulate_alerts.py
```

Las alertas deberían:
1. Llegar al webhook
2. Filtrarse por severidad
3. Insertarse en PostgreSQL
4. Procesarse por el AI service
5. Guardarse el triaje
6. Registrarse en la bitácora de auditoría

## Troubleshooting

### El webhook no responde

- Verifica que n8n está corriendo: `docker compose ps n8n`
- Verifica que el workflow está activo (toggle en ON)
- Verifica los logs: `docker compose logs n8n`

### Error de conexión a PostgreSQL

- Verifica credenciales en el nodo de PostgreSQL
- Verifica que el servicio postgres está corriendo
- Verifica que el rol `soc_app` existe en la base de datos

### Error en AI Service

- Verifica que ai-service está corriendo: `docker compose ps ai-service`
- Verifica logs: `docker compose logs ai-service`
- El servicio debería responder en: http://ai-service:8001/health

## Notas

- El workflow actual es una **versión simplificada** para demostración
- En producción, deberías:
  - Agregar validación de firma HMAC en el webhook
  - Implementar reintentos con backoff exponencial
  - Agregar manejo de errores más robusto
  - Configurar Slack/Telegram real
  - Integrar con osTicket/Redmine real
