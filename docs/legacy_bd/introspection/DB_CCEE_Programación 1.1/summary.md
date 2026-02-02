# Database Schema: DB_CCEE_Programación 1.1

**Source file:** `DB_CCEE_Programación 1.1.accdb`

## Summary

- **Tables:** 57
- **Queries/Views:** 7
- **Total Columns:** 453
- **Index Entries:** 73
- **Relationships:** 0

## Tables

### A_00_Clase_Vehículo

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Clase_Vehículo | COUNTER | 10 | NO | - |
| Clase_Vehículo | VARCHAR | 255 | YES | - |
| Tipo_MR | VARCHAR | 255 | YES | - |
| Marca_MR | VARCHAR | 255 | YES | - |
| Modelo_MR | VARCHAR | 255 | YES | - |
| Línea | VARCHAR | 255 | YES | - |

### A_00_Coches

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Coches | COUNTER | 10 | NO | - |
| Coche | INTEGER | 10 | YES | - |
| Ubicación | VARCHAR | 255 | YES | - |
| Descripción | VARCHAR | 255 | YES | - |
| Clase_Vehículo | INTEGER | 10 | YES | - |
| Posición | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id_Coches

**Indexes:**
- `PrimaryKey` (Id_Coches) UNIQUE
- `Id_Coches` (Id_Coches) 

### A_00_Estado_Habilitación

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Hab | COUNTER | 10 | NO | - |
| Habilitación | VARCHAR | 255 | YES | - |
| Módulo | VARCHAR | 255 | YES | - |
| Inspección_Previa | DATETIME | 19 | YES | - |
| Inspección_Estática | DATETIME | 19 | YES | - |
| Ensayo_Dinámico | DATETIME | 19 | YES | - |
| Estado | VARCHAR | 255 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |
| kilometraje | INTEGER | 10 | YES | - |
| OT-Simaf | VARCHAR | 255 | YES | - |
| Certificados | BIT | 1 | NO | - |

### A_00_Formaciones

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Formaciones | COUNTER | 10 | NO | - |
| Formaciones | VARCHAR | 255 | YES | - |
| Clase_Vehículo | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id_Formaciones

**Indexes:**
- `PrimaryKey` (Id_Formaciones) UNIQUE

### A_00_Kilometrajes

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Kilometrajes | COUNTER | 10 | NO | - |
| Módulo | INTEGER | 10 | YES | - |
| kilometraje | INTEGER | 10 | YES | - |
| Fecha | DATETIME | 19 | YES | - |

**Primary Key (inferred):** Id_Kilometrajes

**Indexes:**
- `PrimaryKey` (Id_Kilometrajes) UNIQUE

### A_00_Módulos

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Módulos | COUNTER | 10 | NO | - |
| Módulos | VARCHAR | 255 | YES | - |
| Clase_Vehículos | INTEGER | 10 | YES | - |
| Cabina | VARCHAR | 255 | YES | - |

### A_00_Observaciones

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id | INTEGER | 10 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |

**Indexes:**
- `{45675E34-AB47-49C3-A86C-D5512C17F7BB}` (Id) 
- `Id` (Id) 

### A_00_OT_Simaf

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_OT_Simaf | COUNTER | 10 | NO | - |
| OT_Simaf | VARCHAR | 255 | YES | - |
| Módulo | INTEGER | 10 | YES | - |
| Ingreso | VARCHAR | 255 | YES | - |
| Tipo_Tarea | VARCHAR | 255 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Km | INTEGER | 10 | YES | - |
| Fecha_Inicio | DATETIME | 19 | YES | - |
| Fecha_Fin | DATETIME | 19 | YES | - |

**Primary Key (inferred):** Id_OT_Simaf

**Indexes:**
- `OT_Simaf` (OT_Simaf) UNIQUE
- `PrimaryKey` (Id_OT_Simaf) UNIQUE

### A_00_Próxima_Tarea

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Próxima_Tarea | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Próxima_Tarea | VARCHAR | 255 | YES | - |
| Km_entre_Tareas | DOUBLE | 53 | YES | - |
| Tiempo_entre_Tareas | DOUBLE | 53 | YES | - |
| Km_resguardo | DOUBLE | 53 | YES | - |
| Tareas_Para | VARCHAR | 255 | YES | - |
| ORDEN | VARCHAR | 255 | YES | - |

