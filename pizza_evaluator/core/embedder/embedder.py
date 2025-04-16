import numpy as np
import tensorflow as tf
import cv2

from .vector_db import find_closest_class


class PizzaEmbedder:
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)

    def classify(self, image):
        input_tensor = self.preprocess(image)
        embedding = self.model.predict(input_tensor)[0]
        return find_closest_class(embedding)

    def get_embedding(self, image):
        input_tensor = self.preprocess(image)
        return self.model.predict(input_tensor)[0]

    def preprocess(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(image, (480, 480))
        normalized = resized.astype("float32") / 255.0
        return np.expand_dims(normalized, axis=0)
