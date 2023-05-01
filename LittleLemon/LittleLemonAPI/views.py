from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, Sum
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend


from .serializers import (CategorySerializer, 
                          DeliveryCrewOrderSerializer, 
                          ManagerOrderSerializer, 
                          MenuItemSerilaizer, 
                          OrderSerializer, 
                          SetFeaturedSerializer, 
                          UserSerializer, 
                          CartSerializer)

from .models import (Category, 
                     MenuItem,
                     OrderItem, 
                     Order)

from .permissions import (IsDeliveryCrew, 
                          IsManager, 
                          IsCustomer)

from .utils import (belongs_to_customer_group, check_empty_cart, clear_user_cart, get_group, 
                    belongs_to_delivery_crew_group, 
                    belongs_to_manager_group, get_user_cart,
                    remove_user_from_group,
                    add_user_to_manager_group,
                    add_user_to_delivery_crew_group)

class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerilaizer
    filter_backends=(OrderingFilter, SearchFilter, DjangoFilterBackend)
    filterset_fields = ('category')
    ordering_fields = ['price']
    search_fields = ['title']
    pagination_class = PageNumberPagination

    def get_permissions(self):

        permission_classes = []

        if self.request.method in SAFE_METHODS:
            permission_classes +=  [IsAuthenticated, (IsAdminUser| IsManager| IsDeliveryCrew | IsCustomer )]
        else:
            permission_classes +=  [IsAuthenticated, (IsAdminUser | IsManager)]
        
        return [permission_class() for permission_class in permission_classes]