### A_00_Tareas

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Tareas | COUNTER | 10 | NO | - |
| Ingreso | VARCHAR | 255 | YES | - |
| Tipo_Tarea | VARCHAR | 255 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Descripción | VARCHAR | 255 | YES | - |
| Clase_Vehículo | INTEGER | 10 | YES | - |
| Datos | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id_Tareas

**Indexes:**
- `PrimaryKey` (Id_Tareas) UNIQUE

### A_01_Grupos

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Grupos | COUNTER | 10 | NO | - |
| Grupos | VARCHAR | 255 | YES | - |
| Sub_Gurpos | VARCHAR | 255 | YES | - |
| Clase_Vehículo | INTEGER | 10 | YES | - |

**Primary Key (inferred):** Id_Grupos

**Indexes:**
- `PrimaryKey` (Id_Grupos) UNIQUE

### A_01_Lista_Materiales

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Materiales | COUNTER | 10 | NO | - |
| Material | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id_Materiales

**Indexes:**
- `PrimaryKey` (Id_Materiales) UNIQUE

### A_01_Remplazo_Materiales

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Remplazo_Materiales | COUNTER | 10 | NO | - |
| Remplazo | VARCHAR | 255 | YES | - |
| Material | INTEGER | 10 | YES | - |
| Cantidad | INTEGER | 10 | YES | - |
| Estado | VARCHAR | 255 | YES | - |
| Módulo | INTEGER | 10 | YES | - |
| Coche | VARCHAR | 255 | YES | - |
| kilometraje | INTEGER | 10 | YES | - |
| Fecha | DATETIME | 19 | YES | - |
| Intervención | VARCHAR | 255 | YES | - |
| OT_Simaf | VARCHAR | 255 | YES | - |
| Observación | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id_Remplazo_Materiales

**Indexes:**
- `PrimaryKey` (Id_Remplazo_Materiales) UNIQUE

### A_01_Tipo_Novedad

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Tipo_Novedad | COUNTER | 10 | NO | - |
| Tipo_Novedad | VARCHAR | 255 | YES | - |
| Motivo_Novedad | VARCHAR | 255 | YES | - |
| Clase_Vehículo | INTEGER | 10 | YES | - |

**Primary Key (inferred):** Id_Tipo_Novedad

**Indexes:**
- `PrimaryKey` (Id_Tipo_Novedad) UNIQUE

### A_08_Organos_Parque

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_OGP | COUNTER | 10 | NO | - |
| Organo_Parque | VARCHAR | 50 | YES | - |
| Número | VARCHAR | 255 | YES | - |
| Clase_Vehículo | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id_OGP

**Indexes:**
- `Número` (Número) UNIQUE
- `PrimaryKey` (Id_OGP) UNIQUE
- `A_08_Organos_ParqueClase_Vehículo` (Clase_Vehículo) 

### A_12_Accidentales_Anexar

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id | COUNTER | 10 | NO | - |
| Formación | VARCHAR | 255 | YES | - |
| Módulo | VARCHAR | 255 | YES | - |
| Coche | INTEGER | 10 | YES | - |
| Tipo de trabajo | VARCHAR | 255 | YES | - |
| Fecha | DATETIME | 19 | YES | - |
| Tarea a realizar | VARCHAR | 255 | YES | - |
| Trabajo realizado por GOP | LONGCHAR | 1073741823 | YES | - |
| Sector | VARCHAR | 255 | YES | - |
| OT | VARCHAR | 255 | YES | - |
| Tipo de tarea | VARCHAR | 255 | YES | - |
| Tareas realizadas | LONGCHAR | 1073741823 | YES | - |
| OT SIMAF | VARCHAR | 255 | YES | - |
| Resolución | VARCHAR | 255 | YES | - |
| Ticket | DOUBLE | 53 | YES | - |
| ID tarea | DOUBLE | 53 | YES | - |
| Tipo MR | VARCHAR | 255 | YES | - |
| Archivo | BIT | 1 | NO | - |

**Primary Key (inferred):** Id

**Indexes:**
- `PrimaryKey` (Id) UNIQUE
- `ID tarea` (ID tarea) 

