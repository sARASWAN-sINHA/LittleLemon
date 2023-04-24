from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS
from rest_framework.decorators import action
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F, Sum, Q



from .serializers import MenuItemSerilaizer, OrderSerializer, UserSerializer, CartSerializer
from .models import MenuItem, Cart, OrderItem, Order
from .permissions import IsDeliveryCrew, IsManager, IsCustomer

class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerilaizer

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

    manager_group = Group.objects.get(name="Manager")

    def get_queryset(self):
        managers = [manager for manager in self.manager_group.user_set.all()]
        return managers

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('id', None)
        if user_id:
            user = get_object_or_404(User, id=user_id)

            if user.groups.filter(name="Manager").exists():
                 return Response({'message': 'user already present in manager group'}, status=status.HTTP_200_OK)
            
            user.groups.add(self.manager_group)


            if user.groups.filter("Delivery Crew").exists():
                delivery_group = Group.objects.get(name='Delivery Crew')
                delivery_group.user_set.remove(user)
                user.groups.remove(delivery_group)

            return Response({'message': 'user added to the manager group'}, status=status.HTTP_201_CREATED)
        
        return Response({'message': 'Please provide a valid userID! User could not be added to the manager group'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get('pk', None)

        if user_id:
            user = get_object_or_404(User, id=user_id)


            if user.groups.filter(name="Manager").exists() == False:
                # print(user)
                return Response({'message': 'User is not a manager to begin with!'}, status=status.HTTP_200_OK)
            
            user.groups.remove(self.manager_group)
            self.manager_group.user_set.remove(user)
            return Response({'message': 'user removed from the manager group'}, status=status.HTTP_201_CREATED)
        
        return Response({'message': 'Please provide a valid userID! User could not be removed from the manager\'s group'}, status=status.HTTP_400_BAD_REQUEST)


class DeliveryCrewViewSet(ListModelMixin, GenericViewSet):
      
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser | IsManager]

    delivery_crew_group = Group.objects.get(name="Delivery Crew")

    def get_queryset(self):
        delivery_crew = [dc for dc in self.delivery_crew_group.user_set.all()]
        return delivery_crew

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('id', None)
        if user_id:
            user = get_object_or_404(User, id=user_id)
        

            if user.groups.filter(name="Manager").exists():
                return Response({'message': 'user in manager group! Cannot perform this action!'}, status=status.HTTP_400_BAD_REQUEST)

            
            if user.groups.filter(name="Delivery Crew").exists():
                 return Response({'message': 'user already present in delivery crew group'}, status=status.HTTP_200_OK)
            
            user.groups.add(self.delivery_crew_group)
            return Response({'message': 'user added to the delivery crew group'}, status=status.HTTP_201_CREATED)
        
        return Response({'message': 'Please provide a valid userID! User could not be added to the delivery crew group'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get('pk', None)

        if user_id:
            user = get_object_or_404(User, id=user_id)

            if user.groups.filter(name="Delivery Crew").exists() == False:
                return Response({'message': 'User is not among Delivery Crew to begin with!'}, status=status.HTTP_200_OK)
            
            user.groups.remove(self.delivery_crew_group)
            self.delivery_crew_group.user_set.remove(user)
            return Response({'message': 'user removed from the delivery crew group group'}, status=status.HTTP_201_CREATED)
        
        return Response({'message': 'Please provide a valid userID! User could not be removed from the delivery crew\'s group'}, status=status.HTTP_400_BAD_REQUEST)


class CustomerView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )
    
    customer_group = Group.objects.get(name='Customer')
    
    def get_queryset(self):
        customers = [customer for customer in self.customer_group.user_set.all()]
        return customers


class CartViewSet(ListModelMixin, GenericViewSet):
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, (IsCustomer | IsAdminUser)]
    
    def get_queryset(self):
        return Cart.objects.filter(user = self.request.user)
    
    def create(self, request, *args, **kwargs):

        serializer_data = CartSerializer(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        serializer_data.save(user = request.user)
        return Response({'message': 'Item added to cart succesfully!'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['DELETE'])
    def clear_cart(self, request, *args, **kwargs):
        try:
            Cart.objects.filter(user = request.user).delete()
            return Response({'message': 'Cart cleared!'}, status=status.HTTP_204_NO_CONTENT)
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
        
        # print('applied permission classes', permission_classes)

        return [permission_class() for permission_class in permission_classes]
        # print('applied permission classes', x)
        


    def get_queryset(self):
        if self.request.user.groups.filter(name = 'Manager').exists() or self.request.user.is_superuser:
            return Order.objects.all()
        elif self.request.user.groups.filter(name = 'Delivery Crew').exists():
            return Order.objects.filter(delivery_crew = self.request.user)
        else:
            return Order.objects.filter(user = self.request.user)
    
    def create(self, request, *args, **kwargs):

        cart_items = Cart.objects.filter(user = request.user)
        
        if not cart_items.exists():
            return Response({'message': 'Cart is empty!'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = Order.objects.create(user = request.user)
        except Exception as e:
            return Response({'message': f'Failed to create order. Error:- {str(e)}'})

        try:    
            order_items = [OrderItem(order=order, menu_item=cart_item.menu_item, quantity=cart_item.quantity) for cart_item in cart_items]
            OrderItem.objects.bulk_create(order_items)

            order.total = cart_items.aggregate(amt=Sum(F('menu_item__price') * F('quantity')))['amt']
            
            order.save()

            serialized_order = OrderSerializer(instance=order)

            Cart.objects.filter(user = request.user).delete()

            return Response(serialized_order.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            Order.objects.get(id=order.id).delete()
            return Response({'message': f'Action could not be completed. Error:- {str(e)}'})
        
    def retrieve(self, request, pk, *args, **kwargs):
        if request.user.groups.filter(Q(name='Customer') | Q(name='Manager')).exists() or request.user.is_superuser:
            try:
                order_item = self.get_queryset().filter(id=pk)
                
                if not order_item.exists():
                    return Response({'message': 'No orders found!'}, status=status.HTTP_404_NOT_FOUND)
                
                order_item = order_item.first()
                serialized_order_item = OrderSerializer(instance=order_item)
                return Response(serialized_order_item.data, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({'message': f'Failed to retrieve data. Error:- {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)     
        else:
            return Response({'message': 'Only Managers and Customers are allowed to perform this action'}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk, *args, **kwargs):
        if request.user.groups.filter(name='Customer').exists():
            return super().update(request, args, kwargs)

        
    def partial_update(self, request, pk, *args, **kwargs):
        if request.user.groups.filter(name='Customer').exists():
            return super().partial_update(request, args, kwargs)
        
        if request.user.groups.filter(Q(name='Manager') | Q(name='Delivery Crew')).exists():
            try:
                data = self.get_queryset().filter(id=pk)

                if not data.exists():
                    return Response({'message': 'No orders found!'}, status=status.HTTP_404_NOT_FOUND)
                
                order_item = data.first()
                serialized_order_item = OrderSerializer(instance=order_item, data=request.data)
                serialized_order_item.is_valid(raise_exception=True)
                serialized_order_item.save()
                return Response(serialized_order_item.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': f"Failed to update data. Error:- {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        



        
        



    









        
        


        

    
    

