-- =============================================================
-- Huerta LP&ET — Seed de camas con siembra real 2026-04-07
-- =============================================================
-- Fuente: reporte de Jhon Huerta (2026-04-07)
-- Ejecutar DESPUÉS de 01_schema.sql
-- Nota: usa UPSERT para poder re-correrlo sin duplicar
-- =============================================================

INSERT INTO huerta_camas (cama_id, nombre, grupo, orden, sensor_asignado, plantas, updated_by) VALUES
  ('cama1',       'Cama 1',       'brasicas', 1,  'soil_ch2', '["repollo_morado","coliflor_blanca","cebollin"]'::jsonb,        'Jhon Huerta'),
  ('cama2',       'Cama 2',       'hierbas',  2,  'soil_ch5', '["zanahoria","perejil_liso"]'::jsonb,                           'Jhon Huerta'),
  ('cama3',       'Cama 3',       'hojas',    3,  'soil_ch1', '["lechuga_crespa","lechuga_morada_lisa"]'::jsonb,               'Jhon Huerta'),
  ('cama4',       'Cama 4',       'hojas',    4,  'soil_ch3', '["acelga_comun","calendula"]'::jsonb,                           'Jhon Huerta'),
  ('cama5',       'Cama 5',       'brasicas', 5,  NULL,       '["calendula","aji_jalapeno","repollo_morado"]'::jsonb,          'Jhon Huerta'),
  ('cama6',       'Cama 6',       'brasicas', 6,  NULL,       '["repollo_morado"]'::jsonb,                                     'Jhon Huerta'),
  ('cama7',       'Cama 7',       'hierbas',  7,  NULL,       '["cebolla_larga","hierbabuena"]'::jsonb,                        'Jhon Huerta'),
  ('cama8',       'Cama 8',       'hierbas',  8,  NULL,       '["tomillo"]'::jsonb,                                            'Jhon Huerta'),
  ('cama9',       'Cama 9',       'rotacion', 9,  NULL,       '[]'::jsonb,                                                     'Jhon Huerta'),
  ('cama10',      'Cama 10',      'brasicas', 10, NULL,       '["remolacha","coliflor_blanca","repollo_morado"]'::jsonb,       'Jhon Huerta'),
  ('cama11',      'Cama 11',      'rotacion', 11, NULL,       '[]'::jsonb,                                                     'Jhon Huerta'),
  ('cama12',      'Cama 12',      'rotacion', 12, NULL,       '[]'::jsonb,                                                     'Jhon Huerta'),
  ('invernadero', 'Invernadero',  'tomate',   13, 'soil_ch4', '["tomate_san_marzano","tomate_cherry","tomate_chonto"]'::jsonb, 'Jhon Huerta')
ON CONFLICT (cama_id) DO UPDATE SET
  nombre          = EXCLUDED.nombre,
  grupo           = EXCLUDED.grupo,
  orden           = EXCLUDED.orden,
  sensor_asignado = EXCLUDED.sensor_asignado,
  plantas         = EXCLUDED.plantas,
  updated_by      = EXCLUDED.updated_by,
  updated_at      = now();

-- Verificación
SELECT cama_id, nombre, grupo, sensor_asignado, jsonb_array_length(plantas) AS n_plantas
FROM huerta_camas
ORDER BY orden;
