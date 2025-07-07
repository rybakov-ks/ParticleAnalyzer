import os
import requests
from tqdm import tqdm
from .YOLOLoader import YOLOLoader

try:
    from detectron2.engine import DefaultPredictor
    from .Detectron2Loader import Detectron2Loader
    DETECTRON2_AVAILABLE = True
except ImportError:
    DETECTRON2_AVAILABLE = False


class ModelManager:
    def __init__(self, device=None):
        self.device = device
        self.SERVER_URL = "https://rybakov-k.ru/model/"
        
        # Инициализация путей
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.MODELS_DIR = os.path.join(base_path, "model")
        os.makedirs(self.MODELS_DIR, exist_ok=True)

        yolo_files = list(YOLOLoader.MODEL_MAPPING.values())
        detectron_files = []
        if DETECTRON2_AVAILABLE:
            detectron_files = [
                *[v["weights_file"] for v in Detectron2Loader.MODEL_MAPPING.values()]
            ]

        # Проверяем и загружаем модели
        self._ensure_models_available(yolo_files + detectron_files)

        # Инициализация загрузчиков
        self.yolo_loader = YOLOLoader()
        self.detectron_loader = Detectron2Loader(device=self.device) if DETECTRON2_AVAILABLE else None

    def _ensure_models_available(self, required_files):
        """Проверяет и загружает необходимые файлы моделей"""
        for filename in required_files:
            file_path = os.path.join(self.MODELS_DIR, filename)
            if not os.path.exists(file_path):
                self._download_file(filename)

    def _download_file(self, filename):
        """Скачивает файл с сервера"""
        if filename.endswith((".pth", ".yaml")) and not DETECTRON2_AVAILABLE:
            print(f"Skipping {filename} (Detectron2 not available)")
            return False

        url = f"{self.SERVER_URL}{filename}"
        save_path = os.path.join(self.MODELS_DIR, filename)

        try:
            print(f"Downloading {filename}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(save_path, "wb") as f, tqdm(
                desc=filename,
                total=int(response.headers.get("content-length", 0)),
                unit="B",
                unit_scale=True,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
            return True
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
            return False

    def get_model(self, model_name: str):
        """Возвращает модель по имени"""
        if model_name in self.yolo_loader.MODEL_MAPPING:
            return self.yolo_loader.get_model(model_name)
        elif DETECTRON2_AVAILABLE and model_name in self.detectron_loader.MODEL_CONFIGS:
            return self.detectron_loader.get_config(model_name)
        raise ValueError(f"Unknown model: {model_name}")

    def get_predictor(self, model_name: str):
        """Для Detectron возвращает готовый predictor"""
        if DETECTRON2_AVAILABLE and model_name in self.detectron_loader.MODEL_CONFIGS:
            cfg = self.detectron_loader.get_config(model_name)
            return DefaultPredictor(cfg)
        return None

    def get_model_path(self, model_name: str) -> str:
        """Возвращает путь к модели по её имени"""
        if model_name in self.yolo_loader.MODEL_MAPPING:
            return self.yolo_loader.get_model_path(model_name)
        elif DETECTRON2_AVAILABLE and model_name in self.detectron_loader.MODEL_CONFIGS:
            return self.detectron_loader.get_model_path(model_name)
        raise ValueError(f"Model {model_name} not found")

    def get_config_path(self, model_name: str) -> str:
        """Возвращает путь к конфигу (только для Detectron)"""
        if DETECTRON2_AVAILABLE and model_name in self.detectron_loader.MODEL_CONFIGS:
            return self.detectron_loader.get_config_path(model_name)
        raise ValueError(f"Config for {model_name} not available")