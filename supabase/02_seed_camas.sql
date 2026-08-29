-- =============================================================
-- Huerta LP&ET — Seed de camas con siembra real 2026-08-29
-- =============================================================
-- Fuente: reporte de Jhon Huerta por WhatsApp (2026-08-29)
-- Ejecutar DESPUÉS de 01_schema.sql
-- Nota: usa UPSERT para poder re-correrlo sin duplicar
-- =============================================================

INSERT INTO huerta_camas (cama_id, nombre, grupo, orden, sensor_asignado, plantas, updated_by) VALUES
  ('cama1',       'Cama 1',       'hierbas',  1,  'soil_ch2', '["pimenton","cebollin","cebolla_larga","puerro"]'::jsonb,                                  'Jhon Huerta'),
  ('cama2',       'Cama 2',       'hojas',    2,  'soil_ch5', '["coliflor_blanca","calabacin"]'::jsonb,                                                   'Jhon Huerta'),
  ('cama3',       'Cama 3',       'hojas',    3,  'soil_ch1', '["cebollin","brocoli","espinaca"]'::jsonb,                                                 'Jhon Huerta'),
  ('cama4',       'Cama 4',       'hojas',    4,  'soil_ch3', '["calendula","lechuga_romana"]'::jsonb,                                                    'Jhon Huerta'),
  ('cama5',       'Cama 5',       'hierbas',  5,  NULL,       '["pimenton"]'::jsonb,                                                                      'Jhon Huerta'),
  ('cama6',       'Cama 6',       'hojas',    6,  NULL,       '["lechuga_crespa","calendula","albahaca_morada"]'::jsonb,                                  'Jhon Huerta'),
  ('cama7',       'Cama 7',       'hierbas',  7,  NULL,       '["cebolla_larga","menta"]'::jsonb,                                                         'Jhon Huerta'),
  ('cama8',       'Cama 8',       'hierbas',  8,  NULL,       '["perejil_crespo","coliflor_blanca","pimenton"]'::jsonb,                                   'Jhon Huerta'),
  ('cama9',       'Cama 9',       'hojas',    9,  NULL,       '["calabacin","pimenton"]'::jsonb,                                                          'Jhon Huerta'),
  ('cama10',      'Cama 10',      'hierbas',  10, NULL,       '["brocoli","perejil_crespo"]'::jsonb,                                                      'Jhon Huerta'),
  ('cama11',      'Cama 11',      'hojas',    11, NULL,       '["mizuna_roja","cilantro","rucula","lechuga_orejona","albahaca_morada","espinaca"]'::jsonb, 'Jhon Huerta'),
  ('cama12',      'Cama 12',      'hojas',    12, NULL,       '["rabano","pimenton","calendula","kale_rizado"]'::jsonb,                                    'Jhon Huerta'),
  ('invernadero', 'Invernadero',  'tomate',   13, 'soil_ch4', '["tomate_san_marzano","tomate_cherry","tomate_chonto"]'::jsonb,                             'Jhon Huerta')
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
