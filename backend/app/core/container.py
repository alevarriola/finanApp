import aioinject
from aioinject.ext.fastapi import FastAPIExtension
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.auth.auth_info import AuthInfo
from app.auth.jwt_service import JWTService
from app.core.config import Settings, get_settings
from app.core.context import auth_info_var, session_var
from app.db.engine import create_session_factory


def _provide_settings() -> Settings:
    return get_settings()


def _provide_session_factory(settings: Settings) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(settings)


def _create_jwt_service(settings: Settings) -> JWTService:
    return JWTService(settings)


def _provide_session() -> AsyncSession:
    session = session_var.get()
    if session is None:
        raise RuntimeError("No active DB session in context")
    return session


def _provide_auth_info() -> AuthInfo:
    from graphql import GraphQLError

    auth_info = auth_info_var.get()
    if auth_info is None:
        raise GraphQLError("Unauthorized", extensions={"statusCode": 401})
    return auth_info


def create_container() -> aioinject.Container:
    container = aioinject.Container(extensions=[FastAPIExtension()])

    container.register(aioinject.Object(_provide_settings()))
    container.register(aioinject.Singleton(_provide_session_factory))
    container.register(aioinject.Singleton(_create_jwt_service))
    container.register(aioinject.Scoped(_provide_session, interface=AsyncSession))
    container.register(aioinject.Scoped(_provide_auth_info, interface=AuthInfo))

    from app.graphql.categories.repositories.category_repository import CategoryRepository
    from app.graphql.categories.services.category_service import CategoryService
    from app.graphql.invitations.repositories.invitation_repository import InvitationRepository
    from app.graphql.invitations.services.invitation_service import InvitationService
    from app.graphql.transactions.repositories.transaction_repository import TransactionRepository
    from app.graphql.transactions.services.transaction_service import TransactionService
    from app.graphql.users.repositories.user_repository import UserRepository
    from app.graphql.users.services.user_service import UserService
    from app.graphql.wallets.repositories.wallet_repository import WalletRepository
    from app.graphql.wallets.services.wallet_service import WalletService

    container.register(aioinject.Scoped(UserRepository))
    container.register(aioinject.Scoped(UserService))
    container.register(aioinject.Scoped(WalletRepository))
    container.register(aioinject.Scoped(WalletService))
    container.register(aioinject.Scoped(CategoryRepository))
    container.register(aioinject.Scoped(CategoryService))
    container.register(aioinject.Scoped(TransactionRepository))
    container.register(aioinject.Scoped(TransactionService))
    container.register(aioinject.Scoped(InvitationRepository))
    container.register(aioinject.Scoped(InvitationService))

    from app.graphql.reports.repositories.report_repository import ReportRepository
    from app.graphql.reports.services.report_service import ReportService

    container.register(aioinject.Scoped(ReportRepository))
    container.register(aioinject.Scoped(ReportService))

    return container
