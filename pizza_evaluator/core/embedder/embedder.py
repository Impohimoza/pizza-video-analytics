import cv2
import numpy as np
import tensorflow as tf

from .vector_db import find_closest_class


class PizzaEmbedder:
    """Класс для получения вектора пиццы"""
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)

    def classify(self, image: np.ndarray) -> str:
        """Функция для классификации пиццы"""
        input_tensor = self.preprocess(image)
        embedding = self.model.predict(input_tensor)[0]
        return find_closest_class(embedding)

    def get_embedding(self, image: np.ndarray):
        """функция для получения векторного представления кропа"""
        input_tensor = self.preprocess(image)
        return self.model.predict(input_tensor)[0]

    def preprocess(self, image: np.ndarray):
        """Функция для предобработки кропа"""
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(image, (480, 480))
        normalized = resized.astype("float32") / 255.0
        return np.expand_dims(normalized, axis=0)
