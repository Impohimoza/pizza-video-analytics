import os

from .embedder.embedder import PizzaEmbedder
from .detectors.ingredient_detector import IngredientDetector
from .logic.ingredient_checker import IngredientChecker


class CropProcessor:
    """Класс для классификации и оценки пиццы"""
    def __init__(self):
        self.embedder = PizzaEmbedder(model_path=os.getenv("FEATURE_EXTRACTOR_PATH"))
        self.checker = IngredientChecker(IngredientDetector(model_path=os.getenv("INGREDIENTS_DETECTOR")))

    def process_crop(self, crop):
        pizza_id = self.embedder.classify(crop)
        ingredient_count = self.checker.count_ingredients(crop,
                                                          pizza_id=pizza_id)
        for ingr in ingredient_count:
            print(f'{ingr}:   {ingredient_count[ingr]}')
        return pizza_id
