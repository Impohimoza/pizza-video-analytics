from collections import Counter

from db.postgres import pg


class IngredientChecker:
    """Класс содержащий логику подсчета количества ингредиентов в пицце"""
    def __init__(self, class_names):
        self.cursor = pg.get_cursor()
        self.class_names = class_names

    def get_allowed_ingredients(self, pizza_id):
        """Функция для получения всех ингредиентов в пицце"""

        query = """
            SELECT ingredients.name, ingredients.id
            FROM pizza_composition
            JOIN ingredients ON pizza_composition.ingredient_id = ingredients.id
            WHERE pizza_composition.pizza_id = %s
        """
        self.cursor.execute(query, (pizza_id,))
        rows = self.cursor.fetchall()
        # {name: (id, count)}
        return {row[0]: (row[1]) for row in rows}

    def count_ingredients(self, pizza_id, detection_result):
        """Функция для подсчета количества ингредиентов"""
        allowed = self.get_allowed_ingredients(pizza_id)  # {name: (id, count)}
        detected_names = []
        for box in detection_result[0].boxes:
            cls_id = int(box.cls.cpu().numpy()[0])
            name = self.class_names[cls_id]
            detected_names.append(name)

        # Оставляем только допустимые по рецепту
        filtered = [name for name in detected_names if name in allowed]
        counted = Counter(filtered)

        # Преобразуем в {ingredient_id: (detect_count, allowed_count)}
        result = [
            {"ingredient_name": i, "detected_quantity": counted[i]} for i in counted
            ]
        return result
