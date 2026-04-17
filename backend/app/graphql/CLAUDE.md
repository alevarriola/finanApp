# GraphQL Layer - Guide for Claude Agents

## Purpose
All GraphQL modules live here. Each domain has its own directory.

## Module Structure

```
app/graphql/<module>/
├── __init__.py
├── enums.py                        # IntEnum classes
├── models/                         # SQLAlchemy models
├── repositories/                   # DB access only (flush, never commit)
├── services/                       # Business logic + permission checks
├── types/                          # Strawberry input/output types
├── queries/                        # @strawberry.field resolvers
└── mutations/                      # @strawberry.mutation resolvers
```

## Enum Pattern

```python
import enum
import strawberry

@strawberry.enum
class WalletKind(enum.IntEnum):
    CASH = 1
    BANK = 2
    DEBIT = 3
    CREDIT = 4
```

Always use `IntEnum` - stored as SMALLINT in PostgreSQL via `IntEnumType` from `app/db/types.py`.

## Strawberry Type Pattern

```python
@strawberry.type
class WalletType:
    id: uuid.UUID
    name: str
    wallet_kind: WalletKind
    current_balance: Decimal
    created_at: datetime.datetime

    @classmethod
    def from_model(cls, model: Wallet, my_user_id: uuid.UUID) -> "WalletType":
        return cls(...)
```

## Query Pattern

```python
import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject

@strawberry.type
class WalletQueries:
    @strawberry.field
    @inject
    async def wallets(self, service: Injected[WalletService]) -> list[WalletType]:
        wallets = await service.get_user_wallets()
        return [WalletType.from_model(w, service.auth_info.user_id) for w in wallets]
```

Note: `Injected` is imported from `aioinject`, not from `aioinject.ext.strawberry`.

## Mutation Pattern

```python
@strawberry.type
class WalletMutations:
    @strawberry.mutation
    @inject
    async def create_wallet(
        self,
        input: CreateWalletInput,
        service: Injected[WalletService],
    ) -> WalletType:
        try:
            wallet = await service.create_wallet(...)
        except NotFoundError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 404})
        except UnauthorizedError as e:
            raise GraphQLError(str(e), extensions={"statusCode": 403})
        return WalletType.from_model(wallet, service.auth_info.user_id)
```

## GraphQL Errors

```python
from graphql import GraphQLError  # NOT from strawberry.types

raise GraphQLError(
    message="Wallet not found",
    extensions={"statusCode": 404, "type": "NotFoundError"},
)
```

## Registering in the Main Schema (`schemas/schema.py`)

```python
@strawberry.type
class Query(UserQueries, WalletQueries, NewModuleQueries):
    pass

@strawberry.type
class Mutation(AuthMutations, WalletMutations, NewModuleMutations):
    pass
```

## Modules

| Module | Phase | Status |
|--------|-------|--------|
| `users` | 2 | Done - register, login, me, updateProfile, changePassword |
| `wallets` | 3 | Done - CRUD, roles, walletMembers, leaveWallet, idempotency key |
| `transactions` | 4 | Done - create, list, allTransactions, delete, balance, idempotency key |
| `categories` | 4 | Done - global defaults + per-user, no icon field |
| `invitations` | 5 | Done - invite, accept, reject, cancel; received/sent queries |
| `reports` | 6 | Done - dashboardSummary with period/wallet/category filters |
| `ai_chat` | 8 | In progress but functional - natural-language transaction preview + confirmation flow |

## `ai_chat` Notes

Current GraphQL surface:
- `parseTransaction(text: String!)` → `ParsedTransactionType`
- `validateTransaction(text: String!)` → `ValidatedTransactionType`

Expected mutation behavior:
- convert internal typed failures to `GraphQLError` with `statusCode` and `type`
- current `ai_chat` error types include:
  - `FeatureLockedError`
  - `RateLimitError`
  - `SuspiciousPromptError`
  - `AiInputError`
  - `AiProviderError`

Design rule:
- `parseTransaction` and `validateTransaction` are preview-oriented
- the actual DB write still belongs to `transactions.create_transaction`
- do not duplicate transaction persistence logic inside `ai_chat`
