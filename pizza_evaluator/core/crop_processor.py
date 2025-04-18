import os

import numpy as np

from .detectors.ingredient_detector import IngredientDetector
from .embedder.embedder import PizzaEmbedder
from .logic.ingredient_checker import IngredientChecker
from .logic.crust_checker import CrustChecker
from .segmentation.crust_segmentation import CrustSegmentation


class CropProcessor:
    """Класс для классификации и оценки пиццы"""
    def __init__(self):
        self.embedder = PizzaEmbedder(
            model_path=os.getenv("FEATURE_EXTRACTOR_PATH")
            )
        self.ingredient_checker = IngredientChecker(
            IngredientDetector(model_path=os.getenv("INGREDIENTS_DETECTOR"))
            )
        self.crust_checker = CrustChecker(
            model=CrustSegmentation(model_path=os.getenv("CRUST_SEGMENTATION"))
            )

    def process_crop(self, crop: np.ndarray) -> str:
        pizza_id = self.embedder.classify(crop)
        ingredient_count = self.ingredient_checker.count_ingredients(
            crop,
            pizza_id=pizza_id
            )
        for ingr in ingredient_count:
            print(f'{ingr}:   {ingredient_count[ingr]}')
        percent_crust = self.crust_checker.get_percentage_crust(crop)
        print(f"Процент корки: {percent_crust}")
        return pizza_id
