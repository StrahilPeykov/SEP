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
    """
    Enum for the types of mentions that can be returned with the emission trace.
    """

    INFORMATION = "Information"
    WARNING = "Warning"
    ERROR = "Error"

@dataclass
class EmissionTraceMention:
    """
    Class that models a message that is passed up on the emission trace tree.
    """

    mention_class: EmissionTraceMentionClass
    message: str

    def __str__(self) -> str:
        """
        __str__ override that returns the mention class and the message of an emission trace mention as a string.

        Returns:
            mention class and message of the emission trace object
        """

        return f"{self.mention_class}: {self.message}"

    def __hash__(self) -> int:
        """
        __hash__ override that returns a hash of the mention class and the message of an emission trace mention.

        Returns:
            hash of emission trace mention class and message
        """

        return hash((self.mention_class, self.message))

@dataclass
class EmissionTraceChild:
    """
    Class that holds the information of the object's children and how many of those children the object is attached to.
    """

    emission_trace: 'EmissionTrace'
    quantity: float

    def __str__(self) -> str:
        """
        __str__ override that returns the quantity and the emission trace object as a string.

        Returns:
            quantity and emission trace object as a string
        """

        return f"{self.quantity}x {self.emission_trace}"

    def __hash__(self) -> int:
        """
        __hash__ override that returns the quantity and the emission trace object as hash.

        Returns:
            hash of emission trace object and quantity
        """

        return hash((self.emission_trace, self.quantity))

@dataclass
class EmissionSplit:
    """
    Class that holds both biogenic and non-biogenic emissions in one place.
    """
    biogenic: float = 0.0
    non_biogenic: float = 0.0

    def __add__(self, other: "EmissionSplit") -> "EmissionSplit":
        """
        __add__ override that adds biogenic and non-biogenic emissions separately.

        Args:
            other: EmissionSplit object
        Returns:
            EmissionSplit object
        """

        return EmissionSplit(
            biogenic=self.biogenic + other.biogenic,
            non_biogenic=self.non_biogenic + other.non_biogenic,
        )

    def __mul__(self, factor: float) -> "EmissionSplit":
        """
        __mul__ override that multiplies biogenic and non-biogenic emissions separately.

        Args:
            factor: float
        Returns:
            EmissionSplit object
        """

        return EmissionSplit(
            biogenic=self.biogenic * factor,
            non_biogenic=self.non_biogenic * factor,
        )

    def __hash__(self) -> int:
        """
        __hash__ override that returns the biogenic and non-biogenic emissions in hash.

        Returns:
            hash of biogenic and non-biogenic emissions
        """

        return hash((self.biogenic, self.non_biogenic))

    @property
    def total(self) -> float:
        """
        Adds up biogenic and non-biogenic emissions together and returns the total emission.

        Returns:
            total emission
        """

        return self.biogenic + self.non_biogenic

@dataclass
class EmissionTrace:
    """
    Class that models an emission trace object.
    """

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
        """
        Returns the type of object that the EmissionTrace is linked to.

        Returns:
            Emission type as string
        """

        from core.models import (Product, Emission,
                                 UserEnergyEmission, UserEnergyEmissionReference,
                                 TransportEmission, TransportEmissionReference,
                                 ProductionEnergyEmission, ProductionEnergyEmissionReference)  # Import here to avoid circular import
        if isinstance(self.related_object, Product):
            return "Product"
        elif isinstance(self.related_object, TransportEmissionReference):
            return "TransportEmissionReference"
        elif isinstance(self.related_object, UserEnergyEmissionReference):
            return "UserEnergyEmissionReference"
        elif isinstance(self.related_object, ProductionEnergyEmissionReference):
            return "ProductionEnergyEmissionReference"
        elif isinstance(self.related_object, TransportEmission):
            return "TransportEmission"
        elif isinstance(self.related_object, UserEnergyEmission):
            return "UserEnergyEmission"
        elif isinstance(self.related_object, ProductionEnergyEmission):
            return "ProductionEnergyEmission"
        elif isinstance(self.related_object, Emission):
            return "Emission"
        else:
            return None

    def __str__(self) -> str:
        """
        __str__ override that returns an emission trace object information as a string.

        Returns:
            emission trace object information
        """

        return f"EmissionTrace(label={self.label}, emissions={self.emissions_subtotal}, children={self.children})"

    def __hash__(self) -> int:
        """
        __hash__ override that returns the emission trace object information as a hash.

        Returns:
            hash of emission trace object information
        """

        return hash((self.label, tuple(self.emissions_subtotal.items()), tuple(self.children), tuple(self.mentions)))

    def __mul__(self, quantity:float) -> 'EmissionTrace':
        """
        __mul__ override that multiplies the emissions in the emission trace object with a multiplier.

        Args:
            quantity: float
        Returns:
            EmissionTrace object with multiplied emissions
        """

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
        """
        This method iterates through all children of the EmissionTrace object and sums up their emissions.
        It updates the emissions_subtotal dictionary with the total emissions for each lifecycle stage.
        """

        for child in self.children:
            for lifecycle_stage, value in child.emission_trace.emissions_subtotal.items():
                if lifecycle_stage in self.emissions_subtotal:
                    self.emissions_subtotal[lifecycle_stage] += value * child.quantity
                else:
                    self.emissions_subtotal[lifecycle_stage] = value * child.quantity

    def __float__(self) -> float:
        """
        __float__ override that returns the total emission of an EmissionTrace object

        Returns:
            total emission of an EmissionTrace object as float
        """

        return self.total

    @property
    def total_biogenic(self) -> float:
        """
        Returns the total biogenic emission of an EmissionTrace object

        Returns:
            total biogenic emission of an EmissionTrace object as float
        """

        return round(sum(split.biogenic for split in self.emissions_subtotal.values()), 2)

    @property
    def total_non_biogenic(self) -> float:
        """
        Returns the total non-biogenic emission of an EmissionTrace object

        Returns:
            total non-biogenic emission of an EmissionTrace object as float
        """

        return round(sum(split.non_biogenic for split in self.emissions_subtotal.values()), 2)

    @property
    def total(self) -> float:
        """
        Returns the total emission of an EmissionTrace object

        Returns:
            total emission of an EmissionTrace object as float
        """

        return round(sum(split.total for split in self.emissions_subtotal.values()), 2)