## 🚀 7 - Crear Entidades EMU (con Composición de Coches)

### Objetivo

Implementar entidades de dominio para **EMU (Electric Multiple Units)** compuestas por coches individuales, aplicando Clean Architecture y SOLID.

---

## 📋 Contexto de Negocio

### Formación = "Formación Eléctrica compuesta por EMUs que operan juntas"
- Una **formación** es un conjunto de EMUs que operan juntas.
- La cantidad de EMUs por formación puede variar (ej: 1 EMU de 8 coches).

### EMU = "Electric Multiple Unit" Módulo Compuesto por N Coches
- Una **EMU** esta compuesto de N **coches** que operan como unidad
- Cada **coche** es también una `MaintenanceUnit` independiente, a cada coche se le puede asignar el mantenimiento kilometraje y hs individualmente que se heredan de la EMU.

- La **EMU completa** es nuestra unidad de mantenimiento principal.

### Tipos de Coches según Fabricante

**CSR (China South Rail)**:
- **MC1** / **MC2**: Coche Motriz con cabina (1 o 2)
- **R1**: Coche Remolque con pantógrafo
- **R2**: Coche Remolque

**Toshiba**:
- **M**: Coche Motriz
- **R**: Coche Remolque con pantógrafo
- **RP**: Coche Remolque Prima (R')

### Ejemplo Formación CSR
    F120: (M20, M45)
    F152: (M71, M37)
    F250: (M80)  # Formación con una sola EMU

    Las composición de formaciones es dinámica, están definidas en la BD Access a la cual accedemos en la tabla 'A_00_Formaciones'.

    Pueden heredar de MaintenanceUnit (id, número, estado, fechas, Linea, para éste proyecto = LR (Línea Roca), etc).


### Ejemplo EMUs CSR
```
EMU: M01 → [MC1-5001, R1-5601, R2-5801, MC2-5002]
EMU: M20 → [MC1-5039, R1-5620, R2-5820, MC2-5040]
EMU: M21 → [MC1-5041, R1-5621, R2-5821, MC2-5042]
EMU: M80 → [MC1-5159, R1-5680, MC2-5160]
EMU: M82 → [MC1-5163, R1-5682, MC2-5164]
... etc

```
### Ejemplo EMUs Toshiba
```
EMU: T16 → [M4032, R4616, RP4822, M4031]
EMU: T15 → [M4029, R4615, M4030]
... etc



```



---

## 🏗️ Entidades a Implementar

### 1️⃣ Entidad Base: `MaintenanceUnit`

**Archivo**: `core/domain/entities/maintenance_unit.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from uuid import UUID

@dataclass
class MaintenanceUnit(ABC):
    """
    Base entity for all railway maintenance units.
    
    Can represent both complete formations (EMU) and individual coaches.
    """
    id: UUID
    unit_number: str           # Ej: "EMU-301", "MC1-301", "R1-301"
    description: str
    manufacturer: str          # "CSR Zhuzhou", "Toshiba"
    manufacture_date: date | None
    commissioning_date: date
    status: UnitStatus         # Enum a crear
    line: str | None            # Ej: "LR" (Línea Roca)
    created_at: datetime
    updated_at: datetime
    
    @abstractmethod
    def get_unit_type(self) -> UnitType:
        """Return the type of this unit."""
        pass
    
    def __post_init__(self):
        self._validate()
    
    def _validate(self):
        if not self.unit_number.strip():
            raise ValueError("unit_number cannot be empty")
        if self.commissioning_date > date.today():
            raise ValueError("commissioning_date cannot be in the future")
        if self.manufacture_date and self.manufacture_date > self.commissioning_date:
            raise ValueError("manufacture_date must be before commissioning_date")
```

---

### 2️⃣ Entidad: `Coach` (Coche Individual)

**Archivo**: `core/domain/entities/coach.py`

```python
@dataclass
class Coach(MaintenanceUnit):
    """
    Individual coach within an EMU formation.
    
    Can be a motor coach (with traction) or trailer coach (without).
    """
    coach_type: CoachType      # Enum: MC1, MC2, R1, R2, M, R, RP
    voltage: int | None        # Solo para coches motores (25000V)
    has_pantograph: bool
    has_cabin: bool            # Solo MC1/MC2 tienen cabina
    place: int | None          # Ej: "1..N" segun longitud del EMU
    seating_capacity: int
    emu_id: UUID | None        # FK a la EMU que lo contiene
    
    def get_unit_type(self) -> UnitType:
        return UnitType.COACH
    
    def is_motor_coach(self) -> bool:
        """Check if this coach has traction."""
        return self.coach_type in [CoachType.MC1, CoachType.MC2, CoachType.M]
    
    def _validate(self):
        super()._validate()
        if self.seating_capacity <= 0:
            raise ValueError("seating_capacity must be positive")
        if self.is_motor_coach() and not self.voltage:
            raise ValueError("Motor coaches must have voltage")
```

---

### 3️⃣ Entidad: `EMU` (Módulo Eléctrico)

**Archivo**: `core/domain/entities/emu.py`

```python
@dataclass
class EMU(MaintenanceUnit):
    """
    Electric Multiple Unit: composed of N coaches.
    
    Represents the entire trainset that operates as a single unit.
    Composed of individual coaches (motor and trailer).
    """
    voltage: int               # 25000 para AC 25kV
    max_speed: int             # km/h
    total_passenger_capacity: int
    coaches: list[Coach]       # Composición de coches
    formation_id: UUID | None  # FK a la Formación que lo contiene
    configuration_id: UUID | None  # FK a ConformacionEmu (reglas flexibles)
    
    def get_unit_type(self) -> UnitType:
        return UnitType.EMU
    
    def __post_init__(self):
        super().__post_init__()
        self._validate_composition()
    
    def _validate_composition(self):
        """Validate that EMU has valid coach composition."""
        if len(self.coaches) < 2:
            raise ValueError("EMU must have at least 2 coaches")
        
        # Verificar que todos los coches son del mismo fabricante
        manufacturers = {coach.manufacturer for coach in self.coaches}
        if len(manufacturers) > 1:
            raise ValueError("All coaches must be from same manufacturer")
        
        # If a configuration is assigned, validate composition in a service layer
        # using EmuConfiguration.validate(...) to avoid hardcoding sequences here.
    
    def get_motor_coaches(self) -> list[Coach]:
        """Return all coaches with traction."""
        return [c for c in self.coaches if c.is_motor_coach()]
    
    def get_trailer_coaches(self) -> list[Coach]:
        """Return all non-motor coaches."""
        return [c for c in self.coaches if not c.is_motor_coach()]
```

---

### 4️⃣ Entidad: `Formation` (Formación Operativa)

**Archivo**: `core/domain/entities/formation.py`

```python
@dataclass
class Formation(MaintenanceUnit):
    """
    Formation: operational unit composed of one or more EMUs.
    
    Represents a complete trainset that operates together in service.
    Example sizes: 1 EMU (8 coaches) or 2 EMUs (3 + 4 coaches).
    
    Example: F120 = (EMU M20, EMU M45)
    
    Attributes:
        emus: List of EMUs that compose this formation
        route: Optional route information (busline/service)
    """
    f_id: str               # Identificador único de la formación
    emus: list[EMU]            # 1 o mas EMUs
    route: str | None          # Ej: "Roca", "Sarmiento", etc
    
    def get_unit_type(self) -> UnitType:
        return UnitType.FORMATION
    
    def __post_init__(self):
        super().__post_init__()
        self._validate_composition()
    
    def _validate_composition(self):
        """Validate that formation has at least 1 EMU."""
        if len(self.emus) < 1:
            raise ValueError("Formation must have at least 1 EMU")
        
        # Verificar que todos los EMUs son del mismo fabricante
        manufacturers = {emu.manufacturer for emu in self.emus}
        if len(manufacturers) > 1:
            raise ValueError("Both EMUs must be from same manufacturer")
    
    def get_total_coaches(self) -> int:
        """Return total number of coaches in formation."""
        return sum(len(emu.coaches) for emu in self.emus)
    
    def get_all_coaches(self) -> list[Coach]:
        """Return all coaches from both EMUs."""
        all_coaches = []
        for emu in self.emus:
            all_coaches.extend(emu.coaches)
        return all_coaches
    
    def get_total_passenger_capacity(self) -> int:
        """Return combined passenger capacity of both EMUs."""
        return sum(emu.total_passenger_capacity for emu in self.emus)
```

---

### 5️⃣ Entidad: `EmuConfiguration` (ConformacionEmu)

**Archivo**: `core/domain/entities/emu_configuration.py`

```python
@dataclass(frozen=True)
class EmuConfiguration:
    """
    Defines a valid coach composition for an EMU.
    
    Example CSR 4-coach: [MC1, R1, R2, MC2]
    Example CSR 8-coach: [MC1, R1, R2, MC2, MC1, R1, R2, MC2]
    """
    id: UUID
    name: str                 # Ej: "CSR-4", "CSR-8", "Toshiba-3"
    manufacturer: str         # "CSR Zhuzhou", "Toshiba"
    coach_sequence: list[CoachType]
    min_coaches: int
    max_coaches: int

    def validate(self, coaches: list[Coach]) -> None:
        """Validate if a coach list matches this configuration."""
        if len(coaches) < self.min_coaches or len(coaches) > self.max_coaches:
            raise ValueError("Coach count outside configuration range")
        # Optional: match ordered sequence (if strict)
        # Optional: allow partial match for legacy data
```

---

## 🎨 Value Objects a Crear

### `UnitStatus`
**Archivo**: `core/domain/value_objects/unit_status.py`
```python
from enum import Enum

class UnitStatus(Enum):
    AVAILABLE = "available"  # Disponible
    DISABLED = "disabled"    # Detenida
    IN_MAINTENANCE = "in_maintenance" # En mantenimiento preventivo / programado
    UNDER_REPAIR = "under_repair" # En reparación correctiva
    RETIRED = "retired" # Fuera de servicio
```

### `UnitType`
**Archivo**: `core/domain/value_objects/unit_type.py`
```python
class UnitType(Enum):
    FORMATION = "formation"    # Formación (1+ EMUs)
    EMU = "emu"                # EMU (N coches)
    COACH = "coach"            # Coche individual
    # Futuros: LOCOMOTIVE, TRAILER_COACH, etc.
```

### `CoachType`
**Archivo**: `core/domain/value_objects/coach_type.py`
```python
class CoachType(Enum):
    # CSR types
    MC1 = "mc1"    # Motor Coach 1 (con cabina)
    MC2 = "mc2"    # Motor Coach 2 (con cabina)
    R1 = "r1"      # Remolque 1
    R2 = "r2"      # Remolque 2 (con pantógrafo)
    
    # Toshiba types
    M = "m"        # Motriz
    R = "r"        # Remolque
    RP = "rp"      # Remolque con Pantógrafo
```


---

## 📁 Estructura de Archivos

```
core/
└── domain/
    ├── entities/
    │   ├── __init__.py
    │   ├── maintenance_unit.py   # Base abstracta
    │   ├── coach.py              # Coche individual
    │   ├── emu.py                # Unidad Eléctrica
    │   ├── formation.py          # Formación (1+ EMUs)
    │   └── emu_configuration.py  # ConformacionEmu
    └── value_objects/
        ├── __init__.py
        ├── unit_status.py
        ├── unit_type.py
        └── coach_type.py
```

---

## ✅ Tests a Crear

### `test_coach.py`

**Archivo**: `tests/core/domain/entities/test_coach.py`

```python
from uuid import uuid4
from datetime import date, datetime
from core.domain.entities.coach import Coach
from core.domain.value_objects import CoachType, UnitStatus

def test_create_motor_coach_csr():
    """Se puede crear un coche motor CSR."""
    coach = Coach(
        id=uuid4(),
        unit_number="MC1-301",
        description="Motor Coach 1",
        manufacturer="CSR Zhuzhou",
        manufacture_date=date(2014, 3, 15),
        commissioning_date=date(2015, 1, 20),
        status=UnitStatus.AVAILABLE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        coach_type=CoachType.MC1,
        voltage=25000,
        has_pantograph=False,
        has_cabin=True,
        seating_capacity=52,
        emu_id=None
    )
    assert coach.is_motor_coach() == True
    assert coach.has_cabin == True

def test_motor_coach_requires_voltage():
    """Coches motrices deben tener voltage."""
    with pytest.raises(ValueError, match="Motor coaches must have voltage"):
        Coach(
            id=uuid4(),
            unit_number="MC1-301",
            description="Motor Coach 1",
            manufacturer="CSR Zhuzhou",
            manufacture_date=date(2014, 3, 15),
            commissioning_date=date(2015, 1, 20),
            status=UnitStatus.AVAILABLE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            coach_type=CoachType.MC1,
            voltage=None,  # Error!
            has_pantograph=False,
            has_cabin=True,
            seating_capacity=52,
            emu_id=None
        )

def test_trailer_coach_without_voltage():
    """Coches remolque no necesitan voltage."""
    coach = Coach(
        id=uuid4(),
        unit_number="R1-301",
        description="Remolque 1",
        manufacturer="CSR Zhuzhou",
        manufacture_date=date(2014, 3, 15),
        commissioning_date=date(2015, 1, 20),
        status=UnitStatus.AVAILABLE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        coach_type=CoachType.R1,
        voltage=None,
        has_pantograph=False,
        has_cabin=False,
        seating_capacity=72,
        emu_id=None
    )
    assert coach.is_motor_coach() == False
```

### `test_emu.py`

**Archivo**: `tests/core/domain/entities/test_emu.py`

```python
def test_create_valid_csr_emu():
    """Se puede crear una EMU CSR válida."""
    mc1 = Coach(
        id=uuid4(),
        unit_number="MC1-5001",
        description="Motor Coach 1",
        manufacturer="CSR Zhuzhou",
        manufacture_date=date(2014, 3, 15),
        commissioning_date=date(2015, 1, 20),
        status=UnitStatus.AVAILABLE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        coach_type=CoachType.MC1,
        voltage=25000,
        has_pantograph=False,
        has_cabin=True,
        seating_capacity=52,
        emu_id=None
    )
    
    r1 = Coach(..., coach_type=CoachType.R1, voltage=None, ...)
    r2 = Coach(..., coach_type=CoachType.R2, voltage=None, has_pantograph=True, ...)
    mc2 = Coach(..., coach_type=CoachType.MC2, voltage=25000, has_cabin=True, ...)
    
    emu = EMU(
        id=uuid4(),
        unit_number="M01",
        description="Módulo CSR 01",
        manufacturer="CSR Zhuzhou",
        manufacture_date=date(2014, 12, 1),
        commissioning_date=date(2015, 2, 1),
        status=UnitStatus.AVAILABLE,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        voltage=25000,
        max_speed=120,
        total_passenger_capacity=180,
        coaches=[mc1, r1, r2, mc2],
        formation_id=None
    )
    
    assert len(emu.coaches) == 4
    assert len(emu.get_motor_coaches()) == 2
    assert len(emu.get_trailer_coaches()) == 2

def test_emu_must_have_minimum_coaches():
    """EMU debe tener un minimo de coches."""
    coach1 = Coach(...)
    
    with pytest.raises(ValueError, match="EMU must have at least 2 coaches"):
        EMU(
            ...,
            coaches=[coach1]  # Solo 1!
        )

def test_emu_configuration_validates_sequence():
    """ConformacionEmu valida la secuencia de coches."""
    config = EmuConfiguration(
        id=uuid4(),
        name="CSR-4",
        manufacturer="CSR Zhuzhou",
        coach_sequence=[CoachType.MC1, CoachType.R1, CoachType.R2, CoachType.MC2],
        min_coaches=4,
        max_coaches=4
    )
    mc1 = Coach(..., coach_type=CoachType.MC1, ...)
    r1 = Coach(..., coach_type=CoachType.R1, ...)
    r2 = Coach(..., coach_type=CoachType.R2, ...)
    mc2 = Coach(..., coach_type=CoachType.MC2, ...)
    
    config.validate([mc1, r1, r2, mc2])

def test_emu_coaches_same_manufacturer():
    """Todos los coches de una EMU deben ser del mismo fabricante."""
    mc1_csr = Coach(..., manufacturer="CSR Zhuzhou", ...)
    r1_csr = Coach(..., manufacturer="CSR Zhuzhou", ...)
    r2_toshiba = Coach(..., manufacturer="Toshiba", ...)  # Diferente!
    mc2_csr = Coach(..., manufacturer="CSR Zhuzhou", ...)
    
    with pytest.raises(ValueError, match="All coaches must be from same manufacturer"):
        EMU(..., coaches=[mc1_csr, r1_csr, r2_toshiba, mc2_csr])
```

### `test_formation.py`

**Archivo**: `tests/core/domain/entities/test_formation.py`

```python
from uuid import uuid4
from datetime import date, datetime
from core.domain.entities.formation import Formation
from core.domain.entities.emu import EMU
from core.domain.entities.coach import Coach
from core.domain.value_objects import CoachType, UnitStatus, UnitType

def test_create_valid_formation():
    """Se puede crear una formación válida con 2 EMUs."""
    # Crear coches para EMU 1 (3 coches)
    mc1_emu1 = Coach(
        id=uuid4(),
        unit_number="MC1-5001",
        description="Motor Coach 1",
        manufacturer="CSR Zhuzhou",
        manufacture_date=date(2014, 3, 15),
        commissioning_date=date(2015, 1, 20),
        status=UnitStatus.AVAILABLE,
        line="LR",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        coach_type=CoachType.MC1,
        voltage=25000,
        has_pantograph=False,
        has_cabin=True,
        place=1,
        seating_capacity=52,
        emu_id=None
    )
    r1_emu1 = Coach(..., coach_type=CoachType.R1, place=2, ...)
    mc2_emu1 = Coach(..., coach_type=CoachType.MC2, has_cabin=True, place=3, ...)
    
    # Crear EMU 1 (3 coches)
    emu1 = EMU(
        id=uuid4(),
        unit_number="M01",
        description="Módulo CSR 01",
        manufacturer="CSR Zhuzhou",
        manufacture_date=date(2014, 12, 1),
        commissioning_date=date(2015, 2, 1),
        status=UnitStatus.AVAILABLE,
        line="LR",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        voltage=25000,
        max_speed=120,
        total_passenger_capacity=176,
        coaches=[mc1_emu1, r1_emu1, mc2_emu1],
        formation_id=None
    )
    
    # Crear EMU 2 (4 coches)
    mc1_emu2 = Coach(..., coach_type=CoachType.MC1, place=1, ...)
    r1_emu2 = Coach(..., coach_type=CoachType.R1, place=2, ...)
    r2_emu2 = Coach(..., coach_type=CoachType.R2, place=3, ...)
    mc2_emu2 = Coach(..., coach_type=CoachType.MC2, place=4, ...)
    
    emu2 = EMU(
        id=uuid4(),
        unit_number="M20",
        description="Módulo CSR 20",
        manufacturer="CSR Zhuzhou",
        manufacture_date=date(2014, 12, 1),
        commissioning_date=date(2015, 2, 1),
        status=UnitStatus.AVAILABLE,
        line="LR",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        voltage=25000,
        max_speed=120,
        total_passenger_capacity=228,
        coaches=[mc1_emu2, r1_emu2, r2_emu2, mc2_emu2],
        formation_id=None
    )
    
    # Crear Formación con 2 EMUs
    formation = Formation(
        id=uuid4(),
        unit_number="F120",
        description="Formación CSR 120",
        manufacturer="CSR Zhuzhou", 
        manufacture_date=date(2014, 12, 1),
        commissioning_date=date(2015, 2, 1),
        status=UnitStatus.AVAILABLE,
        line="LR",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        emus=[emu1, emu2],
        route="Constitución - La Plata" 
        #route = "PC-LP"
    )
    
    assert formation.get_unit_type() == UnitType.FORMATION
    assert len(formation.emus) == 2
    assert formation.get_total_coaches() == 7  # 3 + 4
    assert formation.get_total_passenger_capacity() == 404  # 176 + 228

def test_formation_must_have_at_least_one_emu():
    """Formación debe tener al menos 1 EMU."""
    with pytest.raises(ValueError, match="Formation must have at least 1 EMU"):
        Formation(
            ...,
            emus=[]  # Ninguno
        )

def test_formation_emus_same_manufacturer():
    """Ambos EMUs de una formación deben ser del mismo fabricante."""
    emu1_csr = EMU(..., manufacturer="CSR Zhuzhou", ...)
    emu2_toshiba = EMU(..., manufacturer="Toshiba", ...)  # Diferente!
    
    with pytest.raises(ValueError, match="Both EMUs must be from same manufacturer"):
        Formation(..., emus=[emu1_csr, emu2_toshiba])

def test_formation_get_all_coaches():
    """Se pueden obtener todos los coches de una formación."""
    emu1 = EMU(..., coaches=[coach1, coach2, coach3])  # 3 coches
    emu2 = EMU(..., coaches=[coach4, coach5, coach6, coach7])  # 4 coches
    
    formation = Formation(..., emus=[emu1, emu2])
    
    all_coaches = formation.get_all_coaches()
    assert len(all_coaches) == 7
```

### `test_emu_configuration.py`

**Archivo**: `tests/core/domain/entities/test_emu_configuration.py`

```python
from uuid import uuid4
import pytest
from core.domain.entities.emu_configuration import EmuConfiguration
from core.domain.entities.coach import Coach
from core.domain.value_objects import CoachType

def test_emu_configuration_accepts_valid_sequence():
    """Conformacion Emu acepta una secuencia valida."""
    config = EmuConfiguration(
        id=uuid4(),
        name="CSR-4",
        manufacturer="CSR Zhuzhou",
        coach_sequence=[CoachType.MC1, CoachType.R1, CoachType.R2, CoachType.MC2],
        min_coaches=4,
        max_coaches=4
    )
    mc1 = Coach(..., coach_type=CoachType.MC1, ...)
    r1 = Coach(..., coach_type=CoachType.R1, ...)
    r2 = Coach(..., coach_type=CoachType.R2, ...)
    mc2 = Coach(..., coach_type=CoachType.MC2, ...)

    config.validate([mc1, r1, r2, mc2])

def test_emu_configuration_rejects_invalid_count():
    """ConformacionEmu rechaza una cantidad invalida de coches."""
    config = EmuConfiguration(..., min_coaches=4, max_coaches=4, ...)
    mc1 = Coach(...)

    with pytest.raises(ValueError, match="Coach count outside configuration range"):
        config.validate([mc1])
```

---

## 🎯 Checklist de Implementación

- [ ] Crear estructura de carpetas (`entities/`, `value_objects/`)
- [ ] Implementar enums: `UnitStatus`, `UnitType` (incluir FORMATION), `CoachType`
- [ ] Implementar `MaintenanceUnit` (ABC) con validaciones
- [ ] Implementar `Coach` con lógica motor/remolque
- [ ] Implementar `EMU` con validación de composición
- [ ] Implementar `Formation` con validación de 1+ EMUs
- [ ] Implementar `EmuConfiguration` para composición flexible
- [ ] Tests para `Coach` (mínimo 3 tests)
- [ ] Tests para `EMU` (mínimo 4 tests)
- [ ] Tests para `Formation` (mínimo 4 tests)
- [ ] Tests para `EmuConfiguration` (mínimo 2 tests)
- [ ] Verificar NO imports de Django/infraestructura
- [ ] Coverage > 85% en `core/domain/entities/`

---

## 🚦 Comandos de Verificación

```bash
# Tests
pytest tests/core/domain/entities/ -v

# Coverage
pytest tests/core/domain/entities/ --cov=core/domain/entities --cov-report=term-missing

# Verificar pureza (debe devolver vacío)
grep -r "from django" core/
grep -r "import django" core/
```

---

## 📝 Notas Importantes

- **NO** crear Django models ahora (eso después en `infrastructure/`)
- **NO** implementar lógica de mantenimiento todavía (solo estructura)
- Los `coaches` en `EMU` son referencias, a objetos coaches existentes
- Los `emus` en `Formation` son referencias a objetos EMU existentes
- `emu_id` en `Coach` es opcional (puede existir coche sin EMU asignada)
- `formation_id` en `EMU` es opcional (puede existir EMU sin Formación asignada)
- `configuration_id` en `EMU` no es opcional (no puede existir EMU sin ConformacionEmu)
- `line` en todas las entidades es para identificar línea operativa (ej: "LR" = Línea Roca)
- `place` en Coach es la posicion dentro del EMU (1..N)
- `route` en Formation es información de servicio (ej: "Constitución - La Plata")
- Composición de formaciones dinámica: puede variar, se puede obtener desde la BD.
- Composición de EMUs dinámica: puede variar, se puede obtener desde la BD. (Muy improbable en CSR, mas común en Toshiba)
- Validaciones CSR/Toshiba se pueden expandir después
- Locomotives y otros tipos se implementarán en futuras iteraciones
