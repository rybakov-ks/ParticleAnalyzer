import os
from ultralytics import YOLO

class YOLOLoader:
    MODEL_MAPPING = {
        "Yolo11 (dataset 1)": "Yolo11_d1.pt",
        "Yolo12 (dataset 1)": "Yolo12_d1.pt",
        "Yolo11 (dataset 2)": "Yolo11_d2.pt",
        "Yolo12 (dataset 2)": "Yolo12_d2.pt",
    }

    def __init__(self):
        self._base_path = os.path.join(os.path.dirname(__file__), "..", "model")

        self.models = {
            display_name: YOLO(self._model_path(file_name))
            for display_name, file_name in self.__class__.MODEL_MAPPING.items()
        }

    def _model_path(self, name: str) -> str:
        return os.path.join(self._base_path, name)

    def get_model(self, model_name: str):
        return self.models.get(model_name)

    def get_model_path(self, model_name: str):
        if model_name in self.__class__.MODEL_MAPPING:
            return self._model_path(self.__class__.MODEL_MAPPING[model_name])
        return None