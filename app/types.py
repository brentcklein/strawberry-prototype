from random import random
from typing import Optional, List

import strawberry

from graphql import GraphQLResolveInfo

from app.permissions import AdminPermission


# Define GraphQL types
@strawberry.type
class User:
    name: str
    age: int
    nickname: Optional[str]

    # @strawberry.field marks a method as a "resolver" in graphql parlance
    # Specifying this as a resolver causes it to be calculated only when requested by the client
    @strawberry.field(permission_classes=[AdminPermission])
    def rating(self, info: GraphQLResolveInfo) -> float:
        return random()


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
