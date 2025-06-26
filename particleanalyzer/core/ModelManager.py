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
        # URL сервера
        self.SERVER_URL = "https://rybakov-k.ru/model/"

        # Путь к моделям
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.MODELS_DIR = os.path.join(base_path, "model")
        os.makedirs(self.MODELS_DIR, exist_ok=True)

        # Проверяем и загружаем модели
        self._ensure_models_available()

        # Инициализируем YOLO
        self.yolo_loader = YOLOLoader()

        # Инициализируем detectron_loader только если detectron2 доступен
        if DETECTRON2_AVAILABLE:
            self.detectron_loader = Detectron2Loader(device=self.device)
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
            "Cascade_X152": "detectron",
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
        raise ValueError(
            f"Config for {model_name} not available (YOLO models don't use config files)"
        )

    def _ensure_models_available(self):
        """Проверяет и загружает только необходимые модели"""
        # Базовые файлы для YOLO (всегда нужны)
        required_files = [
            "Yolo11_d1.pt",
            "Yolo11_d2.pt",
            "Yolo12_d1.pt",
            "Yolo12_d2.pt",
        ]

        # Добавляем модели Detectron2 только если доступен
        if DETECTRON2_AVAILABLE:
            required_files.extend(
                [
                    "faster_rcnn_R_101_FPN_3x.pth",
                    "faster_rcnn_X_101_32x8d_FPN_3x.pth",
                    "cascade_mask_rcnn_R_50_FPN_3x.pth",
                    "cascade_mask_rcnn_X_152_32x8d_FPN_IN5k_gn_dconv.pth",
                ]
            )

        for filename in required_files:
            file_path = os.path.join(self.MODELS_DIR, filename)
            if not os.path.exists(file_path):
                self._download_file(filename)

    def _download_file(self, filename):
        """Скачивает файл с сервера"""
        # Если это модель Detectron2 и библиотека недоступна - пропускаем
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
