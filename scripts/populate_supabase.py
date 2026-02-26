"""
Script para poblar Supabase con los datos iniciales del proyecto
Ejecutar despues de crear las tablas con supabase_schema.sql
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Faltan SUPABASE_URL o SUPABASE_KEY en .env")
    exit(1)

# Crear cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ruta al archivo JSON
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "tareas_proyecto.json"

def cargar_json():
    """Carga los datos del archivo JSON"""
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def poblar_equipo(datos):
    """Inserta los miembros del equipo"""
    print("Poblando tabla: equipo...")
    for miembro in datos['equipo']:
        try:
            supabase.table('equipo').upsert({
                'id': miembro['id'],
                'nombre': miembro['nombre'],
                'rol': miembro.get('rol', '')
            }).execute()
            print(f"  + {miembro['nombre']}")
        except Exception as e:
            print(f"  Error con {miembro['nombre']}: {e}")

def poblar_estados(datos):
    """Inserta los estados"""
    print("Poblando tabla: estados...")
    for i, estado in enumerate(datos['estados']):
        try:
            supabase.table('estados').upsert({
                'id': estado['id'],
                'nombre': estado['nombre'],
                'color': estado['color'],
                'descripcion': estado.get('descripcion', ''),
                'orden': i
            }).execute()
            print(f"  + {estado['nombre']}")
        except Exception as e:
            print(f"  Error con {estado['nombre']}: {e}")

def poblar_categorias(datos):
    """Inserta las categorias"""
    print("Poblando tabla: categorias...")
    for cat in datos['categorias']:
        try:
            supabase.table('categorias').upsert({
                'id': cat['id'],
                'nombre': cat['nombre'],
                'icono': cat['icono']
            }).execute()
            print(f"  + {cat['nombre']}")
        except Exception as e:
            print(f"  Error con {cat['nombre']}: {e}")

def poblar_metadata(datos):
    """Inserta la metadata del proyecto"""
    print("Poblando tabla: metadata...")
    meta = datos['metadata']
    try:
        # Primero eliminar metadata existente
        supabase.table('metadata').delete().neq('id', 0).execute()

        supabase.table('metadata').insert({
            'proyecto': meta.get('proyecto', 'Huerta LPET'),
            'finca': meta.get('finca', 'La Palma y El Tucan'),
            'ubicacion': meta.get('ubicacion', 'Zipacon, Cundinamarca'),
            'fecha_inicio_obra': meta.get('fecha_inicio_obra', '2026-02-23'),
            'fecha_limite_compras': meta.get('fecha_limite_compras', '2026-02-20'),
            'ventana_critica': meta.get('ventana_critica', 'Cosecha inicia finales marzo / inicios abril')
        }).execute()
        print(f"  + Metadata del proyecto insertada")
    except Exception as e:
        print(f"  Error con metadata: {e}")

def poblar_tareas(datos):
    """Inserta las tareas"""
    print("Poblando tabla: tareas...")
    for tarea in datos['tareas']:
        try:
            supabase.table('tareas').upsert({
                'id': tarea['id'],
                'categoria': tarea['categoria'],
                'tarea': tarea['tarea'],
                'fecha_objetivo': tarea['fecha_objetivo'],
                'estado': tarea['estado'],
                'responsable': tarea['responsable'],
                'prioridad': tarea['prioridad'],
                'dependencias': tarea.get('dependencias', []),
                'notas': tarea.get('notas', '')
            }).execute()
            print(f"  + {tarea['tarea'][:50]}...")
        except Exception as e:
            print(f"  Error con tarea {tarea['id']}: {e}")

def main():
    print("=" * 50)
    print("POBLANDO SUPABASE CON DATOS DEL PROYECTO")
    print("=" * 50)
    print(f"URL: {SUPABASE_URL}")
    print(f"Archivo: {DATA_PATH}")
    print("=" * 50)

    # Cargar datos
    datos = cargar_json()
    print(f"Datos cargados: {len(datos['tareas'])} tareas")
    print()

    # Poblar tablas en orden (por dependencias de foreign keys)
    poblar_equipo(datos)
    print()

    poblar_estados(datos)
    print()

    poblar_categorias(datos)
    print()

    poblar_metadata(datos)
    print()

    poblar_tareas(datos)
    print()

    print("=" * 50)
    print("COMPLETADO!")
    print("=" * 50)

if __name__ == "__main__":
    main()
