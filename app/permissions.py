from abc import ABC

from graphql import GraphQLResolveInfo
from strawberry import BasePermission
from starlette.requests import Request as StarletteRequest, Headers as StarletteHeaders


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
