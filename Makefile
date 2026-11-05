.PHONY: help up down restart logs migrate seed test lint simulate healthcheck clean build

# Colores para output
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "${GREEN}SistemaTriaje - Comandos disponibles:${NC}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${YELLOW}%-20s${NC} %s\n", $$1, $$2}'

up: ## Levantar todos los servicios
	@echo "${GREEN}Levantando servicios...${NC}"
	docker compose up -d
	@echo "${GREEN}Servicios levantados. Espera 10 segundos para que estén listos...${NC}"
	@sleep 10
	@$(MAKE) healthcheck

up-dev: ## Levantar servicios con perfil de desarrollo (Ollama + mock-ticketing)
	@echo "${GREEN}Levantando servicios en modo desarrollo...${NC}"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "${GREEN}Servicios levantados en modo dev.${NC}"

down: ## Detener y remover todos los servicios
	@echo "${YELLOW}Deteniendo servicios...${NC}"
	docker compose down

restart: down up ## Reiniciar todos los servicios

logs: ## Ver logs de todos los servicios (Ctrl+C para salir)
	docker compose logs -f

logs-backend: ## Ver logs del backend
	docker compose logs -f backend

logs-ai: ## Ver logs del ai-service
	docker compose logs -f ai-service

logs-frontend: ## Ver logs del frontend
	docker compose logs -f frontend

logs-n8n: ## Ver logs de n8n
	docker compose logs -f n8n

migrate: ## Ejecutar migraciones de base de datos
	@echo "${GREEN}Ejecutando migraciones...${NC}"
	docker compose exec backend alembic upgrade head
	@echo "${GREEN}Migraciones completadas.${NC}"

migrate-create: ## Crear nueva migración (usar: make migrate-create MSG="descripcion")
	@echo "${GREEN}Creando nueva migración: $(MSG)${NC}"
	docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

seed: ## Poblar base de datos con datos de prueba
	@echo "${GREEN}Poblando base de datos con datos de prueba...${NC}"
	docker compose exec backend python scripts/seed.py
	@echo "${GREEN}Base de datos poblada con 4 usuarios y 300+ alertas.${NC}"
	@echo "${GREEN}Credenciales de demo:${NC}"
	@echo "  Administrador: admin@example.com / Demo1234!"
	@echo "  Analista:      analista@example.com / Demo1234!"
	@echo "  Gestor:        gestor@example.com / Demo1234!"
	@echo "  Auditor:       auditor@example.com / Demo1234!"

simulate: ## Enviar alertas de prueba al webhook de n8n
	@echo "${GREEN}Simulando alertas...${NC}"
	docker compose exec backend python scripts/simulate_alerts.py
	@echo "${GREEN}Alertas enviadas. Verifica el dashboard en http://localhost${NC}"

healthcheck: ## Verificar estado de todos los servicios
	@echo "${GREEN}Verificando servicios...${NC}"
	@docker compose exec backend python scripts/healthcheck.py || echo "${YELLOW}Backend no responde${NC}"
	@echo "${GREEN}Healthcheck completado.${NC}"

test: ## Ejecutar todos los tests
	@echo "${GREEN}Ejecutando tests del backend...${NC}"
	docker compose exec backend pytest -v --cov=app --cov-report=term-missing
	@echo "${GREEN}Ejecutando tests del ai-service...${NC}"
	docker compose exec ai-service pytest -v --cov=app --cov-report=term-missing
	@echo "${GREEN}Ejecutando tests del frontend...${NC}"
	docker compose exec frontend npm run test

test-backend: ## Ejecutar solo tests del backend
	docker compose exec backend pytest -v --cov=app --cov-report=html

test-ai: ## Ejecutar solo tests del ai-service
	docker compose exec ai-service pytest -v --cov=app --cov-report=html

test-frontend: ## Ejecutar solo tests del frontend
	docker compose exec frontend npm run test

lint: ## Ejecutar linters en todo el código
	@echo "${GREEN}Linting backend...${NC}"
	docker compose exec backend ruff check app/
	docker compose exec backend black --check app/
	@echo "${GREEN}Linting ai-service...${NC}"
	docker compose exec ai-service ruff check app/
	docker compose exec ai-service black --check app/
	@echo "${GREEN}Linting frontend...${NC}"
	docker compose exec frontend npm run lint

format: ## Formatear código automáticamente
	@echo "${GREEN}Formateando backend...${NC}"
	docker compose exec backend black app/
	docker compose exec backend ruff check --fix app/
	@echo "${GREEN}Formateando ai-service...${NC}"
	docker compose exec ai-service black app/
	docker compose exec ai-service ruff check --fix app/
	@echo "${GREEN}Formateando frontend...${NC}"
	docker compose exec frontend npm run format

build: ## Construir imágenes Docker
	@echo "${GREEN}Construyendo imágenes...${NC}"
	docker compose build

clean: ## Limpiar volúmenes y contenedores (¡CUIDADO! Elimina datos)
	@echo "${YELLOW}¿Seguro que quieres eliminar todos los volúmenes? (y/N)${NC}"
	@read -r response; \
	if [ "$$response" = "y" ] || [ "$$response" = "Y" ]; then \
		docker compose down -v; \
		echo "${GREEN}Volúmenes eliminados.${NC}"; \
	else \
		echo "${GREEN}Operación cancelada.${NC}"; \
	fi

shell-backend: ## Abrir shell en container del backend
	docker compose exec backend bash

shell-ai: ## Abrir shell en container del ai-service
	docker compose exec ai-service bash

shell-db: ## Abrir psql en PostgreSQL
	docker compose exec postgres psql -U soc_admin -d soctriaje

shell-redis: ## Abrir redis-cli
	docker compose exec redis redis-cli

install: up migrate seed ## Instalación completa (up + migrate + seed)
	@echo "${GREEN}============================================${NC}"
	@echo "${GREEN}Instalación completada exitosamente!${NC}"
	@echo "${GREEN}============================================${NC}"
	@echo ""
	@echo "Accede a:"
	@echo "  - Dashboard:  http://localhost"
	@echo "  - Backend API: http://localhost:8000/docs"
	@echo "  - n8n:        http://localhost:5678"
	@echo ""
	@echo "Credenciales de demo:"
	@echo "  - Administrador: admin@example.com / Demo1234!"
	@echo "  - Analista:      analista@example.com / Demo1234!"
	@echo "  - Gestor:        gestor@example.com / Demo1234!"
	@echo "  - Auditor:       auditor@example.com / Demo1234!"
	@echo ""
	@echo "Para simular alertas: ${YELLOW}make simulate${NC}"

status: ## Ver estado de los servicios
	docker compose ps
