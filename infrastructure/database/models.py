"""
Django ORM models for railway fleet persistence.

This module contains two families of models:

1. **Domain models** (EmuModel, CoachModel, FormationModel, EmuConfigurationModel)
   – map domain entities to the database for persistence.  The domain entities
   in ``core/domain/`` remain pure Python without Django dependencies.

2. **Staging models** (``Stg*``)
   – raw mirrors of the legacy Access tables.  They are populated by the
   ``sync_access`` management command and used as the source-of-truth for
   projections and dashboard queries, replacing direct ODBC access.

Naming convention:
- Domain models end with ``Model`` suffix
- Staging models start with ``Stg`` prefix
- Fields use verbose_name in Spanish for Django Admin
"""

import uuid

from django.db import models


class EmuConfigurationModel(models.Model):
    """
    Persistent storage for EMU coach configurations.

    Defines valid coach compositions for different EMU types.
    Example: CSR-4 = [MC1, R1, R2, MC2]
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre",
        help_text="Nombre de la configuración (ej: CSR-4, Toshiba-3)",
    )
    manufacturer = models.CharField(
        max_length=100,
        verbose_name="Fabricante",
        help_text="CSR Zhuzhou o Toshiba",
    )
    coach_sequence = models.JSONField(
        verbose_name="Secuencia de coches",
        help_text="Lista ordenada de tipos de coche (ej: ['mc1', 'r1', 'r2', 'mc2'])",
    )
    min_coaches = models.PositiveSmallIntegerField(
        verbose_name="Mínimo de coches",
    )
    max_coaches = models.PositiveSmallIntegerField(
        verbose_name="Máximo de coches",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        db_table = "fleet_emu_configuration"
        verbose_name = "Configuración de EMU"
        verbose_name_plural = "Configuraciones de EMU"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.manufacturer})"


class EmuModel(models.Model):
    """
    Persistent storage for Electric Multiple Units (EMU).

    An EMU is a trainset composed of multiple coaches that operates
    as a single unit. Also known as "Módulo" in legacy systems.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    unit_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de módulo",
        help_text="Identificador del módulo (ej: M01, T15)",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descripción",
    )
    manufacturer = models.CharField(
        max_length=100,
        verbose_name="Fabricante",
        help_text="CSR Zhuzhou o Toshiba",
    )
    manufacture_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de fabricación",
    )
    commissioning_date = models.DateField(
        verbose_name="Fecha de puesta en servicio",
    )
    line = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Línea",
        help_text="Línea ferroviaria (ej: LR = Línea Roca)",
    )
    voltage = models.PositiveIntegerField(
        default=25000,
        verbose_name="Voltaje (V)",
        help_text="Voltaje de operación en voltios",
    )
    max_speed = models.PositiveSmallIntegerField(
        default=120,
        verbose_name="Velocidad máxima (km/h)",
    )
    total_passenger_capacity = models.PositiveIntegerField(
        default=0,
        verbose_name="Capacidad total de pasajeros",
    )
    configuration = models.ForeignKey(
        EmuConfigurationModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emus",
        verbose_name="Configuración",
    )
    # Legacy ID for mapping to Access database
    legacy_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        unique=True,
        verbose_name="ID legacy (Access)",
        help_text="Id_Módulos de la base Access",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        db_table = "fleet_emu"
        verbose_name = "EMU (Módulo)"
        verbose_name_plural = "EMUs (Módulos)"
        ordering = ["unit_number"]

    def __str__(self) -> str:
        return self.unit_number


class CoachModel(models.Model):
    """
    Persistent storage for individual railway coaches.

    A coach is a single car within an EMU. Can be motor (with traction)
    or trailer (without traction).
    """

    COACH_TYPE_CHOICES = [
        # CSR types
        ("mc1", "MC1 - Motriz Cabecera 1"),
        ("mc2", "MC2 - Motriz Cabecera 2"),
        ("r1", "R1 - Remolque"),
        ("r2", "R2 - Remolque Prima"),
        # Toshiba types
        ("m", "M - Motriz"),
        ("r", "R - Remolque"),
        ("rp", "RP - Remolque Prima"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    unit_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de coche",
        help_text="Número identificador del coche (ej: 5001, 4029)",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descripción",
    )
    manufacturer = models.CharField(
        max_length=100,
        verbose_name="Fabricante",
    )
    manufacture_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de fabricación",
    )
    commissioning_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de puesta en servicio",
    )
    line = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Línea",
    )
    coach_type = models.CharField(
        max_length=10,
        choices=COACH_TYPE_CHOICES,
        verbose_name="Tipo de coche",
    )
    voltage = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Voltaje (V)",
        help_text="Solo para coches motrices",
    )
    has_pantograph = models.BooleanField(
        default=False,
        verbose_name="Tiene pantógrafo",
    )
    has_cabin = models.BooleanField(
        default=False,
        verbose_name="Tiene cabina",
    )
    place = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Posición en EMU",
        help_text="Posición del coche dentro del módulo (1..N)",
    )
    seating_capacity = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Capacidad de asientos",
    )
    emu = models.ForeignKey(
        EmuModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coaches",
        verbose_name="EMU (Módulo)",
    )
    # Legacy ID for mapping to Access database
    legacy_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID legacy (Access)",
        help_text="Id_Coches de la base Access",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        db_table = "fleet_coach"
        verbose_name = "Coche"
        verbose_name_plural = "Coches"
        ordering = ["emu", "place"]

    def __str__(self) -> str:
        return f"{self.unit_number} ({self.get_coach_type_display()})"


