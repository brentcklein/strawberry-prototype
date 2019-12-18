from typing import Optional, List, Type

import strawberry
from strawberry.field import strawberry_field

from app.permissions import LocalPermission, XometryPermission


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
