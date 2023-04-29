from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from django.contrib.auth.models import User

from .models import Cart, MenuItem, Category, Order, OrderItem
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug', 'title']

class MenuItemSerilaizer(serializers.ModelSerializer):

    category = CategorySerializer(read_only = True)
    category_id = serializers.IntegerField(write_only = True)

    class Meta:
        model = MenuItem
        fields = ['title', 'price','featured','category', 'category_id','id']

  
    
    def to_representation(self, item):
        item = super().to_representation(item)
        category_data = item.pop('category')
        item['category'] = category_data.get('title', "No catgory found!!")
        return item
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']

class CartSerializer(serializers.ModelSerializer):

    menu_item = MenuItemSerilaizer(read_only=True)
    menu_item_id = serializers.IntegerField(write_only=True)


    user = UserSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['user', 'menu_item', 'quantity', 'menu_item_id', 'price']

    def to_representation(self, cart_item):
        cart_item = super().to_representation(cart_item)

        menu_item_price = cart_item.get('menu_item').pop('price')
        cart_item['unit_price'] = menu_item_price

        cart_user = cart_item.pop('user')
        user_full_name= cart_user.get('first_name') + " " + cart_user.get('last_name')

        if user_full_name == " ": 
           user_full_name = "User"

        
        user_email = cart_user.get('email', "No email linked to  the user") 

        cart_item['user'] = {
            'full_name': user_full_name,
            'email': user_email,
        }
        return cart_item


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerilaizer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ('order','menu_item','quantity',)
    

        


class OrderSerializer(serializers.ModelSerializer):

    order_items = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ('id', 'user','delivery_crew','status', 'order_items', 'total','date')
        # read_only = ['total', 'delivery_crew','status', 'order_items', 'total','date']


    def get_order_items(self, order):
        order_items = order.order_item.all()
        return OrderItemSerializer(instance=order_items, many=True).data


class ManagerOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id','delivery_crew','status')

    def validate(self, data):
        delivery_crew = data.get('delivery_crew', None)
        if delivery_crew.groups.filter(name='Delivery Crew').exists() == False:
            raise ValidationError(message={"message": "Should be a delivery agent!"})
        return super().validate(data)


class DeliveryCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id','status',)
