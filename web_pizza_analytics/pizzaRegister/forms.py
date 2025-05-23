from django import forms
from .models import Pizzas, Ingredients, PizzaEmbeddings


class PizzaForm(forms.ModelForm):
    class Meta:
        model = Pizzas
        fields = ['name', 'pizza_size', 'crust_size']


class SinglePizzaImageForm(forms.ModelForm):
    image = forms.ImageField()

    class Meta:
        model = PizzaEmbeddings
        fields = ['image']


class PizzaCompositionForm(forms.Form):
    ingredient = forms.ModelChoiceField(queryset=Ingredients.objects.all(), required=False)
