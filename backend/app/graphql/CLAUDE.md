# GraphQL Layer — Guide for Claude Agents

## Purpose
Exposes all FinanApp API as GraphQL. Each domain has its own directory with the standard structure.

## Module Structure

```
app/graphql/wallets/
├── __init__.py
├── enums.py                        # IntEnum classes (WalletType, etc.)
├── models/
│   └── wallet.py                   # SQLAlchemy model
├── repositories/
│   └── wallet_repository.py        # WalletRepository — DB access only
├── services/
│   └── wallet_service.py           # WalletService — business logic only
├── types/
│   └── wallet_types.py             # WalletType, CreateWalletInput, UpdateWalletInput
├── queries/
│   └── wallet_queries.py           # WalletQueries (@strawberry.field)
└── mutations/
    └── wallet_mutations.py         # WalletMutations (@strawberry.mutation)
```

## Strawberry Type Pattern

```python
# types/wallet_types.py
import strawberry
import uuid
import datetime
from decimal import Decimal

@strawberry.type
class WalletType:
    id: uuid.UUID
    name: str
    balance: Decimal
    created_at: datetime.datetime

    @classmethod
    def from_model(cls, model: "Wallet") -> "WalletType":
        return cls(
            id=model.id,
            name=model.name,
            balance=model.balance,
            created_at=model.created_at,
        )

@strawberry.input
class CreateWalletInput:
    name: str
    initial_balance: Decimal
    wallet_type: str
    currency: str = "PYG"
```

## Query Pattern

```python
# queries/wallet_queries.py
import strawberry
import uuid
from aioinject.ext.strawberry import inject, Injected

@strawberry.type
class WalletQueries:
    @strawberry.field
    @inject
    async def get_wallet(
        self,
        wallet_id: uuid.UUID,
        service: Injected["WalletService"],
    ) -> WalletType | None:
        wallet = await service.get_by_id(wallet_id)
        return WalletType.from_model(wallet) if wallet else None

    @strawberry.field
    @inject
    async def list_wallets(
        self,
        service: Injected["WalletService"],
    ) -> list[WalletType]:
        wallets = await service.get_user_wallets()
        return [WalletType.from_model(w) for w in wallets]
```

## Mutation Pattern

```python
# mutations/wallet_mutations.py
import strawberry
from aioinject.ext.strawberry import inject, Injected

@strawberry.type
class WalletMutations:
    @strawberry.mutation
    @inject
    async def create_wallet(
        self,
        input: CreateWalletInput,
        service: Injected["WalletService"],
    ) -> WalletType:
        wallet = await service.create_wallet(
            name=input.name,
            initial_balance=input.initial_balance,
        )
        return WalletType.from_model(wallet)
```

## Registering in the Main Schema

```python
# schemas/schema.py — add to merge_types
from app.graphql.wallets.queries.wallet_queries import WalletQueries
from app.graphql.wallets.mutations.wallet_mutations import WalletMutations

Query = merge_types("Query", (WalletQueries, ...others...))
Mutation = merge_types("Mutation", (WalletMutations, ...others...))
```

## Planned Modules

| Module | Phase | Description |
|--------|-------|-------------|
| `users` | Phase 2 | Registration, login, profile |
| `wallets` | Phase 3 | Accounts/wallets |
| `transactions` | Phase 4 | Income and expenses |
| `categories` | Phase 4 | Spending categories |
| `invitations` | Phase 5 | Sharing accounts |

## GraphQL Errors

```python
from strawberry.types import GraphQLError

raise GraphQLError(
    message="Wallet not found",
    extensions={"statusCode": 404, "type": "NotFoundError"},
)
```