### A_12_Accidentales_Tabla

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id | COUNTER | 10 | NO | - |
| Formación | VARCHAR | 255 | YES | - |
| Módulo | VARCHAR | 255 | YES | - |
| Coche | INTEGER | 10 | YES | - |
| Tipo de trabajo | VARCHAR | 255 | YES | - |
| Fecha | DATETIME | 19 | YES | - |
| Tarea a realizar | LONGCHAR | 1073741823 | YES | - |
| Trabajo realizado por GOP | VARCHAR | 255 | YES | - |
| Sector | VARCHAR | 255 | YES | - |
| OT | VARCHAR | 255 | YES | - |
| Tipo de tarea | VARCHAR | 255 | YES | - |
| Tareas realizadas | LONGCHAR | 1073741823 | YES | - |
| OT SIMAF | VARCHAR | 255 | YES | - |
| Resolución | DOUBLE | 53 | YES | - |
| Ticket | DOUBLE | 53 | YES | - |
| ID tarea | DOUBLE | 53 | YES | - |
| Tipo MR | VARCHAR | 255 | YES | - |
| Archivo | BIT | 1 | NO | - |

**Primary Key (inferred):** Id

**Indexes:**
- `PrimaryKey` (Id) UNIQUE
- `ID tarea` (ID tarea) 

### A_14_Cambio_Coches

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Cambio_Coches | COUNTER | 10 | NO | - |
| Módulo | INTEGER | 10 | YES | - |
| Coches | INTEGER | 10 | YES | - |
| Fecha | DATETIME | 19 | YES | - |
| Descripción | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id_Cambio_Coches

**Indexes:**
- `PrimaryKey` (Id_Cambio_Coches) UNIQUE

### A_14_Cambio_Módulos

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Cambio_Módulos | COUNTER | 10 | NO | - |
| Módulos | INTEGER | 10 | YES | - |
| Formaciones | INTEGER | 10 | YES | - |
| Cabina | VARCHAR | 255 | YES | - |
| Fecha | DATETIME | 19 | YES | - |

### A_15_Lavados

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Lavado | COUNTER | 10 | NO | - |
| Formación | VARCHAR | 255 | YES | - |
| Fecha | DATETIME | 19 | YES | - |
| Depósito | VARCHAR | 255 | YES | - |
| Turno | VARCHAR | 255 | YES | - |
| Intervención | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id_Lavado

**Indexes:**
- `PrimaryKey` (Id_Lavado) UNIQUE

### A_17_Módulos_Bajo_Seguimiento

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Mod_Seguimiento | INTEGER | 10 | YES | - |
| Módulo | INTEGER | 10 | YES | - |
| Fecha | DATETIME | 19 | YES | - |
| Información Adicional | VARCHAR | 255 | YES | - |

### A_17_Seguimientos

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Seguimientos | COUNTER | 10 | NO | - |
| Nombre | VARCHAR | 255 | YES | - |
| Descripción | VARCHAR | 255 | YES | - |
| Tarea_a_Realizar | VARCHAR | 255 | YES | - |
| Frecuencia | INTEGER | 10 | YES | - |
| Tipo | VARCHAR | 255 | YES | - |
| Fecha_Inicio | DATETIME | 19 | YES | - |
| Fecha_Fin | DATETIME | 19 | YES | - |
| Documentos_Relacionados | VARCHAR | 255 | YES | - |
| Estado | VARCHAR | 255 | YES | - |
| Notas Finales | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id_Seguimientos

**Indexes:**
- `PrimaryKey` (Id_Seguimientos) UNIQUE

### A_30_Matafuefos

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id | COUNTER | 10 | NO | - |
| N_Serie | VARCHAR | 255 | YES | - |
| Ubición | VARCHAR | 255 | YES | - |
| Módulo | INTEGER | 10 | YES | - |
| Estado | VARCHAR | 255 | YES | - |
| Tipo | VARCHAR | 255 | YES | - |
| Mes | VARCHAR | 255 | YES | - |
| Año | INTEGER | 10 | YES | - |
| Vencimiento | VARCHAR | 243 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id

**Indexes:**
- `Módulo` (Módulo) UNIQUE
- `N° Serie` (N_Serie) UNIQUE
- `PrimaryKey` (Id) UNIQUE

### A_31_Descarga_Eventos

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Descarga_Eventos | COUNTER | 10 | NO | - |
| Formación | VARCHAR | 255 | YES | - |
| Fecha | DATETIME | 19 | YES | - |
| Observación | VARCHAR | 255 | YES | - |
| Registro | DATETIME | 19 | YES | - |

