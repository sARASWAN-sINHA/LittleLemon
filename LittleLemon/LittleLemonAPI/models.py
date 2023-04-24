from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone as tz

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length= 255, db_index=True)

    def __str__(self) -> str:
        return f"{self.title}"

class MenuItem(models.Model):
    title = models.CharField(max_length= 255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField()
    category = models.ForeignKey(to=Category, on_delete=models.PROTECT)
    
    
    def __str__(self) -> str:
        return f"{self.title}"

class Cart(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(to=MenuItem, on_delete=models.CASCADE, default=1)
    quantity = models.IntegerField()

    @property
    def price(self):
        return self.quantity * self.menu_item.price
    

    def __str__(self) -> str:
        return f'{self.user}\'s cart'

    class Meta:
        unique_together = ['user', 'menu_item']

class Order(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(to=User, related_name = 'delivery_crew', on_delete=models.SET_NULL, null=True)
    status = models.BooleanField(db_index=True, default=False)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    date = models.DateTimeField(db_index=True, default=tz.now())

    def __str__(self) -> str:
        return f'{self.user}\'s order'


class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, related_name = "order_item", on_delete=models.CASCADE)
    menu_item = models.ForeignKey(to=MenuItem, on_delete=models.CASCADE, default=1)
    quantity = models.IntegerField()

    class Meta:
        unique_together = ['order', 'menu_item']
