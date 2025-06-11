from .YOLOLoader import YOLOLoader
try:
    from detectron2.engine import DefaultPredictor
    from .Detectron2Loader import Detectron2Loader
    DETECTRON2_AVAILABLE = True
except ImportError:
    DETECTRON2_AVAILABLE = False

class ModelManager:
    def __init__(self):
        self.yolo_loader = YOLOLoader()
        
        # Инициализируем detectron_loader только если detectron2 доступен
        if DETECTRON2_AVAILABLE:
            self.detectron_loader = Detectron2Loader()
        else:
            self.detectron_loader = None
        
        self.model_types = {
            "Yolo11 (dataset 1)": "yolo",
            "Yolo12 (dataset 1)": "yolo",
            "Yolo11 (dataset 2)": "yolo",
            "Yolo12 (dataset 2)": "yolo",
            "R101": "detectron",
            "X101": "detectron",
            "Cascade_R50": "detectron",
            "Cascade_X152": "detectron"
        }
    
    def get_model(self, model_name: str):
        """Возвращает модель по имени"""
        model_type = self.model_types.get(model_name)
        
        if model_type == "yolo":
            return self.yolo_loader.get_model(model_name)
        elif model_type == "detectron":
            return self.detectron_loader.get_config(model_name)
        else:
            raise ValueError(f"Unknown model type: {model_name}")
    
    def get_predictor(self, model_name: str):
        """Для Detectron возвращает готовый predictor"""
        if model_name in self.detectron_loader.configs:
            cfg = self.detectron_loader.get_config(model_name)
            return DefaultPredictor(cfg)
        return None
        
    def get_model_path(self, model_name: str) -> str:
        """Возвращает путь к модели по её имени"""
        if model_name in self.yolo_loader.models:
            return self.yolo_loader.get_model_path(model_name)
        elif model_name in self.detectron_loader.configs:
            return self.detectron_loader.get_model_path(model_name)
        else:
            raise ValueError(f"Model {model_name} not found")

    def get_config_path(self, model_name: str) -> str:
        """Возвращает путь к конфигу (только для Detectron)"""
        if model_name in self.detectron_loader.configs:
            return self.detectron_loader.get_config_path(model_name)
        raise ValueError(f"Config for {model_name} not available (YOLO models don't use config files)")