from django import forms
from .models import Pizzas, Ingredients, PizzaEmbeddings


class PizzaForm(forms.ModelForm):
    class Meta:
        model = Pizzas
        fields = ['name', 'crust_percentage']


class SinglePizzaImageForm(forms.ModelForm):
    image = forms.ImageField()

    class Meta:
        model = PizzaEmbeddings
        fields = ['image']


class PizzaCompositionForm(forms.Form):
    ingredient = forms.ModelChoiceField(queryset=Ingredients.objects.all(), required=False)
    quantity = forms.IntegerField(min_value=1, required=False)

