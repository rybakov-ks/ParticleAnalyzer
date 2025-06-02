from ultralytics import YOLO

"""Работаем с моделями YOLO"""
class YOLOLoader:
    def __init__(self):
        self.models = {
            "Yolo11 (dataset 2)": YOLO("model/Yolo11_d2.pt"),
            "Yolo12 (dataset 2)": YOLO("model/Yolo12_d2.pt"),
            "Yolo11 (dataset 1)": YOLO("model/Yolo11_d1.pt"),
            "Yolo12 (dataset 1)": YOLO("model/Yolo12_d1.pt"),
        }
        self.models_path = {
            "Yolo11 (dataset 1)": 'model/Yolo11_d1.pt',
            "Yolo12 (dataset 1)": 'model/Yolo12_d1.pt',
            "Yolo11 (dataset 2)": 'model/Yolo11_d2.pt',
            "Yolo12 (dataset 2)": 'model/Yolo12_d2.pt'
        }

    def get_model(self, model_name: str):
        return self.models.get(model_name)
        
    def get_model_path(self, model_name: str):
        return self.models_path.get(model_name)