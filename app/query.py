from typing import Optional, List

import strawberry
from graphql import GraphQLResolveInfo

from app.permissions import LocalPermission
from app.types import User, UserGroup

from app.db import xometry, customers


# Define Query type and fields
@strawberry.type
class Query:
    @strawberry.field
    def user(self, info: GraphQLResolveInfo, user_id: str) -> Optional[User]:
        pass

    # This field has no permissions attached
    @strawberry.field
    def users(self, info: GraphQLResolveInfo, group: str = None) -> List[User]:
        if group is None:
            return customers

        user_group: Optional[UserGroup] = xometry.get_user_group(group)
        if user_group is None:
            return []
        return user_group.users

    # This is equivalent to @local_field
    @strawberry.field(permission_classes=[LocalPermission])
    def groups(self, info: GraphQLResolveInfo) -> List[UserGroup]:
        return xometry.user_groups
