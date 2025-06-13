# -*- coding: utf-8 -*-
import os
from ultralytics import YOLO

"""Работаем с моделями YOLO"""
class YOLOLoader:
    def __init__(self):
        
        base_path = os.path.dirname(__file__)
        model_path = lambda name: os.path.join(base_path, "..", "model", name)
        
        self.models = {
            "Yolo11 (dataset 2)": YOLO(model_path("Yolo11_d2.pt")),
            "Yolo12 (dataset 2)": YOLO(model_path("Yolo12_d2.pt")),
            "Yolo11 (dataset 1)": YOLO(model_path("Yolo11_d1.pt")),
            "Yolo12 (dataset 1)": YOLO(model_path("Yolo12_d1.pt")),
        }
        self.models_path = {
            "Yolo11 (dataset 1)": model_path("Yolo11_d1.pt"),
            "Yolo12 (dataset 1)": model_path("Yolo12_d1.pt"),
            "Yolo11 (dataset 2)": model_path("Yolo11_d2.pt"),
            "Yolo12 (dataset 2)": model_path("Yolo12_d2.pt")
        }

    def get_model(self, model_name: str):
        return self.models.get(model_name)
        
    def get_model_path(self, model_name: str):
        return self.models_path.get(model_name)