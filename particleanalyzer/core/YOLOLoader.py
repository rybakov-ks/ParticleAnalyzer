import os
from ultralytics import YOLO

"""Работаем с моделями YOLO"""


class YOLOLoader:
    def __init__(self):
        self._base_path = os.path.dirname(__file__)

        self.models = {
            "Yolo11 (dataset 2)": YOLO(self._model_path("Yolo11_d2.pt")),
            "Yolo12 (dataset 2)": YOLO(self._model_path("Yolo12_d2.pt")),
            "Yolo11 (dataset 1)": YOLO(self._model_path("Yolo11_d1.pt")),
            "Yolo12 (dataset 1)": YOLO(self._model_path("Yolo12_d1.pt")),
        }
        self.models_path = {
            "Yolo11 (dataset 1)": self._model_path("Yolo11_d1.pt"),
            "Yolo12 (dataset 1)": self._model_path("Yolo12_d1.pt"),
            "Yolo11 (dataset 2)": self._model_path("Yolo11_d2.pt"),
            "Yolo12 (dataset 2)": self._model_path("Yolo12_d2.pt"),
        }

    def _model_path(self, name: str):
        return os.path.join(self._base_path, "..", "model", name)

    def get_model(self, model_name: str):
        return self.models.get(model_name)

    def get_model_path(self, model_name: str):
        return self.models_path.get(model_name)
