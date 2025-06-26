import logging
from sahi.models.detectron2 import Detectron2DetectionModel

logger = logging.getLogger(__name__)

"""Переопределяем load_model для скрытия ошибки"""


class CustomDetectron2Model(Detectron2DetectionModel):
    def load_model(self):
        from detectron2.config import get_cfg
        from detectron2.data import MetadataCatalog
        from detectron2.engine import DefaultPredictor

        cfg = get_cfg()

        try:  # Переделываем импорт конфига и модели для скрытия ошибки "{} not available in Model Zoo!"
            cfg.merge_from_file(self.config_path)
            cfg.MODEL.WEIGHTS = self.model_path
        except Exception as e:  # try to load from local
            print(e)
            if self.config_path is not None:
                cfg.merge_from_file(self.config_path)
            cfg.MODEL.WEIGHTS = self.model_path

        # set model device
        cfg.MODEL.DEVICE = self.device.type
        # set input image size
        if self.image_size is not None:
            cfg.INPUT.MIN_SIZE_TEST = self.image_size
            cfg.INPUT.MAX_SIZE_TEST = self.image_size
        # init predictor
        model = DefaultPredictor(cfg)

        self.model = model

        # detectron2 category mapping
        if self.category_mapping is None:
            try:  # try to parse category names from metadata
                metadata = MetadataCatalog.get(cfg.DATASETS.TRAIN[0])
                category_names = metadata.thing_classes
                self.category_names = category_names
                self.category_mapping = {
                    str(ind): category_name
                    for ind, category_name in enumerate(self.category_names)
                }
            except Exception as e:
                logger.warning(e)
                # https://detectron2.readthedocs.io/en/latest/tutorials/datasets.html#update-the-config-for-new-datasets
                if cfg.MODEL.META_ARCHITECTURE == "RetinaNet":
                    num_categories = cfg.MODEL.RETINANET.NUM_CLASSES
                else:  # fasterrcnn/maskrcnn etc
                    num_categories = cfg.MODEL.ROI_HEADS.NUM_CLASSES
                self.category_names = [
                    str(category_id) for category_id in range(num_categories)
                ]
                self.category_mapping = {
                    str(ind): category_name
                    for ind, category_name in enumerate(self.category_names)
                }
        else:
            self.category_names = list(self.category_mapping.values())
