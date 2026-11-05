# Product Steering - SistemaTriaje (SOC-Lite)

## Propósito

SistemaTriaje es un sistema de triaje automático de alertas SOC para PYMEs que combina orquestación low-code (n8n) con razonamiento LLM (LangChain) para reducir la fatiga de alertas y el MTTT (Mean Time To Triage).

## Problema que resuelve

- Los SOAR comerciales cuestan decenas de miles de dólares (inaccesibles para PYMEs)
- Los SIEMs open source (Wazuh) generan alertas pero no las priorizan ni enriquecen
- 70-90% de alertas son falsos positivos o de baja relevancia
- Fatiga de alertas que causa que alertas críticas sean ignoradas

## Impacto

**CRÍTICO**: Reduce el MTTT de horas a minutos, cubre NIST CSF DE.AE (análisis de anomalías), habilita operación "24/7" sin personal nocturno y apoya ISO 27001 A.8.15 (registro de eventos) y A.5.24 (respuesta a incidentes).

## Usuarios y roles

| Rol | Responsabilidades | Permisos |
|-----|-------------------|----------|
| **Administrador** | Configuración del sistema, gestión de usuarios y roles | Todo: usuarios, roles, configuración, alertas, incidentes, reportes, bitácora (lectura) |
| **Analista** | Investigación y triaje de alertas, gestión de incidentes | Ver/gestionar alertas, triaje, incidentes (cambiar estado, comentar, reclasificar), ver dashboards |
| **Gestor** | Supervisión de métricas y generación de reportes | Solo dashboards y reportes (lectura y exportación) |
| **Auditor** | Revisión de bitácora y auditoría de cumplimiento | Solo bitácora (lectura/exportación). Sin acceso a alertas ni configuración |

## Métricas de éxito

1. **MTTT (Mean Time To Triage)**: Reducción de horas a < 5 minutos
2. **% Falsos Positivos**: Identificación automática de ≥ 85% de FP
3. **Reducción de ruido**: Filtrado automático de ≥ 70% de alertas de baja relevancia
4. **Tasa de escalación correcta**: ≥ 90% de alertas críticas correctamente identificadas
5. **Tiempo de respuesta del sistema**: < 30 segundos por alerta (incluido enriquecimiento)

## Alcance funcional

### En scope (MVP)
- Ingesta de alertas desde Wazuh y OPNsense
- Enriquecimiento con VirusTotal, AbuseIPDB, GeoIP
- Clasificación automática con LLM (local Ollama por defecto)
- Dashboard de métricas y alertas
- Sistema de notificaciones (Slack/Telegram)
- Integración con sistemas de ticketing (osTicket/Redmine)
- Reportes en PDF, Word y Excel
- RBAC con 4 roles
- Bitácora de auditoría inmutable

### Fuera de scope (v2+)
- Respuesta automática (aislamiento de hosts, bloqueo de IPs)
- Integración con más de 2 fuentes de alertas
- Análisis forense automatizado
- Machine learning para detección de anomalías
- App móvil
- Multi-tenancy

## Idioma

- **Documentación, UI y mensajes**: Español
- **Código e identificadores**: Inglés
- **Commits**: Español (Conventional Commits)
