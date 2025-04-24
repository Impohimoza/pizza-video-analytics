# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from pgvector.django import VectorField


class Ingredients(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'ingredients'


class PizzaComposition(models.Model):
    pizza = models.OneToOneField('Pizzas', models.DO_NOTHING, primary_key=True)  # The composite primary key (pizza_id, ingredient_id) found, that is not supported. The first column is selected.
    ingredient = models.ForeignKey(Ingredients, models.DO_NOTHING)
    quantity = models.IntegerField()

    class Meta:
        managed = False
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


class Pizzas(models.Model):
    name = models.TextField(unique=True)
    crust_percentage = models.FloatField()

    class Meta:
        managed = False
        db_table = 'pizzas'