class ManagerViewSet(ListModelMixin, GenericViewSet):
      
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    manager_group = get_group(group_name="Manager")

    def get_queryset(self):
        managers = [manager for manager in self.manager_group.user_set.all()]
        return managers
    

    def get_object(self):

        user_id = None
        if self.action == 'destroy':
            user_id = self.kwargs.get("pk", None)
        else:
            user_id = self.request.data.get('id', None)
        
        if user_id:
            user = get_object_or_404(User, id=user_id)
            return user
        raise ValidationError({"id": "Id cannot be empty/NULL/None."})
    

    def create(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            if belongs_to_manager_group(user):
                return Response({'message': 'user already present in manager group'}, status=status.HTTP_200_OK)
            add_user_to_manager_group(user, self.manager_group)
            return Response({'message': 'user added to the manager group'}, status=status.HTTP_201_CREATED)
        except :
            return Response({'message': 'Please provide a valid userID! User could not be added to the manager group'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):

        try:
            user = self.get_object()
            if not belongs_to_manager_group(user):
                return Response({'message': 'User is not a manager to begin with!'}, status=status.HTTP_200_OK)
            remove_user_from_group(user, self.manager_group)
            return Response({'message': 'user removed from the manager group'}, status=status.HTTP_201_CREATED)   
        except :
            return Response({'message': 'Please provide a valid userID! User could not be removed from the manager\'s group'}, status=status.HTTP_400_BAD_REQUEST)


class DeliveryCrewViewSet(ListModelMixin, GenericViewSet):
      
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser | IsManager]

    delivery_crew_group = get_group(group_name='Delivery Crew')

    def get_queryset(self):
        delivery_crew = [dc for dc in self.delivery_crew_group.user_set.all()]
        return delivery_crew
    
    def get_object(self):
        user_id = None
        if self.action == 'destroy':
            user_id = self.kwargs.get("pk", None)
        else:
            user_id = self.request.data.get('id', None)
        
        if user_id:
            user = get_object_or_404(User, id=user_id)
            return user
        raise ValidationError({"id": "Id cannot be empty/NULL/None."})


    def create(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            if belongs_to_manager_group(user):
                return Response({'message': 'user in manager group! Cannot perform this action!'}, status=status.HTTP_400_BAD_REQUEST)
            if belongs_to_delivery_crew_group(user):
                return Response({'message': 'user already present in delivery crew group'}, status=status.HTTP_200_OK)
            add_user_to_delivery_crew_group(user, self.delivery_crew_group)
            return Response({'message': 'user added to the delivery crew group'}, status=status.HTTP_201_CREATED)
        except :
            return Response({'message': 'Please provide a valid userID! User could not be added to the delivery crew group'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            if not belongs_to_delivery_crew_group(user):
                return Response({'message': 'User is not among Delivery Crew to begin with!'}, status=status.HTTP_200_OK)
            remove_user_from_group(user, self.delivery_crew_group)
            return Response({'message': 'user removed from the delivery crew group group'}, status=status.HTTP_201_CREATED)
        except:
            return Response({'message': 'Please provide a valid userID! User could not be removed from the delivery crew\'s group'}, status=status.HTTP_400_BAD_REQUEST)


class CustomerView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )
    
    customer_group = get_group(group_name='Customer')
    
    def get_queryset(self):
        customers = [customer for customer in self.customer_group.user_set.all()]
        return customers


class CartViewSet(ListModelMixin, GenericViewSet):
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, (IsCustomer | IsAdminUser)]
    
    def get_queryset(self):
        return get_user_cart(self.request.user)
    
    def create(self, request, *args, **kwargs):

        serializer_data = CartSerializer(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        serializer_data.save(user = request.user)
        return Response({'message': 'Item added to cart succesfully!'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['DELETE'])
    def clear_cart(self, request, *args, **kwargs):
        try:
            response_message = clear_user_cart(request.user)
            return Response({'message': response_message}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'message': f'Could not clear cart. Error:- {str(e)}'})
        


class OrderViewSet(UpdateModelMixin, ListModelMixin, GenericViewSet):
    
    serializer_class = OrderSerializer

    def get_permissions(self):
        permission_classes = []
       
        if self.action== 'create':
            permission_classes += [IsAuthenticated, IsCustomer]
        else:
            permission_classes += [IsAuthenticated, (IsCustomer| IsDeliveryCrew| IsManager| IsAdminUser)]

        return [permission_class() for permission_class in permission_classes]

    def get_queryset(self):
        if belongs_to_manager_group(self.request.user) or self.request.user.is_superuser:
            return Order.objects.all()
        elif belongs_to_delivery_crew_group(self.request.user):
            return Order.objects.filter(delivery_crew = self.request.user)
        elif belongs_to_customer_group(self.request.user):
            return Order.objects.filter(user = self.request.user)
        return Order.objects.none()
    
    def create(self, request, *args, **kwargs):
        if check_empty_cart(request.user):
            return Response({'message': 'Cart is empty!'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.create(user = request.user)
        except Exception as e:
            return Response({'message': f'Failed to create order. Error:- {str(e)}'})

        try:    
            cart_items = get_user_cart(user=request.user)
            order_items = [OrderItem(order=order, menu_item=cart_item.menu_item, quantity=cart_item.quantity) for cart_item in cart_items]
            OrderItem.objects.bulk_create(order_items)
            order.total = cart_items.aggregate(amt=Sum(F('menu_item__price') * F('quantity')))['amt']
            order.save()
            serialized_order = OrderSerializer(instance=order)
            clear_user_cart(user=request.user)
            return Response(serialized_order.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            Order.objects.get(id=order.id).delete()
            return Response({'message': f'Action could not be completed. Error:- {str(e)}'})
        
    def retrieve(self, request, pk, *args, **kwargs):
        if belongs_to_customer_group(request.user) or belongs_to_manager_group(request.user) or request.user.is_superuser:
            try:
                order_item = self.get_object()
                serialized_order_item = OrderSerializer(instance=order_item)
                return Response(serialized_order_item.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': f'Failed to retrieve data. Error:- {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)     
        else:
            return Response({'message': 'Only Managers and Customers are allowed to perform this action'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, *args, **kwargs):
                
        if belongs_to_delivery_crew_group(request.user) or belongs_to_manager_group(request.user):
            try:
                order_item = self.get_object()
                serialized_order_item = None

                if belongs_to_manager_group(request.user):
                    serialized_order_item = ManagerOrderSerializer(instance=order_item, data=request.data, partial=True)
                if belongs_to_delivery_crew_group(request.user):
                    serialized_order_item = DeliveryCrewOrderSerializer(instance=order_item, data=request.data, partial=True)
                
                
                serialized_order_item.is_valid(raise_exception=True)
                serialized_order_item.save()
                return Response(serialized_order_item.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': f"Failed to update data. Error:- {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "You don't have permission to perform this action."}, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method not in  SAFE_METHODS:
            permission_classes += [IsAdminUser]
        
        return [permission_class() for permission_class in permission_classes]

class SetFeaturedView(UpdateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = SetFeaturedSerializer
    
