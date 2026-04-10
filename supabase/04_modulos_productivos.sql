-- =============================================================
-- Módulos Productivos — Fase 1: BSF + base para truchas/conejos/lombrices
-- =============================================================
-- Tablas genéricas de lotes que sirven para CUALQUIER sistema productivo:
-- BSF, truchas, conejos, lombrices. Diseño modular.
-- Proyecto: pzkxbymwvimwnfmqoihj
-- Fecha: 2026-04-10
-- =============================================================

-- ── TABLA: modulos ──────────────────────────────────────────
-- Catálogo de los sistemas productivos de la finca
CREATE TABLE IF NOT EXISTS modulos (
    id          TEXT PRIMARY KEY,        -- bsf, truchas, conejos, lombrices, huerta, aves
    nombre      TEXT NOT NULL,
    descripcion TEXT,
    activo      BOOLEAN DEFAULT true,
    created_at  TIMESTAMPTZ DEFAULT now()
);

INSERT INTO modulos (id, nombre, descripcion) VALUES
    ('bsf',        'Mosca Soldado Negra',  'Producción de larvas BSF para alimento animal'),
    ('truchas',    'Truchas',              'Producción de truchas por tanque/lote'),
    ('conejos',    'Conejos',              'Cría y engorde de conejos'),
    ('lombrices',  'Lombricompost',         'Producción de humus con lombrices'),
    ('huerta',     'Huerta',               'Cultivo de hortalizas y aromáticas'),
    ('aves',       'Aves de Corral',       'Gallinas, gallos, pollitos')
ON CONFLICT (id) DO NOTHING;

