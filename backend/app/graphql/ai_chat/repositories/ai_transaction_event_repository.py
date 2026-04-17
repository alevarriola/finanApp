import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.ai_chat.models.ai_transaction_event import AiTransactionEvent


class AiTransactionEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, event: AiTransactionEvent) -> AiTransactionEvent:
        self.session.add(event)
        await self.session.flush()
        return event

    async def save(self, event: AiTransactionEvent) -> AiTransactionEvent:
        await self.session.flush()
        return event

    async def get_by_id(self, event_id: uuid.UUID) -> AiTransactionEvent | None:
        stmt = select(AiTransactionEvent).where(AiTransactionEvent.id == event_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
