from django.db.models.signals import post_save
from django.contrib import auth
from django.contrib.auth.models import Group
from django.dispatch import receiver


@receiver(signal=post_save, sender = auth.get_user_model())
def add_user_to_customer(sender, instance, created, **kwargs):
    customer_group = Group.objects.get(name='Customer')
    instance.groups.add(customer_group)
    
