"""
Django ORM models for railway fleet persistence.

These models map domain entities to the database for persistence.
The domain entities in core/domain/ remain pure Python without
Django dependencies.

Naming convention:
- Models end with 'Model' suffix to distinguish from domain entities
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
