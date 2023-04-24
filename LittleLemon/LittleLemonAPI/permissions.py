from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name= "Manager").exists()
    def __str__(self) -> str:
        return "Manager Group"

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name= "Delivery Crew").exists()
    def __str__(self) -> str:
        return "DC Group"
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name= "Customer").exists()
    def __str__(self) -> str:
        return "Customer Group"
