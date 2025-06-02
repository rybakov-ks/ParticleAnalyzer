import os
from detectron2.config import get_cfg
from detectron2.model_zoo import model_zoo
from detectron2.utils.logger import setup_logger
import logging
import warnings

logger = setup_logger()
logger.setLevel("ERROR")
logging.disable(logging.CRITICAL)

# Скрываем предупреждения PyTorch
warnings.filterwarnings("ignore", category=UserWarning)
"""Работаем с моделями Detectron2"""
class Detectron2Loader:
    def __init__(self):
        # Инициализация конфигураций
        self.configs = {
            "R101": self._init_r101_config(),
            "X101": self._init_x101_config(),
            "Cascade_R50": self._init_cascade_r50_config(),
            "Cascade_X152": self._init_cascade_x152_config()
        }
        
        self.config_paths = {
            "R101": "model/faster_rcnn_R_101_FPN_3x.yaml",
            "X101": "model/faster_rcnn_X_101_32x8d_FPN_3x.yaml",
            "Cascade_R50": "model/cascade_mask_rcnn_R_50_FPN_3x.yaml",
            "Cascade_X152": "model/cascade_mask_rcnn_X_152_32x8d_FPN_IN5k_gn_dconv.yaml"
        }
        
        self.model_paths = {
            "R101": "model/faster_rcnn_R_101_FPN_3x.pth",
            "X101": "model/faster_rcnn_X_101_32x8d_FPN_3x.pth",
            "Cascade_R50": "model/cascade_mask_rcnn_R_50_FPN_3x.pth",
            "Cascade_X152": "model/cascade_mask_rcnn_X_152_32x8d_FPN_IN5k_gn_dconv.pth"
        }
        
        # Сохраняем конфигурации в файлы
        self._save_configs()

    def _init_r101_config(self):
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"))
        cfg.OUTPUT_DIR = 'model'
        cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "faster_rcnn_R_101_FPN_3x.pth")
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
        cfg.MODEL.DEVICE = "cuda"
        return cfg

    def _init_x101_config(self):
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_3x.yaml"))
        cfg.OUTPUT_DIR = 'model'
        cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "faster_rcnn_X_101_32x8d_FPN_3x.pth")
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
        cfg.MODEL.DEVICE = "cuda"
        return cfg

    def _init_cascade_r50_config(self):
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("Misc/cascade_mask_rcnn_R_50_FPN_3x.yaml"))
        cfg.OUTPUT_DIR = 'model'
        cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "cascade_mask_rcnn_R_50_FPN_3x.pth")
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
        cfg.MODEL.DEVICE = "cuda"
        return cfg

    def _init_cascade_x152_config(self):
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("Misc/cascade_mask_rcnn_X_152_32x8d_FPN_IN5k_gn_dconv.yaml"))
        cfg.OUTPUT_DIR = 'model'
        cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "cascade_mask_rcnn_X_152_32x8d_FPN_IN5k_gn_dconv.pth")
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
        cfg.MODEL.DEVICE = "cuda"
        return cfg

    def _save_configs(self):
        """Сохраняет конфигурации в файлы"""
        for model_name, cfg in self.configs.items():
            with open(self.config_paths[model_name], "w") as f:
                f.write(cfg.dump())

    def get_config(self, model_name: str):
        """Возвращает конфигурацию модели"""
        return self.configs.get(model_name)

    def get_config_path(self, model_name: str):
        """Возвращает путь к файлу конфигурации"""
        return self.config_paths.get(model_name)

    def get_model_path(self, model_name: str):
        """Возвращает путь к весам модели"""
        return self.model_paths.get(model_name)