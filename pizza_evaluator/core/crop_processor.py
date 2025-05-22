import os

import numpy as np

from .detectors.ingredient_detector import IngredientDetector
from .embedder.embedder import PizzaEmbedder
from .segmentation.crust_segmentation import CrustSegmentation
from .logic.ingredient_checker import IngredientChecker
from .logic.crust_checker import CrustChecker
from .logic.distribution_checker import DistributionChecker
from .logic.filling_center_checker import FillingCenterChecker
from .api.evaluation_to_server import send_evaluation_to_server


class CropProcessor:
    """Класс для классификации и оценки пиццы"""
    def __init__(self):
        self.embedder = PizzaEmbedder(
            model_path=os.getenv("FEATURE_EXTRACTOR_PATH")
            )
        self.detector = IngredientDetector(model_path=os.getenv("INGREDIENTS_DETECTOR"))
        self.segmentation = CrustSegmentation(model_path=os.getenv("CRUST_SEGMENTATION"))
        self.ingredient_checker = IngredientChecker(self.detector.class_names)
        self.filling_center_checker = FillingCenterChecker()
        self.crust_checker = CrustChecker()
        self.distribution_checker = DistributionChecker(0.6)

    def process_crop(self, crop: np.ndarray) -> str:
        pizza_id = self.embedder.classify(crop)
        detection_result = self.detector.detect(crop)
        segmentation_result = self.segmentation.detect(crop)
        ingredient_count = self.ingredient_checker.count_ingredients(
            pizza_id=pizza_id,
            detection_result=detection_result
            )
        print(ingredient_count)
        percent_crust = self.crust_checker.get_percentage_crust(
            crop,
            segmentation_result
            )
        print(f"Процент корки: {percent_crust}")
        distribution = self.distribution_checker.ingredient_distribution_score(
            crop,
            detection_result,
            segmentation_result
            )
        print(distribution)
        shift, radius = self.filling_center_checker.compute_center_shift(
            crop,
            segmentation_result
            )
        print(f"Радиус пиццы: {radius}")
        print(f"Смещение начинки: {shift}")
        send_evaluation_to_server(pizza_id,
                                  percent_crust,
                                  ingredient_count,
                                  crop)
        return pizza_id
