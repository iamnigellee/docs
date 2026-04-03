"""
BlockIntel World Model Layer
============================
The cognitive core of BlockIntel's intelligent business platform.
Two interdependent models form the company's "perception system":

- CompanyWorldModel: replaces hierarchical management with information routing
- CustomerWorldModel: models the financial reality of every customer, merchant, and market

Connected via an asynchronous EventBus for real-time signal propagation.
"""

from .data_models import (
    BuildStatus,
    ConsumerProfile,
    Decision,
    MerchantProfile,
    OrganizationRole,
    ResourceAllocation,
    Signal,
    Transaction,
    generate_build_statuses,
    generate_consumer_profiles,
    generate_decisions,
    generate_merchant_profiles,
    generate_resource_allocations,
    generate_signals,
    generate_transactions,
)
from .event_bus import EventBus, Event
from .company_model import CompanyWorldModel
from .customer_model import CustomerWorldModel

__all__ = [
    # Data models
    "BuildStatus",
    "ConsumerProfile",
    "Decision",
    "MerchantProfile",
    "OrganizationRole",
    "ResourceAllocation",
    "Signal",
    "Transaction",
    # Generators
    "generate_build_statuses",
    "generate_consumer_profiles",
    "generate_decisions",
    "generate_merchant_profiles",
    "generate_resource_allocations",
    "generate_signals",
    "generate_transactions",
    # Event bus
    "Event",
    "EventBus",
    # World models
    "CompanyWorldModel",
    "CustomerWorldModel",
]
