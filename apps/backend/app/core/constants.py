from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    NO_ANSWER = "no_answer"

class EmploymentStatus(str, Enum):
    EMPLOYED = "employed"
    UNEMPLOYED = "unemployed"
    STUDENT = "student"
    SELF_EMPLOYED = "self_employed"
    PART_TIME = "part_time"
    HOMEMAKER = "homemaker"
    RETIRED = "retired"
    OTHER = "other"
    UNKNOWN = "unknown"

class IncomeDecreasedReason(str, Enum):
    JOB_LOSS = "job_loss"
    BUSINESS_CLOSURE = "business_closure"
    REDUCED_SHIFT = "reduced_shift"
    INCOME_DROP = "income_drop"
    LEAVE_ABSENCE = "leave_absence"
    OTHER = "other"
    UNKNOWN = "unknown"

class SavingsAmountRange(str, Enum):
    UNDER_500K = "under_500k"
    K500_TO_1M = "500k_to_1m"
    M1M_TO_3M = "1m_to_3m"
    M3M_TO_5M = "3m_to_5m"
    M5M_OR_MORE = "5m_or_more"
    UNKNOWN = "unknown"

class DisabilityType(str, Enum):
    PHYSICAL = "physical"
    INTELLECTUAL = "intellectual"
    MENTAL = "mental"
    INTRACTABLE_DISEASE = "intractable_disease"
    OTHER = "other"
    UNKNOWN = "unknown"

class SupportType(str, Enum):
    CASH = "cash"
    SUBSIDY = "subsidy"
    MEDICAL = "medical"
    SERVICE_DISCOUNT = "service_discount"
    SERVICE_DISPATCH = "service_dispatch"
    LOAN = "loan"
    GOODS = "goods"
    CONSULTATION = "consultation"
    TAX_REDUCTION = "tax_reduction"
    OTHER = "other"

class Category(str, Enum):
    HOUSING = "housing"
    CHILDCARE = "childcare"
    LIVELIHOOD = "livelihood"
    DISABILITY = "disability"
    EDUCATION = "education"
    MEDICAL = "medical"
    OTHER = "other"

class BenefitAmountType(str, Enum):
    FIXED = "fixed"
    MAX_AMOUNT = "max_amount"
    DEPENDS = "depends"
    FREE_TEXT = "free_text"
    UNKNOWN = "unknown"

class BenefitUnit(str, Enum):
    PER_PERSON = "per_person"
    PER_CHILD = "per_child"
    PER_HOUSEHOLD = "per_household"
    PER_MONTH = "per_month"
    PER_USE = "per_use"
    ONE_TIME = "one_time"
    OTHER = "other"
    UNKNOWN = "unknown"

class ApplicationMethod(str, Enum):
    ONLINE = "online"
    MAIL = "mail"
    COUNTER = "counter"
    AUTOMATIC = "automatic"
    NOT_REQUIRED = "not_required"
    UNKNOWN = "unknown"

class ApplicationPeriodType(str, Enum):
    ALWAYS = "always"
    DEADLINE = "deadline"
    LIMITED = "limited"
    UNKNOWN = "unknown"

class ConfidenceLevel(str, Enum):
    OFFICIAL = "official"
    MANUAL_CHECKED = "manual_checked"
    ESTIMATED = "estimated"
    DUMMY = "dummy"

class SourceType(str, Enum):
    HTML = "html"
    PDF = "pdf"
    MANUAL = "manual"
    OTHER = "other"

class UserProgramStatus(str, Enum):
    INTERESTED = "interested"
    CHECKING = "checking"
    APPLIED = "applied"
    APPROVED = "approved"
    REJECTED = "rejected"
    NOT_APPLICABLE = "not_applicable"

class HousingStatus(str, Enum):
    OWNED = "owned"
    RENTED = "rented"
    PUBLIC_HOUSING = "public_housing"
    LIVING_WITH_FAMILY = "living_with_family"
    OTHER = "other"
    UNKNOWN = "unknown"
