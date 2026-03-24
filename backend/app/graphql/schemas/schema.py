import aioinject
import strawberry
from aioinject.ext.strawberry import AioInjectExtension
from strawberry.fastapi import GraphQLRouter

from app.core.middleware.graphql_middleware import GraphQLAuthMiddleware
from app.graphql.users.mutations.auth_mutations import AuthMutations
from app.graphql.users.queries.user_queries import UserQueries


@strawberry.type
class Query(UserQueries):
    pass


@strawberry.type
class Mutation(AuthMutations):
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