class FormationModel(models.Model):
    """
    Persistent storage for train formations.

    A formation is one or more EMUs operating together as a complete train.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    f_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="ID de formación",
        help_text="Identificador de la formación (ej: F120)",
    )
    unit_number = models.CharField(
        max_length=20,
        verbose_name="Número de formación",
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descripción",
    )
    manufacturer = models.CharField(
        max_length=100,
        verbose_name="Fabricante",
    )
    commissioning_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de puesta en servicio",
    )
    line = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Línea",
    )
    route = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Recorrido",
        help_text="Ej: Constitución - La Plata",
    )
    emus = models.ManyToManyField(
        EmuModel,
        related_name="formations",
        blank=True,
        verbose_name="EMUs",
    )
    # Legacy ID for mapping to Access database
    legacy_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID legacy (Access)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        db_table = "fleet_formation"
        verbose_name = "Formación"
        verbose_name_plural = "Formaciones"
        ordering = ["f_id"]

    def __str__(self) -> str:
        return self.f_id

    def get_total_coaches(self) -> int:
        """Return total number of coaches across all EMUs."""
        return sum(emu.coaches.count() for emu in self.emus.all())


# =============================================================================
# Staging models – raw mirrors of Access tables
# =============================================================================
# These tables are populated by the ``sync_access`` management command
# and should never be edited manually.  They intentionally preserve the
# legacy column semantics (nullable, no foreign-key constraints) so that
# the ETL can bulk-upsert without worrying about ordering or integrity.


class StgModulo(models.Model):
    """
    Raw mirror of ``A_00_Módulos`` – module master data.

    The ``access_id`` field corresponds to ``Id_Módulos`` in Access and is the
    primary key used as FK by kilometraje and OT_Simaf tables.
    """

    access_id = models.IntegerField(
        unique=True,
        verbose_name="Id_Módulos (Access)",
    )
    nombre = models.CharField(
        max_length=20,
        verbose_name="Módulos",
        help_text="Ej: M01, T06",
    )
    clase_vehiculo = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Clase_Vehículos (FK Access)",
    )
    tipo_mr = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Tipo_MR",
    )
    marca_mr = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Marca_MR",
    )
    synced_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última sincronización",
    )

    class Meta:
        db_table = "stg_modulo"
        verbose_name = "Staging: Módulo"
        verbose_name_plural = "Staging: Módulos"
        ordering = ["nombre"]

    def __str__(self) -> str:
        return f"{self.nombre} (access_id={self.access_id})"


class StgKilometraje(models.Model):
    """
    Raw mirror of ``A_00_Kilometrajes`` – daily odometer readings per module.

    ``modulo_access_id`` is the numeric FK (``[Módulo]``) to ``A_00_Módulos.Id_Módulos``.
    The natural incremental key is ``(modulo_access_id, fecha)``.
    """

    modulo_access_id = models.IntegerField(
        verbose_name="Módulo (FK Access)",
        db_index=True,
    )
    fecha = models.DateField(
        verbose_name="Fecha de lectura",
    )
    kilometraje = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Kilometraje acumulado",
    )
    synced_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última sincronización",
    )

    class Meta:
        db_table = "stg_kilometraje"
        verbose_name = "Staging: Kilometraje"
        verbose_name_plural = "Staging: Kilometrajes"
        constraints = [
            models.UniqueConstraint(
                fields=["modulo_access_id", "fecha"],
                name="uq_stg_km_modulo_fecha",
            ),
        ]
        indexes = [
            models.Index(fields=["fecha"], name="ix_stg_km_fecha"),
            models.Index(
                fields=["modulo_access_id", "-fecha"],
                name="ix_stg_km_modulo_fecha_desc",
            ),
        ]
        ordering = ["-fecha"]

    def __str__(self) -> str:
        return f"Mod {self.modulo_access_id} @ {self.fecha}: {self.kilometraje}"


class StgOtSimaf(models.Model):
    """
    Raw mirror of ``A_00_OT_Simaf`` – maintenance work orders (OTs).

    Each row represents a maintenance event (IQ, AN1-6, BA1-3, RB, RG, …).
    ``modulo_access_id`` is the FK to ``A_00_Módulos.Id_Módulos``.

    The natural key for upsert is ``(modulo_access_id, tarea, fecha_fin)``,
    though duplicates with identical dates and tasks can exist in Access.
    We use ``access_row_hash`` as a dedup helper (MD5 of key fields).
    """

    modulo_access_id = models.IntegerField(
        verbose_name="Módulo (FK Access)",
        db_index=True,
    )
    tipo_tarea = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Tipo_Tarea",
    )
    tarea = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Tarea",
        help_text="Código de tarea: IQ, AN1, BA2, RB, RG, MEN, etc.",
    )
    km = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="Km al momento de la OT",
    )
    fecha_inicio = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha inicio de la OT",
    )
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha fin de la OT",
        db_index=True,
    )
    ot_simaf = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="OT SIMAF",
        help_text="Número de OT en sistema SIMAF",
    )
    access_row_hash = models.CharField(
        max_length=32,
        blank=True,
        default="",
        verbose_name="Hash de fila (dedup)",
        db_index=True,
    )
    synced_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última sincronización",
    )

    class Meta:
        db_table = "stg_ot_simaf"
        verbose_name = "Staging: OT SIMAF"
        verbose_name_plural = "Staging: OTs SIMAF"
        indexes = [
            models.Index(
                fields=["modulo_access_id", "-fecha_fin"],
                name="ix_stg_ot_modulo_fecha_desc",
            ),
            models.Index(
                fields=["tarea", "-fecha_fin"],
                name="ix_stg_ot_tarea_fecha_desc",
            ),
        ]
        ordering = ["-fecha_fin"]

    def __str__(self) -> str:
        return f"Mod {self.modulo_access_id} | {self.tarea} @ {self.fecha_fin}"


class StgCoche(models.Model):
    """
    Raw mirror of ``A_00_Coches`` – individual coach master data.
    """

    coche = models.IntegerField(
        unique=True,
        verbose_name="Número de coche",
    )
    posicion = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Posición",
    )
    ubicacion = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name="Ubicación",
        help_text="Tipo lógico: MC1, MC2, R1, R2, MC, R, RP",
    )
    descripcion = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Descripción",
    )
    synced_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última sincronización",
    )

    class Meta:
        db_table = "stg_coche"
        verbose_name = "Staging: Coche"
        verbose_name_plural = "Staging: Coches"
        ordering = ["coche"]

    def __str__(self) -> str:
        return f"Coche {self.coche} ({self.ubicacion})"


class StgFormacionModulo(models.Model):
    """
    Raw mirror of ``A_14_Estado_Formaciones_Consulta`` – module-to-coach mapping.

    Represents which coaches belong to each module at a given point in time.
    """

    modulo_access_id = models.IntegerField(
        verbose_name="Módulo (FK Access)",
        db_index=True,
    )
    coche = models.IntegerField(
        verbose_name="Número de coche",
    )
    synced_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última sincronización",
    )

    class Meta:
        db_table = "stg_formacion_modulo"
        verbose_name = "Staging: Formación-Módulo"
        verbose_name_plural = "Staging: Formaciones-Módulos"
        constraints = [
            models.UniqueConstraint(
                fields=["modulo_access_id", "coche"],
                name="uq_stg_form_modulo_coche",
            ),
        ]

    def __str__(self) -> str:
        return f"Mod {self.modulo_access_id} -> Coche {self.coche}"


# =============================================================================
# Sync log – tracks sync_access runs
# =============================================================================


class SyncLog(models.Model):
    """
    Tracks each execution of the ``sync_access`` management command.

    Used by the web UI to display the last sync timestamp and to
    provide feedback while a sync is running in background.
    """

    STATUS_CHOICES = [
        ("running", "En ejecución"),
        ("success", "Completado"),
        ("failed", "Fallido"),
    ]

    started_at = models.DateTimeField(
        verbose_name="Inicio",
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="running",
        verbose_name="Estado",
    )
    tables_synced = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Tablas sincronizadas",
        help_text='{"modulos": 114, "kilometrajes": 191182, ...}',
    )
    log_output = models.TextField(
        blank=True,
        default="",
        verbose_name="Salida del log",
    )
    error_message = models.TextField(
        blank=True,
        default="",
        verbose_name="Mensaje de error",
    )

    class Meta:
        db_table = "sync_log"
        verbose_name = "Log de sincronización"
        verbose_name_plural = "Logs de sincronización"
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"Sync {self.started_at:%Y-%m-%d %H:%M} [{self.status}]"

    @property
    def duration_seconds(self) -> float | None:
        """Elapsed time in seconds, or None if still running."""
        if self.finished_at and self.started_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None
