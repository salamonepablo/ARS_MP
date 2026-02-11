# Scripts de Utilidad

Scripts auxiliares para desarrollo y operación del sistema ARS_MP.

## Conexión a Base de Datos Access

### test_access_connection.py

Verifica la conexión ODBC a la base de datos Access legacy.

```bash
py scripts/test_access_connection.py
```

**Output esperado:**
- Path de la BD configurada en `.env`
- Estado de conexión ODBC
- Lista de tablas disponibles
- Verificación de acceso a datos

### toggle_db_path.py / toggle_db_path.ps1

Alterna entre la base de datos local (copia de desarrollo) y la remota (producción en unidad G: vía VPN).

**Python:**
```bash
py scripts/toggle_db_path.py show    # Ver path actual
py scripts/toggle_db_path.py local   # Cambiar a copia local
py scripts/toggle_db_path.py remote  # Cambiar a G: (VPN)
```

**PowerShell:**
```powershell
.\scripts\toggle_db_path.ps1 show
.\scripts\toggle_db_path.ps1 local
.\scripts\toggle_db_path.ps1 remote
```

## Paths Configurados

| Modo | Path |
|------|------|
| **Local** | `docs/legacy_bd/Accdb/DB_CCEE_Programación 1.1.accdb` |
| **Remote** | `G:\Material Rodante\1-Servicio Eléctrico\DB\Base de Dato Prog\DB_CCEE_Programación 1.1.accdb` |

## Notas

- La BD remota requiere conexión VPN activa
- La BD local es una copia para desarrollo/testing
- Usar `local` para desarrollo sin afectar producción
- Usar `remote` para sincronizar datos reales con `sync_access`
