#!/usr/bin/env python
"""Test Access database connection with current .env configuration."""

import os
import pyodbc
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

db_path = os.getenv('LEGACY_ACCESS_DB_PATH')
db_password = os.getenv('LEGACY_ACCESS_DB_PASSWORD')
driver = os.getenv('LEGACY_ACCESS_ODBC_DRIVER', 'Microsoft Access Driver (*.mdb, *.accdb)')
timeout = int(os.getenv('LEGACY_ACCESS_QUERY_TIMEOUT', '15'))

print(f'📍 DB Path: {db_path}')
print(f'📍 Exists: {Path(db_path).exists()}')
print(f'🔐 Password: {"***" if db_password else "NO ENCONTRADA"}')
print(f'🔌 Driver: {driver}')
print(f'⏱️  Timeout: {timeout}s')
print()

# Construir connection string
conn_string = (
    f'DRIVER={{{driver}}};'
    f'DBQ={Path(db_path).resolve()};'
    f'PWD={db_password};'
    f'ReadOnly=1;'
)

print('🔗 Intentando conexión...')
try:
    conn = pyodbc.connect(conn_string, timeout=timeout)
    cursor = conn.cursor()
    
    print(f'✅ CONEXIÓN ODBC EXITOSA')
    
    # Enlistar tablas accesibles
    tables = list(cursor.tables(tableType='TABLE'))
    print(f'\n📊 Tablas disponibles: {len(tables)}')
    
    if tables:
        print(f'\n📋 Primeras 10 tablas:')
        for i, table in enumerate(tables[:10]):
            print(f'  {i+1}. {table[2]}')  # table[2] es el nombre de la tabla
    
    # Intentar query en una tabla conocida
    print(f'\n🔍 Verificando acceso a datos reales...')
    try:
        # Access usa TOP en lugar de LIMIT
        cursor.execute("SELECT TOP 1 * FROM [A_00_Kilometrajes]")
        row = cursor.fetchone()
        if row:
            print(f'✅ Tabla "A_00_Kilometrajes" accesible')
            cols = [desc[0] for desc in cursor.description]
            print(f'   Columnas ({len(cols)}): {", ".join(cols[:5])}...')
        else:
            print(f'⚠️  Tabla "A_00_Kilometrajes" vacía')
    except Exception as e:
        print(f'⚠️  No se pudo acceder a "A_00_Kilometrajes": {e}')
    
    conn.close()
    print(f'\n✅ Prueba completada exitosamente')
except Exception as e:
    print(f'❌ ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