**Primary Key (inferred):** Id_Descarga_Eventos

**Indexes:**
- `PrimaryKey` (Id_Descarga_Eventos) UNIQUE

### A_32_Medición_Torno_Semestral

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_MED_TOR | COUNTER | 10 | NO | - |
| Módulo | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| kilometraje | INTEGER | 10 | YES | - |
| Fecha | DATETIME | 19 | YES | - |
| OT-Simaf | VARCHAR | 255 | YES | - |
| Observación | LONGCHAR | 1073741823 | YES | - |

### A_40_Auditoria de Documentos

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id | COUNTER | 10 | NO | - |
| Fecha_Recepción | DATETIME | 19 | YES | - |
| Und_Mantenimiento | VARCHAR | 255 | YES | - |
| Cantidad | INTEGER | 10 | YES | - |
| Intervención | VARCHAR | 255 | YES | - |
| Fecha_Intervención | DATETIME | 19 | YES | - |
| Fecha_Reingreso | DATETIME | 19 | YES | - |
| FIRMAS | VARCHAR | 255 | YES | - |
| Campos vacios | VARCHAR | 255 | YES | - |
| FECHAS | VARCHAR | 255 | YES | - |
| VALORES | VARCHAR | 255 | YES | - |
| Km | VARCHAR | 255 | YES | - |
| DATOS ANULADOS | VARCHAR | 255 | YES | - |
| Entregada fuera de término | VARCHAR | 255 | YES | - |
| SIMAF Abierto | VARCHAR | 255 | YES | - |
| Observaciones1 | LONGCHAR | 1073741823 | YES | - |
| OBSERVACIONES2 | LONGCHAR | 1073741823 | YES | - |
| RESPONSABLE | VARCHAR | 255 | YES | - |
| Campo1 | VARCHAR | 255 | YES | - |

**Primary Key (inferred):** Id

**Indexes:**
- `PrimaryKey` (Id) UNIQUE

### B_01_Materiales

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Mat_Toshiba | INTEGER | 10 | YES | - |
| NGA | INTEGER | 10 | YES | - |
| Cantidad | INTEGER | 10 | YES | - |

**Indexes:**
- `NGA` (NGA) 

### B_01_Novedades

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id | INTEGER | 10 | YES | - |
| Coche | VARCHAR | 255 | YES | - |
| Novedad | VARCHAR | 255 | YES | - |
| Grupo | VARCHAR | 255 | YES | - |
| Sub_Grupo | VARCHAR | 255 | YES | - |
| Tipo_Novedad | VARCHAR | 255 | YES | - |
| Motivo_Novedad | VARCHAR | 255 | YES | - |
| OT_Resolución | VARCHAR | 255 | YES | - |
| Fecha_Resolución | DATETIME | 19 | YES | - |
| Id_Nov_Mat | COUNTER | 10 | NO | - |

**Indexes:**
- `{1B2038CF-10DA-4D24-B04B-251DB62D2F11}` (Id) 
- `Id` (Id) 
- `Id_Nov_Mat` (Id_Nov_Mat) 

### B_02_Mantenimientos

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Mantenimientos | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |

**Indexes:**
- `{938E4942-8051-46E0-9E79-51ED76CAF0F5}` (Id_Mantenimientos) 
- `Id_Mantenimientos` (Id_Mantenimientos) 

### B_03_Actuaciones_VBC

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_VCB | INTEGER | 10 | YES | - |
| Mantenimiento | VARCHAR | 255 | YES | - |
| Actuaciones | INTEGER | 10 | YES | - |

**Indexes:**
- `Id_VCB` (Id_VCB) UNIQUE
- `{344DD1F1-287C-46DD-86F0-720DBEE5438B}` (Id_VCB) 

### B_04_Compresor_Toshiba

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_CM_Toshiba | INTEGER | 10 | YES | - |
| Compresor | VARCHAR | 255 | YES | - |
| Horas | INTEGER | 10 | YES | - |
| Nivel de Aceite | REAL | 24 | YES | - |
| Perdidas | VARCHAR | 255 | YES | - |
| Agregado_Aceite | REAL | 24 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |

**Indexes:**
- `Id_CM_Toshiba` (Id_CM_Toshiba) UNIQUE
- `{685D729E-25A0-4A37-93B2-E0A4ECB42413}` (Id_CM_Toshiba) 

