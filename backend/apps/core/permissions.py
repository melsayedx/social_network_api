"""Custom permissions for the API."""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    
    Assumes the model has a `user` field that references the owner.
    """
    
    def has_object_permission(self, request, view, obj) -> bool:
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """Permission that only allows owners to access the object."""
    
    def has_object_permission(self, request, view, obj) -> bool:
        return obj.user == request.user
