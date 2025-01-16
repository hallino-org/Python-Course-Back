from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Only allow staff members to edit objects.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Only allow authors of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Assuming the object has an author field that's related to Course authors
        if hasattr(obj, 'chapter'):
            return request.user in obj.chapter.course.authors.all()
        elif hasattr(obj, 'course'):
            return request.user in obj.course.authors.all()
        return False


class IsCourseAuthorOrReadOnly(permissions.BasePermission):
    """
    Only course authors allowed.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user in obj.authors.all()
