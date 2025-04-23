from django.shortcuts import render, get_object_or_404
from pizzaRegister.models import Pizzas, Ingredients, PizzaComposition
from .models import Evaluation, PizzeriaLocation, IngredientEvaluation
from django.contrib.auth.decorators import login_required
import openpyxl
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid
import json
from datetime import datetime


# Список всех оценок с фильтрами
@login_required(login_url='/login/')
def evaluation_list(request):
    evaluations = Evaluation.objects.all()

    # Получение параметров фильтрации из запроса
    pizza_id = request.GET.get('pizza')
    location_id = request.GET.get('location')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    quality = request.GET.get('quality')  # <-- новый параметр

    if pizza_id:
        evaluations = evaluations.filter(pizza_id=pizza_id)
    if location_id:
        evaluations = evaluations.filter(location_id=location_id)
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            evaluations = evaluations.filter(date__gte=start)
        except ValueError:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            evaluations = evaluations.filter(date__lte=end)
        except ValueError:
            pass
    if quality:
        try:
            evaluations = evaluations.filter(quality_percentage__lte=float(quality))
        except ValueError:
            pass

    pizzas = Pizzas.objects.all()
    locations = PizzeriaLocation.objects.all()

    return render(request, 'evaluateRegister/evaluation_list.html', {
        'evaluations': evaluations,
        'pizzas': pizzas,
        'locations': locations,
    })


# Подробная страница одной оценки
@login_required(login_url='/login/')
def evaluation_detail(request, evaluation_id):
    evaluation = get_object_or_404(Evaluation, id=evaluation_id)

    ingredient_evaluations = evaluation.ingredient_evaluations.select_related('ingredient').all()

    return render(request, 'evaluateRegister/evaluation_detail.html', {
        'evaluation': evaluation,
        'ingredient_evaluations': ingredient_evaluations,
    })


@login_required(login_url='/login/')
def evaluation_export(request):
    evaluations = Evaluation.objects.all()

    # Те же фильтры, что и в списке
    pizza_id = request.GET.get('pizza')
    location_id = request.GET.get('location')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    quality = request.GET.get('quality')

    if pizza_id:
        evaluations = evaluations.filter(pizza_id=pizza_id)
    if location_id:
        evaluations = evaluations.filter(location_id=location_id)
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            evaluations = evaluations.filter(date__gte=start)
        except ValueError:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            evaluations = evaluations.filter(date__lte=end)
        except ValueError:
            pass
    if quality:
        try:
            evaluations = evaluations.filter(quality_percentage__lte=float(quality))
        except ValueError:
            pass

    # Создание Excel файла
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Оценки пицц"

    # Заголовки
    ws.append(["Пицца", "Адрес", "Дата оценки", "Качество (%)", "Процент корки (%)"])

    for evaluation in evaluations:
        ws.append([
            evaluation.pizza.name,
            evaluation.location.address,
            evaluation.date.strftime("%d.%m.%Y %H:%M"),
            round(evaluation.quality_percentage, 1),
            round(evaluation.crust_percentage, 1)
        ])

    # Отправляем файл пользователю
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = "evaluations_export.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response


@csrf_exempt
def create_evaluation_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    # Получение данных
    token = request.POST.get('token')
    pizza_id = request.POST.get('pizza_id')
    crust_percentage = request.POST.get('crust_percentage')
    ingredients_json = request.POST.get('ingredients')
    photo = request.FILES.get('photo')

    if not all([token, pizza_id, crust_percentage, ingredients_json, photo]):
        return JsonResponse({"error": "Missing required fields"}, status=400)

    # Проверка токена
    try:
        token_uuid = uuid.UUID(token)
        location = PizzeriaLocation.objects.get(token=token_uuid)
    except (PizzeriaLocation.DoesNotExist, ValueError):
        return JsonResponse({"error": "Invalid token"}, status=403)

    # Проверка пиццы
    try:
        pizza = Pizzas.objects.get(id=pizza_id)
    except Pizzas.DoesNotExist:
        return JsonResponse({"error": "Pizza not found"}, status=404)

    # Парсинг ингредиентов
    try:
        ingredients_data = json.loads(ingredients_json)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid ingredients format"}, status=400)

    if float(crust_percentage) > 100:
        return JsonResponse({"error": "Crust > 100%"}, status=400)

    # Получение эталонного процента корки из пиццы
    expected_crust_percentage = pizza.crust_percentage  # предполагаем, что у модели Pizzas есть поле crust_percentage

    # Сохраняем оценку без качества пока
    evaluation = Evaluation.objects.create(
        pizza=pizza,
        location=location,
        photo=photo,
        quality_percentage=0.0,  # пересчитаем ниже
        crust_percentage=float(crust_percentage)
    )

    # Сохраняем ингредиенты + собираем данные для расчёта
    ingredient_penalties = []

    for ingredient in ingredients_data:
        ing_id = ingredient.get('ingredient_id')
        detected_quantity = ingredient.get('detected_quantity')

        try:
            ingredient_obj = Ingredients.objects.get(id=ing_id)

            try:
                composition = PizzaComposition.objects.get(pizza=pizza, ingredient=ingredient_obj)
                expected_quantity = composition.quantity
            except PizzaComposition.DoesNotExist:
                expected_quantity = 0

            # Сохраняем ингредиент
            IngredientEvaluation.objects.create(
                evaluation=evaluation,
                ingredient=ingredient_obj,
                detected_quantity=detected_quantity,
                expected_quantity=expected_quantity
            )

            # Расчёт штрафа за ингредиенты
            if expected_quantity > 0:
                diff = abs(detected_quantity - expected_quantity) / expected_quantity * 100
                ingredient_penalties.append(diff)

        except Ingredients.DoesNotExist:
            continue

    # Расчёт оценки
    def calculate_quality(crust_real, crust_expected, penalties):
        crust_penalty = abs(crust_real - crust_expected) * 2

        if penalties:
            avg_ingredient_penalty = sum(penalties) / len(penalties)
        else:
            avg_ingredient_penalty = 0

        total_penalty = crust_penalty + avg_ingredient_penalty
        quality = max(100 - total_penalty, 0)
        return round(quality, 1)

    final_quality = calculate_quality(
        crust_real=float(crust_percentage),
        crust_expected=float(expected_crust_percentage),
        penalties=ingredient_penalties
    )

    # Обновляем качество в Evaluation
    evaluation.quality_percentage = final_quality
    evaluation.save()

    return JsonResponse({"success": True, "evaluation_id": evaluation.id, "quality": final_quality})