### B_05_Punta_de_Eje

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Punta_Eje | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Coche | INTEGER | 10 | YES | - |
| Bogie1 | INTEGER | 10 | YES | - |
| Bogie2 | INTEGER | 10 | YES | - |

**Indexes:**
- `{D8BDC930-5E03-40F1-A9F9-DEC206A958B5}` (Id_Punta_Eje) 
- `Id_Punta_Eje` (Id_Punta_Eje) 

### B_06_Pastilla_Freno_Mínima

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Pastilla_Freno | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| N° | REAL | 24 | YES | - |
| Medida_Tomada | INTEGER | 10 | YES | - |
| Cambio | VARCHAR | 255 | YES | - |

### B_07_Placa_Pantógrafo

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Placa_Pantógrafo | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Medida_N1 | REAL | 24 | YES | - |
| Cambio | VARCHAR | 255 | YES | - |
| Motivo | VARCHAR | 255 | YES | - |

### B_08_Organos_Parque

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Organos_Parque_Toshiba | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Organo_Parque | VARCHAR | 50 | YES | - |
| Coche | INTEGER | 10 | YES | - |
| Posición | VARCHAR | 255 | YES | - |
| Número | VARCHAR | 255 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |

**Indexes:**
- `{5E94D6E4-BDF5-41A6-8EC4-74E437B388CB}` (Id_Organos_Parque_Toshiba) 
- `Id_Organos_Parque_Toshiba` (Id_Organos_Parque_Toshiba) 
- `Número` (Número) 

### B_09_Ensayo_Ultrasonido

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_US_Toshiba | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Motivo | VARCHAR | 255 | YES | - |
| Realizado_por | VARCHAR | 255 | YES | - |
| Completo | VARCHAR | 255 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |

**Indexes:**
- `Id_US_Toshiba` (Id_US_Toshiba) UNIQUE
- `{0ADEAC29-18B8-4A91-AE3F-BC4253F2C485}` (Id_US_Toshiba) 

### B_10_Rodados

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Rodados | INTEGER | 10 | YES | - |
| R7_Motriz_Cab | INTEGER | 10 | YES | - |
| R3_Remolcado | INTEGER | 10 | YES | - |
| Rodado_Acople | INTEGER | 10 | YES | - |
| Motivo | VARCHAR | 255 | YES | - |
| Estado | VARCHAR | 255 | YES | - |

**Indexes:**
- `Id_Rodados` (Id_Rodados) UNIQUE
- `{6D79685F-48CC-4D39-AB27-9CC3B9AB4FB1}` (Id_Rodados) 

### B_19_Altura_Acople

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Acople_Perno | COUNTER | 10 | NO | - |
| Fecha_Inspección | DATETIME | 19 | YES | - |
| Coche1-A | INTEGER | 10 | YES | - |
| Coche1-B | INTEGER | 10 | YES | - |
| Dif_Coche_1-2 | INTEGER | 10 | YES | - |
| Coche2-A | INTEGER | 10 | YES | - |
| Coche2-B | INTEGER | 10 | YES | - |
| Dif_Coche_2-3 | INTEGER | 10 | YES | - |
| Coche3-A | INTEGER | 10 | YES | - |
| Coche3-B | INTEGER | 10 | YES | - |
| Dif_Coche_3-4 | INTEGER | 10 | YES | - |
| Coche4-A | INTEGER | 10 | YES | - |
| Coche4-B | INTEGER | 10 | YES | - |
| Dif_Coche_4-5 | INTEGER | 10 | YES | - |
| Coche5-A | INTEGER | 10 | YES | - |
| Coche5-B | INTEGER | 10 | YES | - |
| Dif_Coche_5-6 | INTEGER | 10 | YES | - |
| Coche6-A | INTEGER | 10 | YES | - |
| Coche6-B | INTEGER | 10 | YES | - |
| Dif_Coche_6-7 | INTEGER | 10 | YES | - |
| Coche7-A | INTEGER | 10 | YES | - |
| Coche7-B | INTEGER | 10 | YES | - |
| Formación | VARCHAR | 255 | YES | - |
| CabinaB | VARCHAR | 255 | YES | - |
| CabinaA | VARCHAR | 255 | YES | - |
| Coche1 | INTEGER | 10 | YES | - |
| Coche2 | INTEGER | 10 | YES | - |
| Coche3 | INTEGER | 10 | YES | - |
| Coche4 | INTEGER | 10 | YES | - |
| Coche5 | INTEGER | 10 | YES | - |
| Coche6 | INTEGER | 10 | YES | - |
| Coche7 | INTEGER | 10 | YES | - |
| NarizA-B | INTEGER | 10 | YES | - |
| NarizB-B | INTEGER | 10 | YES | - |
| NarizA-A | VARCHAR | 255 | YES | - |
| NarizB-A | VARCHAR | 255 | YES | - |
| Dif_Nariz | DOUBLE | 53 | YES | - |

