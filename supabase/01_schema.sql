-- =============================================================
-- Huerta LP&ET — Esquema Supabase (camas + bitácora)
-- =============================================================
-- Migración desde localStorage del dashboard → Supabase
-- Proyecto: pzkxbymwvimwnfmqoihj
-- Fecha: 2026-04-07
-- =============================================================

-- Limpieza (solo si se re-ejecuta)
DROP TABLE IF EXISTS huerta_bitacora CASCADE;
DROP TABLE IF EXISTS huerta_camas    CASCADE;

-- ── TABLA: huerta_camas ──────────────────────────────────────
-- Definición de las 12 camas + invernadero con:
--   - plantas asignadas (JSONB: array de plant IDs del PLANT_CATALOG)
--   - sensor físico asignado (soil_ch1..5 o null)
--   - grupo / nombre / orden para el render
CREATE TABLE huerta_camas (
    cama_id          TEXT PRIMARY KEY,            -- cama1, cama2, ..., cama12, invernadero
    nombre           TEXT NOT NULL,               -- "Cama 1", "Invernadero"
    grupo            TEXT NOT NULL,               -- hojas, hierbas, brasicas, rotacion, tomate
    orden            INTEGER NOT NULL DEFAULT 0,  -- para orden de render
    sensor_asignado  TEXT,                        -- soil_ch1..5 o null
    plantas          JSONB NOT NULL DEFAULT '[]'::jsonb,  -- array de plant IDs
    notas            TEXT,
    updated_at       TIMESTAMPTZ DEFAULT now(),
    updated_by       TEXT
);

CREATE INDEX idx_huerta_camas_grupo ON huerta_camas(grupo);

-- ── TABLA: huerta_bitacora ───────────────────────────────────
-- Log de cosecha, siembra, riego, observaciones, plagas, etc.
CREATE TABLE huerta_bitacora (
    id          BIGSERIAL PRIMARY KEY,
    local_id    TEXT UNIQUE,                      -- id local del dashboard (btk_123...)
    fecha       DATE NOT NULL,
    hora        TEXT,                             -- HH:MM
    cama_id     TEXT,                             -- FK lógica a huerta_camas.cama_id (puede ser null)
    tipo        TEXT NOT NULL,                    -- cosecha, siembra, trasplante, riego_manual, plagas, observacion, etc.
    planta_id   TEXT,                             -- FK lógica al PLANT_CATALOG (ej: repollo_morado)
    cantidad    NUMERIC,
    unidad      TEXT,                             -- kg, g, unidades, l, ml
    nota        TEXT,
    ts          BIGINT,                           -- epoch ms del dashboard
    created_by  TEXT,                             -- nombre/usuario que reportó (futuro: telegram_user)
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_huerta_bitacora_fecha    ON huerta_bitacora(fecha DESC);
CREATE INDEX idx_huerta_bitacora_cama     ON huerta_bitacora(cama_id);
CREATE INDEX idx_huerta_bitacora_tipo     ON huerta_bitacora(tipo);
CREATE INDEX idx_huerta_bitacora_planta   ON huerta_bitacora(planta_id);

-- ── Trigger: actualizar updated_at automáticamente ───────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Reutiliza la función si ya existía de la migración de animales
DROP TRIGGER IF EXISTS trg_huerta_camas_updated ON huerta_camas;
CREATE TRIGGER trg_huerta_camas_updated
  BEFORE UPDATE ON huerta_camas
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ── Row Level Security ──────────────────────────────────────
-- Permitir lectura y escritura pública a través de la anon key.
-- (Mismo patrón que inventario-animales.)
ALTER TABLE huerta_camas    ENABLE ROW LEVEL SECURITY;
ALTER TABLE huerta_bitacora ENABLE ROW LEVEL SECURITY;

CREATE POLICY "allow_all_huerta_camas"    ON huerta_camas    FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_huerta_bitacora" ON huerta_bitacora FOR ALL USING (true) WITH CHECK (true);

GRANT SELECT, INSERT, UPDATE, DELETE ON huerta_camas    TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON huerta_bitacora TO anon;
GRANT USAGE, SELECT ON SEQUENCE huerta_bitacora_id_seq TO anon;

-- ── Verificación ────────────────────────────────────────────
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('huerta_camas', 'huerta_bitacora')
ORDER BY tablename;
