from rest_framework.permissions import BasePermission

class IsSuperUser(BasePermission):
    """
    Custom permission to allow only superusers to perform any action.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser
    
class IsSuperUserOrReadOnly(BasePermission):
    """
    Custom permission to allow only superusers to perform any action and others to only read.
    """

    def has_permission(self, request, view):
        return (request.user.is_superuser or request.method in ['GET', 'HEAD', 'OPTIONS'])

        
