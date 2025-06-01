# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from pgvector.django import VectorField


class PizzaRequest(models.Model):
    name = models.CharField(max_length=255)
    ingredients = models.TextField(help_text="JSON строка с ингредиентами")
    description = models.TextField()
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def ingredients_list(self):
        return [i.strip() for i in self.ingredients.split('\n') if i.strip()]


class Pizzas(models.Model):
    name = models.TextField(unique=True)
    pizza_size = models.FloatField()
    crust_size = models.FloatField()
    request = models.OneToOneField(PizzaRequest, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'pizzas'


class Ingredients(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        db_table = 'ingredients'


class PizzaComposition(models.Model):
    pizza = models.OneToOneField('Pizzas', models.CASCADE, primary_key=True)  # The composite primary key (pizza_id, ingredient_id) found, that is not supported. The first column is selected.
    ingredient = models.ForeignKey(Ingredients, models.DO_NOTHING)

    class Meta:
        db_table = 'pizza_composition'
        unique_together = (('pizza', 'ingredient'),)


class PizzaEmbeddings(models.Model):
    pizza = models.ForeignKey('Pizzas', on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='pizza_images/')
    vector = VectorField(dimensions=256, blank=True, null=True)  # поле для хранения эмбеддинга 256 длиной

    def __str__(self):
        return f"Embedding for {self.pizza.name if self.pizza else 'Unknown'}"

    class Meta:
        db_table = 'pizza_embeddings'