**Primary Key (inferred):** Id_Acople_Perno

**Indexes:**
- `PrimaryKey` (Id_Acople_Perno) UNIQUE

### B_20_Escobillas_MT

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Escobillas | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Coche | INTEGER | 10 | YES | - |
| MT1_Número | VARCHAR | 255 | YES | - |
| Escobilla1_MT1 | INTEGER | 10 | YES | - |
| Escobilla2_MT1 | INTEGER | 10 | YES | - |
| Escobilla3_MT1 | INTEGER | 10 | YES | - |
| Escobilla4_MT1 | INTEGER | 10 | YES | - |
| Escobilla5_MT1 | INTEGER | 10 | YES | - |
| Escobilla6_MT1 | INTEGER | 10 | YES | - |
| Escobilla7_MT1 | INTEGER | 10 | YES | - |
| Escobilla8_MT1 | INTEGER | 10 | YES | - |
| N_Precinto_Tapa_Superior_MT1 | INTEGER | 10 | YES | - |
| N_Precinto_Tapa_Inferior_MT1 | INTEGER | 10 | YES | - |
| MT2_Número | VARCHAR | 255 | YES | - |
| Escobilla1_MT2 | INTEGER | 10 | YES | - |
| Escobilla2_MT2 | INTEGER | 10 | YES | - |
| Escobilla3_MT2 | INTEGER | 10 | YES | - |
| Escobilla4_MT2 | INTEGER | 10 | YES | - |
| Escobilla5_MT2 | INTEGER | 10 | YES | - |
| Escobilla6_MT2 | INTEGER | 10 | YES | - |
| Escobilla7_MT2 | INTEGER | 10 | YES | - |
| Escobilla8_MT2 | INTEGER | 10 | YES | - |
| N_Precinto_Tapa_Superior_MT2 | INTEGER | 10 | YES | - |
| N_Precinto_Tapa_Inferior_MT2 | INTEGER | 10 | YES | - |
| MT3_Número | VARCHAR | 255 | YES | - |
| Escobilla1_MT3 | INTEGER | 10 | YES | - |
| Escobilla2_MT3 | INTEGER | 10 | YES | - |
| Escobilla3_MT3 | INTEGER | 10 | YES | - |
| Escobilla4_MT3 | INTEGER | 10 | YES | - |
| Escobilla5_MT3 | INTEGER | 10 | YES | - |
| Escobilla6_MT3 | INTEGER | 10 | YES | - |
| Escobilla7_MT3 | INTEGER | 10 | YES | - |
| Escobilla8_MT3 | INTEGER | 10 | YES | - |
| N_Precinto_Tapa_Superior_MT3 | INTEGER | 10 | YES | - |
| N_Precinto_Tapa_Inferior_MT3 | INTEGER | 10 | YES | - |
| MT4_Número | VARCHAR | 255 | YES | - |
| Escobilla1_MT4 | INTEGER | 10 | YES | - |
| Escobilla2_MT | INTEGER | 10 | YES | - |
| Escobilla3_MT4 | INTEGER | 10 | YES | - |
| Escobilla4_MT4 | INTEGER | 10 | YES | - |
| Escobilla5_MT4 | INTEGER | 10 | YES | - |
| Escobilla6_MT4 | INTEGER | 10 | YES | - |
| Escobilla7_MT4 | INTEGER | 10 | YES | - |
| Escobilla8_MT4 | INTEGER | 10 | YES | - |
| N_Precinto_Tapa_Superior_MT4 | INTEGER | 10 | YES | - |
| N_Precinto_Tapa_Inferior_MT4 | INTEGER | 10 | YES | - |

**Indexes:**
- `Id_Escobillas` (Id_Escobillas) 

