import random
from abc import ABC
from typing import List, Optional, Type

import strawberry
from graphql import GraphQLResolveInfo
from strawberry import BasePermission
from starlette.requests import Request as StarletteRequest

from strawberry.asgi import GraphQL as ASGIGraphQL
from strawberry.field import strawberry_field


# Define GraphQL types
@strawberry.type
class User:
    name: str
    age: int
    nickname: Optional[str]


@strawberry.type
class UserGroup:
    name: str
    users: List[User]

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self.users = []


# Define Permission classes
class XometryPermission(BasePermission, ABC):
    """
    Base class for all Xometry permissions.
    Inherits from BasePermission, which defines the abstract method has_permission(info: GraphQLResolve) -> bool
    has_permission() should return True if permission is granted, False if not, and can optionally set self.message
    if permission is not granted to provide more information to the user.
    """
    message: str


class LocalPermission(XometryPermission):
    """Check to make sure the user is coming from localhost"""
    def has_permission(self, info: GraphQLResolveInfo) -> bool:
        # Strawberry uses starlette as its ASGI framework
        request: StarletteRequest = info.context['request']
        # Inspect the request to get cookies, check headers, etc
        ret = request.client.host == '127.0.0.1'
        if not ret:
            self.message = "No droids"

        return ret


class GandalfPermission(XometryPermission):
    """No passing zone"""
    def has_permission(self, info: GraphQLResolveInfo) -> bool:
        self.message = "Trying to pass? I don't think you shall."
        return False


# Define custom field decorators to collect reusable permissions
def local_field(
        *args: object,
        permission_classes: Optional[List[Type[XometryPermission]]] = None,
        **kwargs: object
) -> strawberry_field:
    # Append LocalPermission to permission_classes (if provided)
    if permission_classes is None:
        permission_classes = []
    permission_classes.append(LocalPermission)

    return strawberry.field(*args, permission_classes=permission_classes, **kwargs)


# Currently strawberry makes no distinction between fields and mutations, which makes it easy to stay DRY.
# This may change in the future?
local_mutation = local_field


# Define some testing data
accounts = UserGroup(name='customers')
accounts.users.append(User(name="Bob", age=50, nickname=None))
accounts.users.append(User(name="Joe", age=30, nickname="Joey"))


# Define Query type and fields
@strawberry.type
class Query:
    # This field has no permissions attached
    @strawberry.field
    def user(self, info: GraphQLResolveInfo, idx: Optional[int] = None) -> Optional[User]:
        idx = idx % len(accounts.users) if idx is not None else 0
        return accounts.users[idx]

    # This is equivalent to @local_field
    @strawberry.field(permission_classes=[LocalPermission])
    def group(self, info: GraphQLResolveInfo) -> UserGroup:
        return accounts


# Define Mutation type and methods
@strawberry.type
class Mutation:
    # Note custom field decorator that enforces LocalPermission
    @local_mutation
    def add_user(self, info: GraphQLResolveInfo, name: str, age: int, nickname: str = None) -> User:
        user = User(name=name, age=age, nickname=nickname)
        accounts.users.append(user)
        return user

    # custom decorators can accept additional permissions
    @local_mutation(permission_classes=[GandalfPermission])
    def add_group(self, info: GraphQLResolveInfo, name: str) -> UserGroup:
        # Implementing to demonstrate permissions
        pass


# This is the strawberry executable schema as demonstrated in the tutorial
schema = strawberry.Schema(query=Query, mutation=Mutation)

# This is the ASGI implementation of the strawberry schema using starlette
app = ASGIGraphQL(schema=schema)
