-- =============================================
-- SCHEMA PARA SISTEMA DE TAREAS - HUERTA LPET
-- Ejecutar en Supabase SQL Editor
-- =============================================

-- Tabla: equipo (miembros del equipo)
CREATE TABLE IF NOT EXISTS equipo (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    rol TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: estados (estados de las tareas)
CREATE TABLE IF NOT EXISTS estados (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    color TEXT DEFAULT '#6c757d',
    descripcion TEXT,
    orden INT DEFAULT 0
);

-- Tabla: categorias (categorias de tareas)
CREATE TABLE IF NOT EXISTS categorias (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    icono TEXT DEFAULT '📌'
);

-- Tabla: metadata (informacion del proyecto)
CREATE TABLE IF NOT EXISTS metadata (
    id SERIAL PRIMARY KEY,
    proyecto TEXT NOT NULL,
    finca TEXT,
    ubicacion TEXT,
    fecha_inicio_obra DATE,
    fecha_limite_compras DATE,
    ventana_critica TEXT,
    ultima_modificacion TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: tareas (tareas del proyecto)
CREATE TABLE IF NOT EXISTS tareas (
    id TEXT PRIMARY KEY,
    categoria TEXT REFERENCES categorias(id),
    tarea TEXT NOT NULL,
    fecha_objetivo DATE,
    estado TEXT REFERENCES estados(id) DEFAULT 'por_iniciar',
    responsable TEXT REFERENCES equipo(id) DEFAULT 'sin_asignar',
    prioridad TEXT DEFAULT 'media',
    dependencias TEXT[], -- Array de IDs de tareas
    notas TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Trigger para actualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tareas_updated_at
    BEFORE UPDATE ON tareas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Habilitar RLS (Row Level Security) - Opcional pero recomendado
ALTER TABLE equipo ENABLE ROW LEVEL SECURITY;
ALTER TABLE estados ENABLE ROW LEVEL SECURITY;
ALTER TABLE categorias ENABLE ROW LEVEL SECURITY;
ALTER TABLE metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE tareas ENABLE ROW LEVEL SECURITY;

-- Politicas para permitir acceso publico (ajustar segun necesidades de seguridad)
CREATE POLICY "Allow public read equipo" ON equipo FOR SELECT USING (true);
CREATE POLICY "Allow public read estados" ON estados FOR SELECT USING (true);
CREATE POLICY "Allow public read categorias" ON categorias FOR SELECT USING (true);
CREATE POLICY "Allow public read metadata" ON metadata FOR SELECT USING (true);
CREATE POLICY "Allow public read tareas" ON tareas FOR SELECT USING (true);

CREATE POLICY "Allow public insert tareas" ON tareas FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update tareas" ON tareas FOR UPDATE USING (true);
CREATE POLICY "Allow public delete tareas" ON tareas FOR DELETE USING (true);

CREATE POLICY "Allow public insert equipo" ON equipo FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update equipo" ON equipo FOR UPDATE USING (true);

CREATE POLICY "Allow public insert metadata" ON metadata FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update metadata" ON metadata FOR UPDATE USING (true);

-- Indices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_tareas_estado ON tareas(estado);
CREATE INDEX IF NOT EXISTS idx_tareas_responsable ON tareas(responsable);
CREATE INDEX IF NOT EXISTS idx_tareas_categoria ON tareas(categoria);
CREATE INDEX IF NOT EXISTS idx_tareas_fecha ON tareas(fecha_objetivo);
