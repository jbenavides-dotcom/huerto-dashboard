-- =============================================================
-- Huerta Bot Telegram — Tabla de estado para confirmaciones
-- =============================================================
-- Guarda acciones pendientes de confirmación por chat_id.
-- Cuando el usuario envía un comando de escritura, se guarda aquí
-- y el bot pregunta "¿confirmas?". Al recibir "sí", se ejecuta.
-- TTL: 10 minutos — después se considera expirado.
-- =============================================================

DROP TABLE IF EXISTS huerta_bot_state CASCADE;

CREATE TABLE huerta_bot_state (
    chat_id         BIGINT PRIMARY KEY,           -- ID del chat de Telegram
    pending_action  JSONB NOT NULL,               -- acción completa que espera confirmación
    pending_type    TEXT,                         -- confirmation | clarification
    question        TEXT,                         -- pregunta que hizo el bot (para contexto)
    created_at      TIMESTAMPTZ DEFAULT now(),
    expires_at      TIMESTAMPTZ DEFAULT (now() + interval '10 minutes')
);

CREATE INDEX idx_huerta_bot_state_expires ON huerta_bot_state(expires_at);

-- RLS: igual que el resto de huerta_*
ALTER TABLE huerta_bot_state ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_huerta_bot_state" ON huerta_bot_state FOR ALL USING (true) WITH CHECK (true);
GRANT SELECT, INSERT, UPDATE, DELETE ON huerta_bot_state TO anon;

-- Función para limpiar estados expirados (se puede llamar periódicamente)
CREATE OR REPLACE FUNCTION cleanup_expired_bot_state()
RETURNS void AS $$
BEGIN
  DELETE FROM huerta_bot_state WHERE expires_at < now();
END;
$$ LANGUAGE plpgsql;

-- Verificación
SELECT 'huerta_bot_state created' AS status;
