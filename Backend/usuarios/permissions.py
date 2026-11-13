from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSelfOrAdmin(BasePermission):
    """Solo el dueño del objeto o un admin pueden mutar/ver detalle sensible."""

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        user_id = getattr(obj, 'id', None) or getattr(obj, 'pk', None)
        return bool(request.user and request.user.is_authenticated and user_id == request.user.id)


class IsAdminOrReadSelf(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.method in SAFE_METHODS:
            return obj.id == request.user.id
        return obj.id == request.user.id
