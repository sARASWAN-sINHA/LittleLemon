
from django.contrib.auth.models import Group, User


from .models import Cart

def get_group(group_name: str) -> Group:
    return Group.objects.get(name=group_name)

def belongs_to_manager_group(user: User) -> bool:
    return user.groups.filter(name="Manager").exists()

def belongs_to_customer_group(user: User)-> bool:
    return user.groups.filter(name="Customer").exists()

def belongs_to_delivery_crew_group(user: User)-> bool:
    return user.groups.filter(name="Delivery Crew").exists()

def remove_user_from_group(user: User, group: Group):
    user.groups.remove(group)
    group.user_set.remove(user)

def add_user_to_group(user: User, group: Group):
    user.groups.add(group)

    if belongs_to_customer_group(user):
        customer_group = get_group(group_name='Customer')
        remove_user_from_group(user, customer_group)

def add_user_to_manager_group(user: User, group: Group):
    add_user_to_group(user, group)

    if belongs_to_delivery_crew_group(user):
        delivery_group = get_group(group_name='Delivery Crew')
        remove_user_from_group(user, delivery_group)

def add_user_to_delivery_crew_group(user: User, group: Group):
    add_user_to_group(user, group)


def get_user_cart(user: User):
    return Cart.objects.filter(user=user)

def check_empty_cart(user: User) ->bool:
    return get_user_cart(user).exists()==False

def clear_user_cart(user: User) -> str:
    if check_empty_cart(user):
        return "Cart already empty!"
    get_user_cart(user).delete()
    return "Cart cleared!"
    