-- ── TABLA: ubicaciones ──────────────────────────────────────
-- Dónde vive cada lote: bandeja, tanque, corral, cama, etc.
CREATE TABLE IF NOT EXISTS ubicaciones (
    id          SERIAL PRIMARY KEY,
    modulo_id   TEXT REFERENCES modulos(id),
    nombre      TEXT NOT NULL,           -- "Bandeja 1", "Tanque A", "Corral Norte"
    tipo        TEXT,                    -- bandeja, tanque, corral, cama_lombriz
    capacidad   TEXT,                    -- "5 kg", "1000 L", "10 conejos"
    activa      BOOLEAN DEFAULT true,
    notas       TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ubicaciones_modulo ON ubicaciones(modulo_id);

-- ── TABLA: lotes ────────────────────────────────────────────
-- Cada lote de producción (BSF, truchas, conejos, lombrices)
-- Un lote = un grupo de organismos que se maneja junto
CREATE TABLE IF NOT EXISTS lotes (
    id              SERIAL PRIMARY KEY,
    codigo          TEXT UNIQUE NOT NULL,     -- "BSF-001", "TRU-001", "CON-001", "LOM-001"
    modulo_id       TEXT REFERENCES modulos(id),
    ubicacion_id    INTEGER REFERENCES ubicaciones(id),
    etapa           TEXT NOT NULL,            -- BSF: huevo/larva/prepupa/pupa/adulto
                                             -- Truchas: alevin/juvenil/engorde/cosecha
                                             -- Conejos: cria/destete/engorde/reproductor
                                             -- Lombrices: activo/cosecha/reposo
    estado          TEXT DEFAULT 'Activo',    -- Activo, Finalizado, Cancelado
    fecha_inicio    DATE NOT NULL,
    fecha_fin       DATE,                    -- cuando el lote se cierra/cosecha
    cantidad_inicial NUMERIC,                -- cantidad al inicio (unidades, kg, g)
    unidad_cantidad TEXT DEFAULT 'unidades', -- unidades, kg, g, litros
    cantidad_actual NUMERIC,                 -- se actualiza con mediciones
    origen          TEXT,                    -- "Producción propia", "Compra", "Donación"
    notas           TEXT,
    created_by      TEXT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_lotes_modulo ON lotes(modulo_id);
CREATE INDEX IF NOT EXISTS idx_lotes_estado ON lotes(estado);
CREATE INDEX IF NOT EXISTS idx_lotes_etapa ON lotes(etapa);
CREATE INDEX IF NOT EXISTS idx_lotes_codigo ON lotes(codigo);

-- ── TABLA: lote_mediciones ──────────────────────────────────
-- Mediciones periódicas de un lote (peso, temperatura, pH, etc.)
CREATE TABLE IF NOT EXISTS lote_mediciones (
    id          SERIAL PRIMARY KEY,
    lote_id     INTEGER REFERENCES lotes(id) ON DELETE CASCADE,
    fecha       DATE NOT NULL,
    tipo        TEXT NOT NULL,           -- peso, temperatura, ph, humedad, mortalidad, observacion
    valor       NUMERIC,                 -- valor numérico (kg, °C, pH, %, etc.)
    unidad      TEXT,                    -- kg, g, °C, %, unidades
    nota        TEXT,                    -- observación libre
    created_by  TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_mediciones_lote ON lote_mediciones(lote_id);
CREATE INDEX IF NOT EXISTS idx_mediciones_fecha ON lote_mediciones(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_mediciones_tipo ON lote_mediciones(tipo);

-- ── TABLA: lote_alimentacion ────────────────────────────────
-- Registro de alimentación de cada lote
CREATE TABLE IF NOT EXISTS lote_alimentacion (
    id          SERIAL PRIMARY KEY,
    lote_id     INTEGER REFERENCES lotes(id) ON DELETE CASCADE,
    fecha       DATE NOT NULL,
    alimento    TEXT NOT NULL,           -- "Residuos cocina", "Concentrado", "Larvas BSF", "Pasto"
    cantidad    NUMERIC,
    unidad      TEXT,                    -- kg, g, litros
    origen      TEXT,                    -- "Cocina", "Compra", "Huerta", "BSF"
    costo       NUMERIC DEFAULT 0,
    nota        TEXT,
    created_by  TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_alimentacion_lote ON lote_alimentacion(lote_id);
CREATE INDEX IF NOT EXISTS idx_alimentacion_fecha ON lote_alimentacion(fecha DESC);

-- ── TABLA: cosechas ─────────────────────────────────────────
-- Producción final de un lote (larvas, humus, truchas, conejos)
CREATE TABLE IF NOT EXISTS cosechas (
    id              SERIAL PRIMARY KEY,
    lote_id         INTEGER REFERENCES lotes(id) ON DELETE CASCADE,
    fecha           DATE NOT NULL,
    producto        TEXT NOT NULL,       -- "Larvas BSF", "Lombricompost", "Trucha", "Conejo"
    cantidad        NUMERIC NOT NULL,
    unidad          TEXT NOT NULL,       -- kg, g, unidades, litros
    destino         TEXT,                -- "Gallinas", "Truchas", "Huerta", "Venta", "Hotel"
    valor_estimado  NUMERIC DEFAULT 0,   -- valor en COP si se vende
    nota            TEXT,
    created_by      TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cosechas_lote ON cosechas(lote_id);
CREATE INDEX IF NOT EXISTS idx_cosechas_fecha ON cosechas(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_cosechas_destino ON cosechas(destino);

-- ── TABLA: flujos_materia ───────────────────────────────────
-- Economía circular: movimientos entre sistemas productivos
-- Ej: "Residuos cocina → BSF", "Larvas BSF → Gallinas", "Compost → Huerta"
CREATE TABLE IF NOT EXISTS flujos_materia (
    id              SERIAL PRIMARY KEY,
    fecha           DATE NOT NULL,
    origen_modulo   TEXT REFERENCES modulos(id),  -- de dónde sale
    destino_modulo  TEXT REFERENCES modulos(id),  -- a dónde va
    material        TEXT NOT NULL,                -- "Residuos orgánicos", "Larvas", "Compost", "Estiércol"
    cantidad        NUMERIC,
    unidad          TEXT,                         -- kg, g, litros
    lote_origen_id  INTEGER REFERENCES lotes(id), -- lote de donde se sacó (opcional)
    lote_destino_id INTEGER REFERENCES lotes(id), -- lote al que se entregó (opcional)
    nota            TEXT,
    created_by      TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_flujos_fecha ON flujos_materia(fecha DESC);
CREATE INDEX IF NOT EXISTS idx_flujos_origen ON flujos_materia(origen_modulo);
CREATE INDEX IF NOT EXISTS idx_flujos_destino ON flujos_materia(destino_modulo);

-- ── TRIGGERS: auto-actualizar updated_at ─────────────────────
-- Reutiliza set_updated_at() que ya existe de migraciones anteriores
DROP TRIGGER IF EXISTS trg_lotes_updated ON lotes;
CREATE TRIGGER trg_lotes_updated
    BEFORE UPDATE ON lotes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ── Row Level Security ──────────────────────────────────────
ALTER TABLE modulos          ENABLE ROW LEVEL SECURITY;
ALTER TABLE ubicaciones      ENABLE ROW LEVEL SECURITY;
ALTER TABLE lotes            ENABLE ROW LEVEL SECURITY;
ALTER TABLE lote_mediciones  ENABLE ROW LEVEL SECURITY;
ALTER TABLE lote_alimentacion ENABLE ROW LEVEL SECURITY;
ALTER TABLE cosechas         ENABLE ROW LEVEL SECURITY;
ALTER TABLE flujos_materia   ENABLE ROW LEVEL SECURITY;

CREATE POLICY "allow_all_modulos"           ON modulos           FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_ubicaciones"       ON ubicaciones       FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_lotes"             ON lotes             FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_lote_mediciones"   ON lote_mediciones   FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_lote_alimentacion" ON lote_alimentacion FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_cosechas"          ON cosechas          FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_flujos_materia"    ON flujos_materia    FOR ALL USING (true) WITH CHECK (true);

GRANT SELECT, INSERT, UPDATE, DELETE ON modulos          TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON ubicaciones      TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON lotes            TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON lote_mediciones  TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON lote_alimentacion TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON cosechas         TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON flujos_materia   TO anon;

GRANT USAGE, SELECT ON SEQUENCE ubicaciones_id_seq      TO anon;
GRANT USAGE, SELECT ON SEQUENCE lotes_id_seq            TO anon;
GRANT USAGE, SELECT ON SEQUENCE lote_mediciones_id_seq  TO anon;
GRANT USAGE, SELECT ON SEQUENCE lote_alimentacion_id_seq TO anon;
GRANT USAGE, SELECT ON SEQUENCE cosechas_id_seq         TO anon;
GRANT USAGE, SELECT ON SEQUENCE flujos_materia_id_seq   TO anon;

-- ── Verificación ────────────────────────────────────────────
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('modulos','ubicaciones','lotes','lote_mediciones','lote_alimentacion','cosechas','flujos_materia')
ORDER BY tablename;
