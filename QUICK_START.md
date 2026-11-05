# 🚀 Inicio Rápido - SistemaTriaje

## Prerequisitos

- Docker 20.10+ y Docker Compose 2.0+
- 4 GB RAM mínimo (8 GB recomendado)
- 10 GB espacio en disco

## Instalación en 3 pasos

### 1. Clonar y configurar

```bash
git clone https://github.com/angscodee/SistemaTriaje.git
cd SistemaTriaje
cp .env.example .env
# Editar .env y cambiar contraseñas/secretos (opcional para dev)
```

### 2. Levantar servicios

```bash
docker compose up -d
# Espera 30 segundos para que todos los servicios estén listos
```

### 3. Inicializar base de datos

```bash
# Ejecutar migraciones
docker compose exec backend alembic upgrade head

# Poblar datos de prueba (4 usuarios + 300+ alertas)
docker compose exec backend python scripts/seed.py
```

## ✅ Verificar instalación

```bash
# Verificar que todos los servicios están saludables
docker compose ps

# O usar el healthcheck
docker compose exec backend python scripts/healthcheck.py
```

## 🎯 Acceder al sistema

### Dashboard (Frontend)
**URL**: http://localhost

El dashboard está en construcción, muestra una página placeholder con enlaces.

### Backend API (Swagger)
**URL**: http://localhost:8000/docs

Prueba el login:
1. Ve a `/api/v1/auth/login`
2. Ejecuta con:
   ```json
   {
     "email": "admin@example.com",
     "password": "Demo1234!"
   }
   ```
3. Copia el `access_token` de la respuesta
4. Haz clic en "Authorize" (arriba a la derecha)
5. Pega el token en el formato: `Bearer <tu_token>`

### n8n (Orquestador)
**URL**: http://localhost:5678
- Usuario: `admin`
- Contraseña: `n8nDemoPassword123` (ver .env)

## 👥 Credenciales de demo

| Rol | Email | Contraseña |
|-----|-------|------------|
| **Administrador** | admin@example.com | Demo1234! |
| **Analista** | analista@example.com | Demo1234! |
| **Gestor** | gestor@example.com | Demo1234! |
| **Auditor** | auditor@example.com | Demo1234! |

## 🧪 Probar el sistema

### Verificar que el backend responde

```bash
curl http://localhost:8000/health
# Respuesta esperada: {"status":"ok"}

curl http://localhost:8000/ready
# Respuesta esperada: {"status":"ready","checks":{"postgres":true,"redis":true}}
```

### Login vía API

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Demo1234!"}'
```

### Ver alertas de ejemplo

```bash
# Primero haz login y obtén el token
TOKEN="<tu_access_token>"

# Consulta la API (necesita implementar el endpoint alerts)
curl http://localhost:8000/api/v1/alerts \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Estado actual del proyecto

### ✅ Funcional
- ✅ Infraestructura Docker completa
- ✅ Backend FastAPI con auth + RBAC
- ✅ Modelos de base de datos (User, Role, Alert, Triage, Incident, AuditLog)
- ✅ Alembic para migraciones
- ✅ Script de seed con usuarios y alertas
- ✅ AI Service con endpoint básico (fallback)
- ✅ Frontend placeholder

### 🚧 En desarrollo
- ⏳ Endpoints de alertas (GET, PATCH, etc.)
- ⏳ Endpoints de métricas y reportes
- ⏳ Workflow de n8n (10 nodos)
- ⏳ Agente LangChain con herramientas
- ⏳ Dashboard React completo
- ⏳ Tests automatizados

## 🛠️ Comandos útiles

```bash
# Ver logs de todos los servicios
docker compose logs -f

# Ver logs solo del backend
docker compose logs -f backend

# Reiniciar servicios
docker compose restart

# Detener todo
docker compose down

# Detener y eliminar volúmenes (¡cuidado! elimina datos)
docker compose down -v

# Abrir shell en el backend
docker compose exec backend bash

# Abrir psql en PostgreSQL
docker compose exec postgres psql -U soc_admin -d soctriaje

# Ver estado de los servicios
docker compose ps
```

## 🐛 Solución de problemas

### El backend no arranca

```bash
# Ver logs para diagnóstico
docker compose logs backend

# Verificar que PostgreSQL está listo
docker compose exec postgres pg_isready -U soc_admin
```

### Error de conexión a base de datos

```bash
# Recrear migraciones
docker compose exec backend alembic downgrade base
docker compose exec backend alembic upgrade head
```

### Puerto 80 ya está en uso

Edita `docker-compose.yml` y cambia:
```yaml
  frontend:
    ports:
      - "8080:80"  # Cambiar de 80 a 8080
```

Luego accede en: http://localhost:8080

## 📖 Documentación completa

- **README principal**: [README.md](README.md)
- **Arquitectura**: [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) (por crear)
- **API**: [docs/API.md](docs/API.md) (por crear)
- **Seguridad**: [docs/SEGURIDAD.md](docs/SEGURIDAD.md) (por crear)
- **Manual de usuario**: [docs/MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md) (por crear)

## 🤝 Contribuir

Para contribuir al desarrollo, consulta las tareas pendientes en:
- [.kiro/specs/tasks.md](.kiro/specs/tasks.md)

## 📧 Soporte

- **Issues**: [https://github.com/angscodee/SistemaTriaje/issues](https://github.com/angscodee/SistemaTriaje/issues)
- **Repositorio**: [https://github.com/angscodee/SistemaTriaje](https://github.com/angscodee/SistemaTriaje)

---

**¡Listo!** Ya tienes SistemaTriaje funcionando localmente. 🎉
