import tensorflow as tf
import numpy as np
import cv2
from django.conf import settings
import os


class FeatureExtractor:
    def __init__(self, model_filename='feature_extractor.keras'):
        model_path = os.path.join(settings.BASE_DIR, 'models', model_filename)
        self.model = tf.keras.models.load_model(model_path)

    def extract(self, image_path):
        print(image_path)
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (480, 480))
        img = img.astype('float32') / 255.0
        img = np.expand_dims(img, axis=0)

        embedding = self.model.predict(img)[0]
        return embedding.tolist()
