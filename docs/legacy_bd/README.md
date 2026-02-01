# Legacy Database Files

## Por que no estan en el repositorio

Los archivos de bases de datos legacy (`.mdb`, `.accdb`, `.csv`, `.xlsx`) **no se incluyen en el repositorio** debido a su tamano (algunos superan los 90MB), lo cual excede el limite recomendado por GitHub de 50MB por archivo.

## Como obtener los archivos

Los archivos estan disponibles en **Google Drive**. Para acceder:

1. Solicitar acceso enviando tu direccion de correo a los responsables del proyecto
2. Una vez autorizado, descargar desde:
   
   **[Google Drive - Legacy BD](https://drive.google.com/drive/folders/1wE95LbRJdRsRl8A_1dSkVpykBnReR8e4?usp=drive_link)**

3. Colocar los archivos descargados en esta estructura:

```
docs/legacy_bd/
├── Accdb/
│   ├── CSR_Kms_MantEvents.xlsx
│   ├── CSR_LecturasKms.csv
│   ├── CSR_MantEvents.csv
│   ├── CSR_Modulos.csv
│   └── DB_CCEE_Programacion 1.1.accdb
└── Access20/
    ├── baseCCEE.mdb
    ├── baseCCRR.mdb
    └── baseLocs.mdb
```

## Descripcion de archivos

### Access20/ (Sistema Legacy VB6 - desde 1990)

| Archivo | Descripcion | Tamano aprox. |
|---------|-------------|---------------|
| `baseCCEE.mdb` | Base de coches electricos | ~67 MB |
| `baseCCRR.mdb` | Base de coches remolque | ~96 MB |
| `baseLocs.mdb` | Base de locomotoras | ~69 MB |

### Accdb/ (Sistema actual - 2015 a presente)

| Archivo | Descripcion | Tamano aprox. |
|---------|-------------|---------------|
| `DB_CCEE_Programacion 1.1.accdb` | Programacion coches electricos | ~63 MB |
| `CSR_Kms_MantEvents.xlsx` | Kilometrajes y eventos (export) | <1 MB |
| `CSR_LecturasKms.csv` | Lecturas de kilometraje | <1 MB |
| `CSR_MantEvents.csv` | Eventos de mantenimiento | <1 MB |
| `CSR_Modulos.csv` | Listado de modulos/unidades | <1 MB |

## Nota para evaluadores del TFM

Al momento de la presentacion del proyecto, se proporcionara acceso al Drive con los archivos de prueba. Indicar la direccion de correo para habilitar el acceso.

## Verificacion

Una vez descargados los archivos, podes verificar que estan correctamente ubicados ejecutando:

```powershell
# Desde la raiz del proyecto
Test-Path "docs/legacy_bd/Access20/baseCCEE.mdb"
Test-Path "docs/legacy_bd/Accdb/DB_CCEE_Programacion 1.1.accdb"
```

Ambos comandos deberian devolver `True`.
