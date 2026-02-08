"""
Repository implementations for fleet domain entities.

Repositories provide an abstraction layer between domain entities
and Django ORM models, isolating persistence logic.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from core.domain.entities.coach import Coach
from core.domain.entities.emu import EMU
from core.domain.entities.emu_configuration import EmuConfiguration
from core.domain.entities.formation import Formation
from core.domain.value_objects.coach_type import CoachType

from .models import CoachModel, EmuConfigurationModel, EmuModel, FormationModel


class EmuConfigurationRepository:
    """Repository for EmuConfiguration domain entities."""

    @staticmethod
    def model_to_entity(model: EmuConfigurationModel) -> EmuConfiguration:
        """Convert Django model to domain entity."""
        # Convert list to tuple for immutability
        coach_sequence = tuple(
            CoachType(ct) for ct in model.coach_sequence
        )
        return EmuConfiguration(
            id=model.id,
            name=model.name,
            manufacturer=model.manufacturer,
            coach_sequence=coach_sequence,
            min_coaches=model.min_coaches,
            max_coaches=model.max_coaches,
        )

    @staticmethod
    def entity_to_model_data(entity: EmuConfiguration) -> dict:
        """Convert domain entity to model field dict (for create/update)."""
        return {
            "id": entity.id,
            "name": entity.name,
            "manufacturer": entity.manufacturer,
            "coach_sequence": [ct.value for ct in entity.coach_sequence],
            "min_coaches": entity.min_coaches,
            "max_coaches": entity.max_coaches,
        }

    def get_by_id(self, config_id: UUID) -> Optional[EmuConfiguration]:
        """Get configuration by ID."""
        try:
            model = EmuConfigurationModel.objects.get(id=config_id)
            return self.model_to_entity(model)
        except EmuConfigurationModel.DoesNotExist:
            return None

    def get_by_name(self, name: str) -> Optional[EmuConfiguration]:
        """Get configuration by name."""
        try:
            model = EmuConfigurationModel.objects.get(name=name)
            return self.model_to_entity(model)
        except EmuConfigurationModel.DoesNotExist:
            return None

    def save(self, entity: EmuConfiguration) -> EmuConfiguration:
        """Save or update a configuration."""
        data = self.entity_to_model_data(entity)
        model, _ = EmuConfigurationModel.objects.update_or_create(
            id=entity.id,
            defaults=data,
        )
        return self.model_to_entity(model)

    def get_all(self) -> list[EmuConfiguration]:
        """Get all configurations."""
        return [
            self.model_to_entity(m)
            for m in EmuConfigurationModel.objects.all()
        ]


class CoachRepository:
    """Repository for Coach domain entities."""

    @staticmethod
    def model_to_entity(model: CoachModel) -> Coach:
        """Convert Django model to domain entity."""
        return Coach(
            id=model.id,
            unit_number=model.unit_number,
            description=model.description,
            manufacturer=model.manufacturer,
            manufacture_date=model.manufacture_date,
            commissioning_date=model.commissioning_date or date.today(),
            line=model.line,
            created_at=model.created_at or datetime.now(),
            updated_at=model.updated_at or datetime.now(),
            coach_type=CoachType(model.coach_type),
            voltage=model.voltage,
            has_pantograph=model.has_pantograph,
            has_cabin=model.has_cabin,
            place=model.place,
            seating_capacity=model.seating_capacity,
            emu_id=model.emu.id if model.emu else None,
        )

    @staticmethod
    def entity_to_model_data(entity: Coach) -> dict:
        """Convert domain entity to model field dict."""
        return {
            "id": entity.id,
            "unit_number": entity.unit_number,
            "description": entity.description,
            "manufacturer": entity.manufacturer,
            "manufacture_date": entity.manufacture_date,
            "commissioning_date": entity.commissioning_date,
            "line": entity.line,
            "coach_type": entity.coach_type.value,
            "voltage": entity.voltage,
            "has_pantograph": entity.has_pantograph,
            "has_cabin": entity.has_cabin,
            "place": entity.place,
            "seating_capacity": entity.seating_capacity,
        }

    def get_by_id(self, coach_id: UUID) -> Optional[Coach]:
        """Get coach by ID."""
        try:
            model = CoachModel.objects.select_related("emu").get(id=coach_id)
            return self.model_to_entity(model)
        except CoachModel.DoesNotExist:
            return None

    def get_by_unit_number(self, unit_number: str) -> Optional[Coach]:
        """Get coach by unit number."""
        try:
            model = CoachModel.objects.select_related("emu").get(
                unit_number=unit_number
            )
            return self.model_to_entity(model)
        except CoachModel.DoesNotExist:
            return None

    def get_by_emu(self, emu_id: UUID) -> list[Coach]:
        """Get all coaches for an EMU."""
        models = CoachModel.objects.filter(emu_id=emu_id).order_by("place")
        return [self.model_to_entity(m) for m in models]

    def save(self, entity: Coach, emu_model: Optional[EmuModel] = None) -> Coach:
        """Save or update a coach."""
        data = self.entity_to_model_data(entity)
        if emu_model:
            data["emu"] = emu_model
        model, _ = CoachModel.objects.update_or_create(
            id=entity.id,
            defaults=data,
        )
        return self.model_to_entity(model)


class EmuRepository:
    """Repository for EMU domain entities."""

    def __init__(self):
        self.coach_repo = CoachRepository()

    def model_to_entity(self, model: EmuModel, include_coaches: bool = True) -> EMU:
        """Convert Django model to domain entity."""
        coaches = []
        if include_coaches:
            coach_models = model.coaches.all().order_by("place")
            coaches = [
                self.coach_repo.model_to_entity(cm)
                for cm in coach_models
            ]

        return EMU(
            id=model.id,
            unit_number=model.unit_number,
            description=model.description,
            manufacturer=model.manufacturer,
            manufacture_date=model.manufacture_date,
            commissioning_date=model.commissioning_date,
            line=model.line,
            created_at=model.created_at or datetime.now(),
            updated_at=model.updated_at or datetime.now(),
            voltage=model.voltage,
            max_speed=model.max_speed,
            total_passenger_capacity=model.total_passenger_capacity,
            coaches=coaches,
            formation_id=None,  # Will be set if needed
            configuration_id=model.configuration.id if model.configuration else None,
        )

    @staticmethod
    def entity_to_model_data(entity: EMU) -> dict:
        """Convert domain entity to model field dict."""
        return {
            "id": entity.id,
            "unit_number": entity.unit_number,
            "description": entity.description,
            "manufacturer": entity.manufacturer,
            "manufacture_date": entity.manufacture_date,
            "commissioning_date": entity.commissioning_date,
            "line": entity.line,
            "voltage": entity.voltage,
            "max_speed": entity.max_speed,
            "total_passenger_capacity": entity.total_passenger_capacity,
        }

    def get_by_id(self, emu_id: UUID) -> Optional[EMU]:
        """Get EMU by ID."""
        try:
            model = EmuModel.objects.prefetch_related("coaches").get(id=emu_id)
            return self.model_to_entity(model)
        except EmuModel.DoesNotExist:
            return None

    def get_by_unit_number(self, unit_number: str) -> Optional[EMU]:
        """Get EMU by unit number."""
        try:
            model = EmuModel.objects.prefetch_related("coaches").get(
                unit_number=unit_number
            )
            return self.model_to_entity(model)
        except EmuModel.DoesNotExist:
            return None

    def get_by_legacy_id(self, legacy_id: int) -> Optional[EMU]:
        """Get EMU by legacy Access database ID."""
        try:
            model = EmuModel.objects.prefetch_related("coaches").get(
                legacy_id=legacy_id
            )
            return self.model_to_entity(model)
        except EmuModel.DoesNotExist:
            return None

    def get_all(self) -> list[EMU]:
        """Get all EMUs."""
        models = EmuModel.objects.prefetch_related("coaches").all()
        return [self.model_to_entity(m) for m in models]

    def save(self, entity: EMU) -> EMU:
        """Save or update an EMU."""
        data = self.entity_to_model_data(entity)
        model, _ = EmuModel.objects.update_or_create(
            id=entity.id,
            defaults=data,
        )
        return self.model_to_entity(model)

    def count(self) -> int:
        """Return total number of EMUs."""
        return EmuModel.objects.count()


class FormationRepository:
    """Repository for Formation domain entities."""

    def __init__(self):
        self.emu_repo = EmuRepository()

    def model_to_entity(self, model: FormationModel) -> Formation:
        """Convert Django model to domain entity."""
        emus = [
            self.emu_repo.model_to_entity(em)
            for em in model.emus.prefetch_related("coaches").all()
        ]

        return Formation(
            id=model.id,
            unit_number=model.unit_number,
            description=model.description,
            manufacturer=model.manufacturer,
            manufacture_date=None,
            commissioning_date=model.commissioning_date or date.today(),
            line=model.line,
            created_at=model.created_at or datetime.now(),
            updated_at=model.updated_at or datetime.now(),
            f_id=model.f_id,
            emus=emus,
            route=model.route,
        )

    def get_by_id(self, formation_id: UUID) -> Optional[Formation]:
        """Get formation by ID."""
        try:
            model = FormationModel.objects.prefetch_related(
                "emus__coaches"
            ).get(id=formation_id)
            return self.model_to_entity(model)
        except FormationModel.DoesNotExist:
            return None

    def get_by_f_id(self, f_id: str) -> Optional[Formation]:
        """Get formation by F_ID."""
        try:
            model = FormationModel.objects.prefetch_related(
                "emus__coaches"
            ).get(f_id=f_id)
            return self.model_to_entity(model)
        except FormationModel.DoesNotExist:
            return None

    def get_all(self) -> list[Formation]:
        """Get all formations."""
        models = FormationModel.objects.prefetch_related("emus__coaches").all()
        return [self.model_to_entity(m) for m in models]