### B_21_Medición_Alturas

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Medición_Alturas | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Coche | VARCHAR | 255 | YES | - |
| R1 | VARCHAR | 255 | YES | - |
| R2 | VARCHAR | 255 | YES | - |
| R3 | VARCHAR | 255 | YES | - |
| R4 | VARCHAR | 255 | YES | - |
| Susp_1-3 | VARCHAR | 255 | YES | - |
| Susp_2-4 | VARCHAR | 255 | YES | - |
| R5 | VARCHAR | 255 | YES | - |
| R6 | VARCHAR | 255 | YES | - |
| R7 | VARCHAR | 255 | YES | - |
| R8 | VARCHAR | 255 | YES | - |
| Susp_5-7 | VARCHAR | 255 | YES | - |
| Susp_6-8 | VARCHAR | 255 | YES | - |

### B_22_Escobillas_MA

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Escobillas_MA | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Cantidad | INTEGER | 10 | YES | - |

**Indexes:**
- `Id_Escobillas_MA` (Id_Escobillas_MA) UNIQUE

### B_23_Medición_Crítica

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Med_Crítica | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Coche | INTEGER | 10 | YES | - |
| Rueda | VARCHAR | 255 | YES | - |
| QR | REAL | 24 | YES | - |
| Ancho | REAL | 24 | YES | - |

### C_01_Materiales

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Mat_CSR | INTEGER | 10 | YES | - |
| NGA | INTEGER | 10 | YES | - |
| Cantidad | INTEGER | 10 | YES | - |

**Indexes:**
- `NGA` (NGA) 

### C_01_Novedades

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Novedades_CSR | INTEGER | 10 | YES | - |
| Coche | INTEGER | 10 | YES | - |
| Novedad | VARCHAR | 255 | YES | - |
| Grupo | VARCHAR | 255 | YES | - |
| Sub_Grupo | VARCHAR | 255 | YES | - |
| Tipo_Novedad | VARCHAR | 255 | YES | - |
| Motivo_Novedad | VARCHAR | 255 | YES | - |
| OT_Resolución | VARCHAR | 255 | YES | - |
| Fecha_Resolución | DATETIME | 19 | YES | - |
| Id_Nov_Mat | COUNTER | 10 | NO | - |

**Indexes:**
- `{D3FF36EA-F4B0-468E-9EF5-F2E350F5B60D}` (Id_Novedades_CSR) 
- `Id_Nov_Mat` (Id_Nov_Mat) 
- `Id_Novedades_CSR` (Id_Novedades_CSR) 

### C_02_Mantenimientos

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Mantenimientos | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |
| Km_Acumulado | INTEGER | 10 | YES | - |

**Indexes:**
- `{01A59766-6974-46FC-B805-EB0E4513ED97}` (Id_Mantenimientos) 
- `Id_Mantenimientos` (Id_Mantenimientos) 

### C_03_Actuaciones_VCB

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_VCB | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Actuaciones | VARCHAR | 255 | YES | - |

**Indexes:**
- `Id_VCB` (Id_VCB) UNIQUE
- `{68F6B6B6-0C3E-4B4E-B843-C9FC0AC7B406}` (Id_VCB) 

### C_04_Compresor_CSR

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_CM_CSR | INTEGER | 10 | YES | - |
| Compresor | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Horas | INTEGER | 10 | YES | - |
| Starts | INTEGER | 10 | YES | - |
| Nivel | REAL | 24 | YES | - |
| Perdidas | VARCHAR | 255 | YES | - |
| Agregado_Aceite | REAL | 24 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |

**Indexes:**
- `Id_CM_CSR` (Id_CM_CSR) UNIQUE
- `{5594ADFF-A7A8-4661-AF24-AB102DBCD4B6}` (Id_CM_CSR) 

### C_06_Pastilla_Freno_Mínima

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Pastilla_Freno | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Coche | INTEGER | 10 | YES | - |
| Rueda | INTEGER | 10 | YES | - |
| Medida_Tomada | REAL | 24 | YES | - |

### C_07_Placa_Pantógrafo

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Placa_Pantógrafo | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Medida_N1 | REAL | 24 | YES | - |
| Medida_N2 | REAL | 24 | YES | - |
| MC1 | VARCHAR | 255 | YES | - |
| MC2 | VARCHAR | 255 | YES | - |
| Cambio_MC1 | VARCHAR | 255 | YES | - |
| Cambio_MC2 | VARCHAR | 255 | YES | - |
| Motivo_MC1 | VARCHAR | 255 | YES | - |
| Motivo_MC2 | VARCHAR | 255 | YES | - |

