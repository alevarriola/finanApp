import aioinject
import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from strawberry.fastapi import GraphQLRouter

from app.core.middleware.graphql_middleware import GraphQLAuthMiddleware
from app.graphql.categories.mutations.category_mutations import CategoryMutations
from app.graphql.invitations.mutations.invitation_mutations import InvitationMutations
from app.graphql.categories.queries.category_queries import CategoryQueries
from app.graphql.invitations.queries.invitation_queries import InvitationQueries
from app.graphql.transactions.mutations.transaction_mutations import TransactionMutations
from app.graphql.transactions.queries.transaction_queries import TransactionQueries
from app.graphql.users.mutations.auth_mutations import AuthMutations
from app.graphql.users.queries.user_queries import UserQueries
from app.graphql.reports.queries.report_queries import ReportQueries
from app.graphql.wallets.mutations.wallet_mutations import WalletMutations
from app.graphql.wallets.queries.wallet_queries import WalletQueries


@strawberry.type
class Query(UserQueries, WalletQueries, CategoryQueries, TransactionQueries, InvitationQueries, ReportQueries):
    pass


@strawberry.type
class Mutation(AuthMutations, WalletMutations, CategoryMutations, TransactionMutations, InvitationMutations):
    pass


def create_graphql_router(container: aioinject.Container) -> GraphQLRouter:
    schema = strawberry.Schema(
        query=Query,
        mutation=Mutation,
        extensions=[
            AioInjectExtension(container=container),
            GraphQLAuthMiddleware,
        ],
    )
    return GraphQLRouter(schema, graphql_ide="graphiql")
