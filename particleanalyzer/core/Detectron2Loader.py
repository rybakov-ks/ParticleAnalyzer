import os
import torch
from detectron2.config import get_cfg
from detectron2.model_zoo import model_zoo
from detectron2.utils.logger import setup_logger
import logging
import warnings

logger = setup_logger()
logger.setLevel("ERROR")
logging.disable(logging.CRITICAL)
warnings.filterwarnings("ignore", category=UserWarning)

"""Работаем с моделями Detectron2"""

class Detectron2Loader:
    MODEL_MAPPING = {
        "R101": {
            "config_file": "COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml",
            "weights_file": "faster_rcnn_R_101_FPN_3x.pth",
            "config_path": "faster_rcnn_R_101_FPN_3x.yaml"
        },
        "X101": {
            "config_file": "COCO-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_3x.yaml",
            "weights_file": "faster_rcnn_X_101_32x8d_FPN_3x.pth",
            "config_path": "faster_rcnn_X_101_32x8d_FPN_3x.yaml"
        },
        "Cascade_R50": {
            "config_file": "Misc/cascade_mask_rcnn_R_50_FPN_3x.yaml",
            "weights_file": "cascade_mask_rcnn_R_50_FPN_3x.pth",
            "config_path": "cascade_mask_rcnn_R_50_FPN_3x.yaml"
        },
        "Cascade_X152": {
            "config_file": "Misc/cascade_mask_rcnn_X_152_32x8d_FPN_IN5k_gn_dconv.yaml",
            "weights_file": "cascade_mask_rcnn_X_152_32x8d_FPN_IN5k_gn_dconv.pth",
            "config_path": "cascade_mask_rcnn_X_152_32x8d_FPN_IN5k_gn_dconv.yaml"
        }
    }

    def __init__(self, device=None):
        self._base_path = os.path.join(os.path.dirname(__file__), "..", "model")
        self.device = self._get_device(device)
        self.configs = {}
        self._init_models()

    def _get_device(self, device):
        if device is None:
            return "cuda" if torch.cuda.is_available() else "cpu"
        return device.type if isinstance(device, torch.device) else str(device)

    def _model_path(self, name: str) -> str:
        return os.path.join(self._base_path, name)

    def _init_model_config(self, model_name):
        cfg = get_cfg()
        model_data = self.MODEL_MAPPING[model_name]
        
        cfg.merge_from_file(model_zoo.get_config_file(model_data["config_file"]))
        cfg.OUTPUT_DIR = self._base_path
        cfg.MODEL.WEIGHTS = self._model_path(model_data["weights_file"])
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
        cfg.MODEL.DEVICE = self.device
        
        return cfg

    def _init_models(self):
        self.configs = {
            name: self._init_model_config(name)
            for name in self.MODEL_MAPPING
        }
        
        self.config_paths = {
            name: self._model_path(self.MODEL_MAPPING[name]["config_path"])
            for name in self.MODEL_MAPPING
        }
        
        self.model_paths = {
            name: self._model_path(self.MODEL_MAPPING[name]["weights_file"])
            for name in self.MODEL_MAPPING
        }
        
        self._save_configs()

    def _save_configs(self):
        for model_name, cfg in self.configs.items():
            with open(self.config_paths[model_name], "w") as f:
                f.write(cfg.dump())

    def get_config(self, model_name: str):
        return self.configs.get(model_name)

    def get_config_path(self, model_name: str):
        return self.config_paths.get(model_name)

    def get_model_path(self, model_name: str):
        return self.model_paths.get(model_name)