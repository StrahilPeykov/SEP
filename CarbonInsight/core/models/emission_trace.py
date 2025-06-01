from copy import deepcopy, copy
from dataclasses import field, dataclass
from enum import Enum
from numbers import Number
from typing import Optional, List, Dict, Tuple, Set, Literal, Union, TYPE_CHECKING, Any

from core.models.lifecycle_stage import LifecycleStage
from core.models.pcf_calculation_method import PcfCalculationMethod
from core.models.reference_impact_unit import ReferenceImpactUnit

if TYPE_CHECKING:
    from core.models import Product, Emission, UserEnergyEmissionReference, TransportEmissionReference, \
        ProductionEnergyEmissionReference, MaterialEmissionReference

class EmissionTraceMentionClass(Enum):
    INFORMATION = "Information"
    WARNING = "Warning"
    ERROR = "Error"

@dataclass
class EmissionTraceMention:
    mention_class: EmissionTraceMentionClass
    message: str

    def __str__(self):
        return f"{self.mention_class}: {self.message}"

    def __hash__(self):
        return hash((self.mention_class, self.message))

@dataclass
class EmissionTraceChild:
    emission_trace: 'EmissionTrace'
    quantity: float

    def __str__(self):
        return f"{self.quantity}x {self.emission_trace}"

    def __hash__(self):
        return hash((self.emission_trace, self.quantity))

@dataclass
class EmissionSplit:
    """Hold both biogenic and non-biogenic in one place."""
    biogenic: float = 0.0
    non_biogenic: float = 0.0

    def __add__(self, other: "EmissionSplit") -> "EmissionSplit":
        return EmissionSplit(
            biogenic=self.biogenic + other.biogenic,
            non_biogenic=self.non_biogenic + other.non_biogenic,
        )

    def __mul__(self, factor: float) -> "EmissionSplit":
        return EmissionSplit(
            biogenic=self.biogenic * factor,
            non_biogenic=self.non_biogenic * factor,
        )

    def __hash__(self):
        return hash((self.biogenic, self.non_biogenic))

    @property
    def total(self) -> float:
        return self.biogenic + self.non_biogenic

@dataclass
class EmissionTrace:
    label: str
    reference_impact_unit: ReferenceImpactUnit
    related_object: Any = None
    methodology: Optional[str] = None
    pcf_calculation_method: PcfCalculationMethod = PcfCalculationMethod.ISO_14040_ISO_14044
    # This contains the emissions up to this stage
    emissions_subtotal: Dict[LifecycleStage, EmissionSplit] = field(default_factory=dict)
    # key = LifecycleStage; value = quantity
    children: Set[EmissionTraceChild] = field(default_factory=set)
    mentions: List[EmissionTraceMention] = field(default_factory=list)

    @property
    def source(self) -> Optional[str]:
        from core.models import (Product, Emission,
                                 UserEnergyEmission, UserEnergyEmissionReference,
                                 TransportEmission, TransportEmissionReference,
                                 ProductionEnergyEmission, ProductionEnergyEmissionReference,
                                 MaterialEmission, MaterialEmissionReference)  # Import here to avoid circular import
        if isinstance(self.related_object, Product):
            return "Product"
        elif isinstance(self.related_object, TransportEmissionReference):
            return "TransportEmissionReference"
        elif isinstance(self.related_object, UserEnergyEmissionReference):
            return "UserEnergyEmissionReference"
        elif isinstance(self.related_object, ProductionEnergyEmissionReference):
            return "ProductionEnergyEmissionReference"
        elif isinstance(self.related_object, MaterialEmissionReference):
            return "MaterialEmissionReference"
        elif isinstance(self.related_object, TransportEmission):
            return "TransportEmission"
        elif isinstance(self.related_object, UserEnergyEmission):
            return "UserEnergyEmission"
        elif isinstance(self.related_object, ProductionEnergyEmission):
            return "ProductionEnergyEmission"
        elif isinstance(self.related_object, MaterialEmission):
            return "MaterialEmission"
        elif isinstance(self.related_object, Emission):
            return "Emission"
        else:
            return None

    def __str__(self):
        return f"EmissionTrace(label={self.label}, emissions={self.emissions_subtotal}, children={self.children})"

    def __hash__(self):
        return hash((self.label, tuple(self.emissions_subtotal.items()), tuple(self.children), tuple(self.mentions)))

    def __mul__(self, quantity:float) -> 'EmissionTrace':
        if not isinstance(quantity, float):
            raise TypeError(f"Cannot multiply EmissionTrace by {type(quantity)}")
        et = deepcopy(self)
        et.label = f"{self.label} * {quantity}"
        et.methodology = f"({self.methodology}) * {quantity}" if self.methodology else None
        et.emissions_subtotal = {
            stage: split * quantity
            for stage, split in self.emissions_subtotal.items()
        }
        et.children.clear()
        et.children.add(
            EmissionTraceChild(
                emission_trace=self,
                quantity=quantity
            )
        )
        et.mentions.clear()
        return et

    def sum_up(self):
        for child in self.children:
            for lifecycle_stage, value in child.emission_trace.emissions_subtotal.items():
                if lifecycle_stage in self.emissions_subtotal:
                    self.emissions_subtotal[lifecycle_stage] += value * child.quantity
                else:
                    self.emissions_subtotal[lifecycle_stage] = value * child.quantity

    def __float__(self) -> float:
        return self.total

    @property
    def total_biogenic(self) -> float:
        return round(sum(split.biogenic for split in self.emissions_subtotal.values()), 2)

    @property
    def total_non_biogenic(self) -> float:
        return round(sum(split.non_biogenic for split in self.emissions_subtotal.values()), 2)

    @property
    def total(self) -> float:
        return round(sum(split.total for split in self.emissions_subtotal.values()), 2)