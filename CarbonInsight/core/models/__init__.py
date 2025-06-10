from auditlog.registry import auditlog

from .emission import Emission, EmissionOverrideFactor
from .emission_bom_link import EmissionBoMLink
from .company import Company
from .company_membership import CompanyMembership
from .product import Product
from .product_bom_line_item import ProductBoMLineItem
from .product_sharing_request import ProductSharingRequest, ProductSharingRequestStatus
from .production_energy_emission import ProductionEnergyEmission, ProductionEnergyEmissionReference, ProductionEnergyEmissionReferenceFactor
from .transport_emission import TransportEmission, TransportEmissionReference, TransportEmissionReferenceFactor
from .user import User
from .user_energy_emission import UserEnergyEmission, UserEnergyEmissionReference, UserEnergyEmissionReferenceFactor
from .ai_conversation_log import AIConversationLog
from .lifecycle_stage import LifecycleStage

#auditlog.register(Emission)
auditlog.register(Company)
#auditlog.register(CompanyMembership)
auditlog.register(Product)
#auditlog.register(ProductBoMLineItem)
#auditlog.register(ProductSharingRequest)
auditlog.register(ProductionEnergyEmission)
#auditlog.register(ProductionEnergyEmissionReference)
#auditlog.register(ProductionEnergyEmissionReferenceFactor)
auditlog.register(TransportEmission)
#auditlog.register(TransportEmissionReference)
#auditlog.register(TransportEmissionReferenceFactor)
#auditlog.register(User)
auditlog.register(UserEnergyEmission)
#auditlog.register(UserEnergyEmissionReference)
#auditlog.register(UserEnergyEmissionReferenceFactor)
