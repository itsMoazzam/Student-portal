from rest_framework.permissions import BasePermission

class IsSubAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user, 'is_subadmin', False) and
            hasattr(request.user, 'subadmin')
        )
        
class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user, 'is_student', False)
        )
        
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user, 'is_admin', False)
        )        
        
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ['GET', 'HEAD', 'OPTIONS'] or
            obj.user == request.user
        )
        