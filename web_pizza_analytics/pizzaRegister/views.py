from django.shortcuts import render, redirect, get_object_or_404
from .forms import PizzaForm, SinglePizzaImageForm, PizzaCompositionForm
from .models import Pizzas, PizzaEmbeddings, PizzaComposition
from .keras_model_loader import FeatureExtractor
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def add_pizza(request):
    error_message = None

    if request.method == 'POST':
        pizza_form = PizzaForm(request.POST)
        image_forms = [SinglePizzaImageForm(request.POST, request.FILES, prefix=str(i)) for i in range(5)]
        composition_forms = [PizzaCompositionForm(request.POST, prefix=str(i)) for i in range(10)]

        if pizza_form.is_valid() and all(f.is_valid() for f in image_forms) and all(cf.is_valid() for cf in composition_forms):
            # Проверка: нет ли уже пиццы с таким названием
            name = pizza_form.cleaned_data['name']
            if Pizzas.objects.filter(name__iexact=name).exists():
                error_message = f"Пицца с названием '{name}' уже существует."
            else:
                # Проверка на дубли ингредиентов
                selected_ingredients = []
                for cf in composition_forms:
                    ingredient = cf.cleaned_data.get('ingredient')
                    if ingredient:
                        if ingredient.id in selected_ingredients:
                            error_message = f"Ингредиент '{ingredient.name}' выбран несколько раз."
                            break
                        selected_ingredients.append(ingredient.id)

                if not error_message:
                    pizza = pizza_form.save()

                    # Сохраняем ингредиенты
                    for cf in composition_forms:
                        ingredient = cf.cleaned_data.get('ingredient')
                        quantity = cf.cleaned_data.get('quantity')
                        if ingredient and quantity:
                            PizzaComposition.objects.create(pizza=pizza, ingredient=ingredient, quantity=quantity)

                    # Сохраняем изображения и эмбеддинги
                    feature_extractor = FeatureExtractor()
                    for img_form in image_forms:
                        if img_form.cleaned_data.get('image'):
                            pizza_image = PizzaEmbeddings.objects.create(pizza=pizza, image=img_form.cleaned_data['image'])
                            embedding = feature_extractor.extract(pizza_image.image.path)
                            pizza_image.vector = embedding
                            pizza_image.save()

                    return redirect('pizza_list')

    else:
        pizza_form = PizzaForm()
        image_forms = [SinglePizzaImageForm(prefix=str(i)) for i in range(5)]
        composition_forms = [PizzaCompositionForm(prefix=str(i)) for i in range(10)]

    return render(request, 'pizzaRegister/pizza_form.html', {
        'pizza_form': pizza_form,
        'image_forms': image_forms,
        'composition_forms': composition_forms,
        'error_message': error_message,
    })


@login_required(login_url='/login/')
def pizza_list(request):
    pizzas = Pizzas.objects.all()
    return render(request, 'pizzaRegister/pizza_list.html', {'pizzas': pizzas})


@login_required(login_url='/login/')
def pizza_detail(request, pizza_id):
    pizza = get_object_or_404(Pizzas, id=pizza_id)
    compositions = PizzaComposition.objects.filter(pizza=pizza)
    images = PizzaEmbeddings.objects.filter(pizza=pizza)
    print(images)
    return render(request, 'pizzaRegister/pizza_detail.html', {
        'pizza': pizza,
        'compositions': compositions,
        'images': images,
    })


@login_required(login_url='/login/')
def delete_pizza(request, pizza_id):
    pizza = get_object_or_404(Pizzas, id=pizza_id)
    pizza.delete()
    return redirect('pizza_list')

