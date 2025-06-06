from django.db import models
from pizzaRegister.models import Pizzas, Ingredients
from django.conf import settings
import uuid


class PizzeriaLocation(models.Model):
    address = models.CharField(max_length=255)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    stream_url = models.TextField(blank=True, null=True) 

    def __str__(self):
        return self.address


class Evaluation(models.Model):
    pizza = models.ForeignKey(Pizzas, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(PizzeriaLocation, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='evaluation_photos/')
    date = models.DateTimeField(auto_now_add=True)
    quality_percentage = models.FloatField()
    crust_percentage = models.FloatField()  # <--- ДОБАВИЛИ процент корки

    def __str__(self):
        return f"{self.pizza.name} - {self.date.strftime('%d.%m.%Y %H:%M')}"


class IngredientEvaluation(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='ingredient_evaluations')
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)  # <--- СВЯЗЫВАЕМ с моделью ингредиентов
    detected_quantity = models.IntegerField()
    expected_quantity = models.IntegerField()


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Уведомление для {self.user.username}"