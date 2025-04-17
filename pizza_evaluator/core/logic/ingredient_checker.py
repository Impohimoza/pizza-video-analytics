from collections import Counter

from db.postgres import pg


class IngredientChecker:
    """Класс содержащий логику подсчета количества ингредиентов в пицце"""
    def __init__(self, detector):
        self.cursor = pg.get_cursor()
        self.detector = detector

    def get_allowed_ingredients(self, pizza_id):
        """Функция для получения всех ингредиентов в пицце"""

        query = """
            SELECT ingredients.name, pizza_composition.quantity
            FROM pizza_composition
            JOIN ingredients ON pizza_composition.ingredient_id = ingredients.id
            WHERE pizza_composition.pizza_id = %s
        """
        self.cursor.execute(query, (pizza_id,))
        rows = self.cursor.fetchall()
        return {row[0]: row[1] for row in rows}  # {name: count}

    def count_ingredients(self, image, pizza_id):
        """Функция для подсчета количества ингредиентов"""
        allowed = self.get_allowed_ingredients(pizza_id)  # {name: count}
        detected_names = self.detector.detect(image)

        # Оставляем только допустимые по рецепту
        filtered = [name for name in detected_names if name in allowed]
        counted = Counter(filtered)

        # Преобразуем в {ingredient_name: count}
        result = {i: (counted[i], allowed[i]) for i in counted}
        return result
