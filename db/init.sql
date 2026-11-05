-- ============================================================================
-- SISTEMA TRIAJE - SCHEMA INICIAL
-- ============================================================================
-- Este script crea el rol de aplicación con permisos restringidos
-- Las tablas se crean con Alembic, este script solo configura permisos
-- ============================================================================

-- Crear rol de aplicación (no admin, permisos restringidos)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'soc_app') THEN
        CREATE ROLE soc_app WITH LOGIN PASSWORD 'changeme_db_password';
    END IF;
END
$$;

-- Grant connect
GRANT CONNECT ON DATABASE soctriaje TO soc_app;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO soc_app;

-- Grant permissions on all tables (serán creadas por Alembic)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO soc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO soc_app;

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Rol soc_app creado con permisos básicos.';
    RAISE NOTICE 'Las tablas serán creadas por Alembic.';
    RAISE NOTICE 'Los triggers de auditoría serán aplicados en 02-triggers.sql';
END
$$;
