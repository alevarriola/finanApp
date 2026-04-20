import datetime
import uuid
from decimal import Decimal

import strawberry
from pydantic import BaseModel, Field, field_validator

from app.graphql.ai_chat.enums import AiTransactionEventStatus, ValidationStatus
from app.graphql.categories.enums import CategoryKind
from app.graphql.transactions.enums import TransactionKind
from app.graphql.wallets.enums import WalletKind, WalletRole


class AiWalletContext(BaseModel):
    id: uuid.UUID
    name: str
    wallet_kind: WalletKind
    currency: str
    role: WalletRole


class AiCategoryContext(BaseModel):
    id: uuid.UUID
    name: str
    name_es: str | None = None
    category_kind: CategoryKind


class ParsedTransaction(BaseModel):
    raw_text: str
    wallet_hint: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    transaction_kind: TransactionKind | None = None
    category_hint: str | None = None
    description: str | None = None
    date: datetime.date | None = None
    confidence: float = 0.0
    requires_confirmation: bool = True
    validation_status: ValidationStatus = ValidationStatus.PARSED

    @field_validator("confidence")
    @classmethod
    def _validate_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return value


class ValidatedTransaction(BaseModel):
    event_id: uuid.UUID | None = None
    raw_text: str
    wallet_id: uuid.UUID | None = None
    wallet_name: str | None = None
    category_id: uuid.UUID | None = None
    category_name: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    transaction_kind: TransactionKind | None = None
    description: str | None = None
    date: datetime.date | None = None
    confidence: float = 0.0
    requires_confirmation: bool = True
    unresolved_fields: list[str] = Field(default_factory=list)
    validation_status: ValidationStatus = ValidationStatus.VALIDATED

    @field_validator("confidence")
    @classmethod
    def _validate_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return value


@strawberry.type
class ParsedTransactionType:
    raw_text: str
    wallet_hint: str | None
    amount: Decimal | None
    currency: str | None
    transaction_kind: TransactionKind | None
    category_hint: str | None
    description: str | None
    date: datetime.date | None
    confidence: float
    requires_confirmation: bool
    validation_status: ValidationStatus

    @classmethod
    def from_model(cls, model: ParsedTransaction) -> "ParsedTransactionType":
        return cls(
            raw_text=model.raw_text,
            wallet_hint=model.wallet_hint,
            amount=model.amount,
            currency=model.currency,
            transaction_kind=model.transaction_kind,
            category_hint=model.category_hint,
            description=model.description,
            date=model.date,
            confidence=model.confidence,
            requires_confirmation=model.requires_confirmation,
            validation_status=model.validation_status,
        )


@strawberry.type
class ValidatedTransactionType:
    event_id: uuid.UUID | None
    raw_text: str
    wallet_id: uuid.UUID | None
    wallet_name: str | None
    category_id: uuid.UUID | None
    category_name: str | None
    amount: Decimal | None
    currency: str | None
    transaction_kind: TransactionKind | None
    description: str | None
    date: datetime.date | None
    confidence: float
    requires_confirmation: bool
    unresolved_fields: list[str]
    validation_status: ValidationStatus

    @classmethod
    def from_model(cls, model: ValidatedTransaction) -> "ValidatedTransactionType":
        return cls(
            event_id=model.event_id,
            raw_text=model.raw_text,
            wallet_id=model.wallet_id,
            wallet_name=model.wallet_name,
            category_id=model.category_id,
            category_name=model.category_name,
            amount=model.amount,
            currency=model.currency,
            transaction_kind=model.transaction_kind,
            description=model.description,
            date=model.date,
            confidence=model.confidence,
            requires_confirmation=model.requires_confirmation,
            unresolved_fields=model.unresolved_fields,
            validation_status=model.validation_status,
        )


@strawberry.input
class CompleteAiTransactionEventInput:
    event_id: uuid.UUID
    status: AiTransactionEventStatus
    corrected_fields: list[str] = strawberry.field(default_factory=list)
    transaction_id: uuid.UUID | None = None
    wallet_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    amount: Decimal | None = None
    currency: str | None = None
    transaction_kind: TransactionKind | None = None
    description: str | None = None
    date: datetime.date | None = None
