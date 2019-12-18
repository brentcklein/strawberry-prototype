import strawberry

from strawberry.asgi import GraphQL as ASGIGraphQL

from app.mutation import Mutation
from app.query import Query

# This is the strawberry executable schema as demonstrated in the tutorial
schema = strawberry.Schema(query=Query, mutation=Mutation)

# This is the ASGI implementation of the strawberry schema using starlette
app = ASGIGraphQL(schema=schema)
