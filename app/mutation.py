from typing import Optional

import strawberry

from graphql import GraphQLResolveInfo

from app.db import xometry, customer_group
from app.decorators import local_mutation
from app.permissions import AdminPermission, GandalfPermission
from app.types import User, UserGroup, Company


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
