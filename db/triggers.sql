-- ============================================================================
-- SISTEMA TRIAJE - TRIGGERS DE AUDITORÍA
-- ============================================================================
-- Estos triggers aseguran la inmutabilidad de la tabla audit_log
-- Requisito crítico para cumplimiento ISO 27001 y SOC 2
-- ============================================================================

-- NOTA: Este script debe ejecutarse DESPUÉS de que Alembic cree la tabla audit_log

-- ============================================================================
-- FUNCIÓN: Prevenir modificación de audit_log
-- ============================================================================
CREATE OR REPLACE FUNCTION prevent_audit_modification()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_log es inmutable - operación % no permitida', TG_OP
        USING HINT = 'La tabla audit_log no puede ser modificada ni eliminada una vez insertada',
              ERRCODE = 'integrity_constraint_violation';
    RETURN NULL;  -- Nunca se alcanza, pero es requerido
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGER: Rechazar UPDATE en audit_log
-- ============================================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_log') THEN
        DROP TRIGGER IF EXISTS prevent_update_audit ON audit_log;
        CREATE TRIGGER prevent_update_audit
        BEFORE UPDATE ON audit_log
        FOR EACH ROW
        EXECUTE FUNCTION prevent_audit_modification();
        
        RAISE NOTICE 'Trigger prevent_update_audit creado en audit_log';
    ELSE
        RAISE WARNING 'Tabla audit_log no existe aún. Los triggers se aplicarán después de las migraciones.';
    END IF;
END
$$;

-- ============================================================================
-- TRIGGER: Rechazar DELETE en audit_log
-- ============================================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_log') THEN
        DROP TRIGGER IF EXISTS prevent_delete_audit ON audit_log;
        CREATE TRIGGER prevent_delete_audit
        BEFORE DELETE ON audit_log
        FOR EACH ROW
        EXECUTE FUNCTION prevent_audit_modification();
        
        RAISE NOTICE 'Trigger prevent_delete_audit creado en audit_log';
    ELSE
        RAISE WARNING 'Tabla audit_log no existe aún. Los triggers se aplicarán después de las migraciones.';
    END IF;
END
$$;

-- ============================================================================
-- FUNCIÓN: Calcular hash encadenado
-- ============================================================================
-- Esta función calcula el hash de un registro de audit_log incluyendo el hash previo
-- Implementa una cadena de bloques (blockchain-style) para detectar manipulación
CREATE OR REPLACE FUNCTION calculate_audit_hash()
RETURNS TRIGGER AS $$
DECLARE
    last_hash TEXT;
    content TEXT;
BEGIN
    -- Obtener el hash del último registro
    SELECT hash INTO last_hash
    FROM audit_log
    ORDER BY id DESC
    LIMIT 1;
    
    -- Si no hay registros previos, usar un hash inicial
    IF last_hash IS NULL THEN
        last_hash := 'GENESIS';
    END IF;
    
    -- Construir contenido a hashear
    content := CONCAT(
        COALESCE(NEW.id::TEXT, ''),
        COALESCE(NEW.ts::TEXT, ''),
        COALESCE(NEW.user_id::TEXT, ''),
        COALESCE(NEW.role, ''),
        COALESCE(NEW.action, ''),
        COALESCE(NEW.resource, ''),
        COALESCE(NEW.status_code::TEXT, ''),
        last_hash
    );
    
    -- Calcular y asignar hashes
    NEW.prev_hash := last_hash;
    NEW.hash := encode(digest(content, 'sha256'), 'hex');
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGER: Calcular hash automáticamente al insertar
-- ============================================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_log') THEN
        DROP TRIGGER IF EXISTS calculate_audit_hash_trigger ON audit_log;
        CREATE TRIGGER calculate_audit_hash_trigger
        BEFORE INSERT ON audit_log
        FOR EACH ROW
        EXECUTE FUNCTION calculate_audit_hash();
        
        RAISE NOTICE 'Trigger calculate_audit_hash_trigger creado en audit_log';
    ELSE
        RAISE WARNING 'Tabla audit_log no existe aún. Los triggers se aplicarán después de las migraciones.';
    END IF;
END
$$;

-- ============================================================================
-- REVOCAR PERMISOS de UPDATE/DELETE/TRUNCATE para soc_app
-- ============================================================================
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_log') THEN
        -- Revocar permisos peligrosos
        REVOKE UPDATE, DELETE, TRUNCATE ON audit_log FROM soc_app;
        
        -- Asegurar que tiene INSERT (necesario para registrar eventos)
        GRANT INSERT ON audit_log TO soc_app;
        GRANT SELECT ON audit_log TO soc_app;  -- Solo lectura para queries
        
        RAISE NOTICE 'Permisos de soc_app en audit_log configurados: INSERT y SELECT permitidos, UPDATE/DELETE/TRUNCATE revocados';
    ELSE
        RAISE WARNING 'Tabla audit_log no existe aún. Los permisos se aplicarán después de las migraciones.';
    END IF;
END
$$;

-- ============================================================================
-- TRIGGERS ADICIONALES: Auditar cambios críticos en otras tablas
-- ============================================================================

-- Trigger para auditar cambios de rol de usuario
CREATE OR REPLACE FUNCTION audit_user_role_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Este trigger se aplicará después de que la tabla user_roles exista
    -- Se implementará en la migración de Alembic
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para auditar cambios de severidad/estado de alertas
CREATE OR REPLACE FUNCTION audit_alert_change()
RETURNS TRIGGER AS $$
BEGIN
    -- Este trigger se aplicará después de que la tabla alerts exista
    -- Se implementará en la migración de Alembic
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Triggers de auditoría configurados.';
    RAISE NOTICE 'audit_log es ahora INMUTABLE para el rol soc_app.';
    RAISE NOTICE 'Cualquier intento de UPDATE/DELETE lanzará una excepción.';
    RAISE NOTICE '============================================';
END
$$;