### C_08_Organos_Parque

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Organos_Parque_CSR | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Organo_Parque | VARCHAR | 255 | YES | - |
| Coche | INTEGER | 10 | YES | - |
| Posición | VARCHAR | 255 | YES | - |
| Número | INTEGER | 10 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |
| Estado | VARCHAR | 255 | YES | - |

**Indexes:**
- `{389A81A8-E05E-4C6C-ACF3-70B3DCC19B76}` (Id_Organos_Parque_CSR) 
- `Id_Organos_Parque_CSR` (Id_Organos_Parque_CSR) 
- `Número` (Número) 

### C_09_Ensayo_Ultrasonido

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_US_CSR | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Motivo | VARCHAR | 255 | YES | - |
| Realizado_por | VARCHAR | 255 | YES | - |
| Completo | VARCHAR | 255 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |

**Indexes:**
- `Id_US_CSR` (Id_US_CSR) UNIQUE
- `{9D564187-A896-4702-BEB9-1BEAE300BDDF}` (Id_US_CSR) 

### C_10_Rodados

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Rodados | INTEGER | 10 | YES | - |
| R2_Motriz_Cab | INTEGER | 10 | YES | - |
| Rodado_Acople | INTEGER | 10 | YES | - |
| Motivo | VARCHAR | 255 | YES | - |
| Estado | VARCHAR | 255 | YES | - |

**Indexes:**
- `Id_Rodados` (Id_Rodados) UNIQUE
- `{D3081FB8-422D-4BEB-A5CA-3B8C040C52D9}` (Id_Rodados) 

### C_11_ATS

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_ATS | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Diámetro_Cargado | INTEGER | 10 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |

**Indexes:**
- `Id_ATS` (Id_ATS) UNIQUE
- `{FEA7BC98-2676-47F2-9728-1A46C2FE8611}` (Id_ATS) 

### C_16_Acople_Automático

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Acople_Automático | INTEGER | 10 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| MC1 | REAL | 24 | YES | - |
| MC2 | REAL | 24 | YES | - |

### C_18_Suplementos

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Suplemento | INTEGER | 10 | YES | - |
| Coche | VARCHAR | 255 | YES | - |
| Bogie1 | VARCHAR | 255 | YES | - |
| Bogie2 | VARCHAR | 255 | YES | - |
| Suplemento | INTEGER | 10 | YES | - |

**Indexes:**
- `{9DE11ECD-EEAE-479F-AE6B-7013AE618912}` (Id_Suplemento) 
- `Id_Suplemento` (Id_Suplemento) 

### Errores de pegado

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| Id_Mantenimientos | DOUBLE | 53 | YES | - |
| Tarea | VARCHAR | 255 | YES | - |
| Observaciones | VARCHAR | 255 | YES | - |
| Km_Acumulado | DOUBLE | 53 | YES | - |

### Usuarios

| Column | Type | Size | Nullable | Default |
|--------|------|------|----------|--------|
| ID_Usuario | COUNTER | 10 | NO | - |
| Nombre_Usuario | LONGCHAR | 1073741823 | YES | - |
| Usuario | VARCHAR | 255 | YES | - |
| Pass | VARCHAR | 255 | YES | - |
| Admin | BIT | 1 | NO | - |
| Programación _Interno | BIT | 1 | NO | - |
| Datos | BIT | 1 | NO | - |
| Mostrar_Cinta_Opciones | BIT | 1 | NO | - |
| Activar_Shift | BIT | 1 | NO | - |
| UsuariosGeneral | BIT | 1 | NO | - |
| Programación | BIT | 1 | NO | - |

**Primary Key (inferred):** ID_Usuario

**Indexes:**
- `PrimaryKey` (ID_Usuario) UNIQUE
- `ID_Usuario` (ID_Usuario) 

## Queries/Views

- **3_NUM_un_NSAP** (VIEW)
- **A_00_Kilometraje_Máx** (VIEW)
- **A_14_Cambio_Coches_Último1** (VIEW)
- **A_14_Cambio_Coches_Último2** (VIEW)
- **A_14_Cambio_Módulos_Último1** (VIEW)
- **A_14_Cambio_Módulos_Último2** (VIEW)
- **A_14_Estado_Formaciones_Consulta** (VIEW)

