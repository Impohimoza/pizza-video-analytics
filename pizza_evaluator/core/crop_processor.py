import os

from .embedder.embedder import PizzaEmbedder


class CropProcessor:
    def __init__(self):
        self.embedder = PizzaEmbedder(model_path=os.getenv("MODEL_PATH"))

    def process_crop(self, crop):
        pizza_name = self.embedder.classify(crop)
        return pizza_name
