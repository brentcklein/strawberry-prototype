import random
from abc import ABC
from typing import List, Optional, Type

import strawberry
from graphql import GraphQLResolveInfo
from starlette.datastructures import Headers as StarletteHeaders
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

    # @strawberry.field marks a method as a "resolver" in graphql parlance
    # Specifying this as a resolver causes it to be calculated only when requested by the client
    @strawberry.field
    def rating(self, info: GraphQLResolveInfo) -> float:
        return random.random()


@strawberry.type
class UserGroup:
    name: str
    users: List[User]

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self.users = []


@strawberry.type
class Company:
    name: str
    user_groups: List[UserGroup]

    def __init__(self, name: str) -> None:
        self.name = name
        self.user_groups = []

    def get_user_group(self, name: Optional[str]) -> Optional[UserGroup]:
        group_names = [user_group.name for user_group in self.user_groups]
        try:
            if name is None:
                name = ""
            group_index = group_names.index(name)
            return self.user_groups[group_index]
        except ValueError:
            return None


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


class AdminPermission(XometryPermission):
    """Check to make sure the user is a member of the admin UserGroup"""
    def has_permission(self, info: GraphQLResolveInfo) -> bool:
        # Checking an arbitrary header as an example. strawberry uses starlette ASGI adapter to handle requests.
        headers: StarletteHeaders = info.context['request'].headers
        is_admin = headers.get('user_group', None) == "admins"
        if not is_admin:
            self.message = "Unauthorized. Must be admin."
        return is_admin


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
xometry = Company(name='Xometry')

xometry.user_groups.append(UserGroup(name='admins'))
xometry.user_groups.append(UserGroup(name='customers'))

admin_group = xometry.user_groups[0]
admins = admin_group.users
admins.append(User(name="Bob", age=50, nickname=None))
admins.append(User(name="Joe", age=30, nickname="Joey"))

customer_group = xometry.user_groups[1]
customers = customer_group.users
customers.append(User(name="Sally", age=40, nickname=None))
customers.append(User(name="Bill", age=35, nickname="Billy"))


# Define Query type and fields
@strawberry.type
class Query:
    # This field has no permissions attached
    @strawberry.field
    def users(self, info: GraphQLResolveInfo, group: str = None) -> List[User]:
        if group is None:
            return admins+customers

        user_group: Optional[UserGroup] = xometry.get_user_group(group)
        if user_group is None:
            return []
        return user_group.users

    # This is equivalent to @local_field
    @strawberry.field(permission_classes=[LocalPermission])
    def groups(self, info: GraphQLResolveInfo) -> List[UserGroup]:
        return xometry.user_groups


# Define Mutation type and methods
@strawberry.type
class Mutation:
    # Note custom field decorator that enforces LocalPermission
    @local_mutation
    def add_user(
            self,
            info: GraphQLResolveInfo,
            name: str,
            age: int,
            nickname: str = None,
            group: str = None
    ) -> User:
        user = User(name=name, age=age, nickname=nickname)
        user_group: Optional[UserGroup] = xometry.get_user_group(group)
        if user_group is None:
            user_group = customer_group
        user_group.users.append(user)
        return user

    # custom decorators can accept additional permissions
    @local_mutation(permission_classes=[AdminPermission])
    def add_group(self, info: GraphQLResolveInfo, name: str) -> UserGroup:
        group: UserGroup = UserGroup(name=name)
        xometry.user_groups.append(group)
        return group

    @local_mutation(permission_classes=[GandalfPermission])
    def add_company(self, info: GraphQLResolveInfo) -> Company:
        # Implementing to demonstrate permissions
        pass


# This is the strawberry executable schema as demonstrated in the tutorial
schema = strawberry.Schema(query=Query, mutation=Mutation)

# This is the ASGI implementation of the strawberry schema using starlette
app = ASGIGraphQL(schema=schema)
