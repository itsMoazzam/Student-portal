from rest_framework.permissions import BasePermission

class IsStudent(BasePermission):
    """
    Allows access only to users who are NOT admin/staff.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and not request.user.is_staff
