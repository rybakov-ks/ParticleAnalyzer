import numpy as np
from typing import List
import logging
from .ImageEnhancement import ImageEnhancement

logger = logging.getLogger(__name__)


class EnhancementPipeline:
    """
    Класс с готовыми пайплайнами улучшения изображений.
    Содержит предустановленные последовательности для различных типов SEM-изображений.
    """

    # Пайплайны для SEM изображений с фокусом на сегментацию
    DEFAULT_PIPELINES = {
        "sem_standard_enhancement": {
            "description": "Универсальный пайплайн для большинства SEM с частицами - баланс шумоподавления и четкости",
            "steps": [
                {
                    "method": "nlm_denoise",
                    "params": {
                        "h": 8,
                        "template_window_size": 7,
                        "search_window_size": 21,
                    },
                },
                {
                    "method": "adaptive_eq",
                    "params": {"clip_limit": 2.2, "tile_grid_size": (8, 8)},
                },
                {"method": "gamma_correction", "params": {"gamma": 0.75}},
                {
                    "method": "unsharp_mask",
                    "params": {
                        "kernel_size": (3, 3),
                        "sigma": 0.8,
                        "amount": 0.7,
                        "threshold": 5,
                    },
                },
            ],
        },
        "sem_high_quality_enhancement": {
            "description": "Для качественных SEM с минимальной обработкой - сохранение деталей",
            "steps": [
                {
                    "method": "bilateral_filter",
                    "params": {"d": 5, "sigma_color": 35, "sigma_space": 35},
                },
                {
                    "method": "adaptive_eq",
                    "params": {"clip_limit": 1.5, "tile_grid_size": (12, 12)},
                },
                {
                    "method": "unsharp_mask",
                    "params": {
                        "kernel_size": (2, 2),
                        "sigma": 0.5,
                        "amount": 0.4,
                        "threshold": 3,
                    },
                },
            ],
        },
        "sem_low_quality_enhancement": {
            "description": "Для зашумленных/размытых SEM - агрессивное улучшение",
            "steps": [
                {"method": "median_filter", "params": {"kernel_size": 2}},
                {
                    "method": "nlm_denoise",
                    "params": {
                        "h": 15,
                        "template_window_size": 7,
                        "search_window_size": 21,
                    },
                },
                {"method": "log_transform", "params": {"c": 1.2}},
                {
                    "method": "adaptive_eq",
                    "params": {"clip_limit": 3.0, "tile_grid_size": (6, 6)},
                },
                {
                    "method": "unsharp_mask",
                    "params": {
                        "kernel_size": (5, 5),
                        "sigma": 1.5,
                        "amount": 1.2,
                        "threshold": 8,
                    },
                },
            ],
        },
        "sem_nanoparticle_enhancement": {
            "description": "Специально для наночастиц - усиление мелких деталей",
            "steps": [
                {
                    "method": "bilateral_filter",
                    "params": {"d": 3, "sigma_color": 20, "sigma_space": 20},
                },
                {"method": "contrast", "params": {"alpha": 1.8, "beta": 2}},
                {"method": "gamma_correction", "params": {"gamma": 0.65}},
                {
                    "method": "unsharp_mask",
                    "params": {
                        "kernel_size": (2, 2),
                        "sigma": 0.3,
                        "amount": 1.8,
                        "threshold": 2,
                    },
                },
            ],
        },
        "sem_edge_enhancement": {
            "description": "Максимальное выделение границ для точной сегментации",
            "steps": [
                {
                    "method": "bilateral_filter",
                    "params": {"d": 7, "sigma_color": 40, "sigma_space": 40},
                },
                {
                    "method": "adaptive_eq",
                    "params": {"clip_limit": 2.5, "tile_grid_size": (10, 10)},
                },
                {"method": "contrast", "params": {"alpha": 1.6, "beta": 0}},
                {
                    "method": "unsharp_mask",
                    "params": {
                        "kernel_size": (3, 3),
                        "sigma": 0.7,
                        "amount": 1.5,
                        "threshold": 0,
                    },
                },
            ],
        },
    }

    def __init__(self):
        """Инициализация с предустановленными пайплайнами."""
        self.enhancer = ImageEnhancement()

        # Копируем константные пайплайны в экземпляр
        self.pipelines = self.DEFAULT_PIPELINES.copy()

    @classmethod
    def get_pipeline_names(cls) -> List[str]:
        """
        Получить список названий доступных пайплайнов без создания экземпляра.

        Returns:
            Список названий пайплайнов
        """
        return list(cls.DEFAULT_PIPELINES.keys())

    def get_available_pipelines(self) -> List[str]:
        """
        Получить список доступных пайплайнов.

        Returns:
            Список названий пайплайнов
        """
        return list(self.pipelines.keys())

    def apply_pipeline(
        self,
        image: np.ndarray,
        pipeline_name: str = "default",
    ) -> np.ndarray:
        """
        Применить пайплайн улучшения к изображению.

        Args:
            image: Входное изображение
            pipeline_name: Название пайплайна

        Returns:
            Улучшенное изображение
        """

        if pipeline_name not in self.pipelines:
            available = self.get_available_pipelines()
            raise ValueError(
                f"Пайплайн '{pipeline_name}' не найден. Доступные: {available}"
            )

        steps = self.pipelines[pipeline_name]["steps"]
        logger.info(f"Применяем пайплайн: {pipeline_name}")

        enhanced_image = image.copy()

        for i, step in enumerate(steps):
            method = step["method"]
            params = step.get("params", {})

            try:
                logger.info(f"Шаг {i+1}/{len(steps)}: {method}")
                enhanced_image = self.enhancer.enhance_image(
                    enhanced_image, method, **params
                )
            except Exception as e:
                logger.error(f"Ошибка на шаге {i+1} ({method}): {e}")
                # Продолжаем с предыдущим результатом
                continue

        logger.info("Пайплайн улучшения завершен")
        return enhanced_image
