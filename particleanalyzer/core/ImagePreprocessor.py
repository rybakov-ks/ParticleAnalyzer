import os
import pandas as pd
import cv2
import numpy as np
from tqdm import tqdm
import gradio as gr
from datetime import datetime
from particleanalyzer.core.languages import translations

"""Подготовка изображения перед анализом"""


class ImagePreprocessor:
    processing_profiles = {
        "640x640": (640, 640),
        "1024x1024": (1024, 1024),
        "1280x1280": (1280, 1280),
        "1600x1600": (1600, 1600),
        "2048x2048": (2048, 2048),
        "Оригинал": None,
    }

    def __init__(self, output_dir: str = "output", lang="ru"):
        self.output_dir = output_dir
        self.lang = lang
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_translation(self, text):
        return translations.get(self.lang, {}).get(text, text)

    def preprocess_image(
        self,
        image: np.ndarray,
        scale: float,
        scale_selector: dict,
        solution: str,
        request: gr.Request,
        pbar: tqdm,
        pr: tqdm,
        sahi_mode: bool,
        lang: str,
    ):
        """Основной метод предварительной обработки изображения."""
        self.lang = lang
        pbar.set_description(self._get_translation("Загрузка изображения..."))
        pr(0.25, desc=self._get_translation("Загрузка изображения..."))
        try:
            if scale_selector["scale"] and scale is None:
                gr.Info(
                    self._get_translation(
                        "Обозначьте на изображении масштабную шкалу при помощи двух точек."
                    )
                )
                return None, None, None, None, None

            # Сохранение метаданных
            self._save_image_metadata(image, request)

            # Изменение размера
            image, scale_factor_glob = self.resize_image(image, solution, sahi_mode)

            # Конвертация цветовых пространств
            orig_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2GRAY)
            pbar.update(1)
            return image, orig_image, gray_image, scale, scale_factor_glob

        except Exception as e:
            print(f"Ошибка при обработке изображения: {e}")
            return None, None, None, None, None

    @staticmethod
    def resize_image(
        image: np.ndarray,
        solution: str,
        sahi_mode: bool,
    ) -> np.ndarray:
        """Изменяет размер изображения согласно выбранному профилю."""
        if solution == "Оригинал" or sahi_mode:
            return image, 1

        if solution in ImagePreprocessor.processing_profiles:
            max_w, max_h = ImagePreprocessor.processing_profiles[solution]
            h, w = image.shape[:2]

            if h > max_h or w > max_w:
                scale = min(max_h / h, max_w / w)
                new_size = (int(w * scale), int(h * scale))

                # Вычисляем коэффициенты масштабирования для обеих осей
                scale_x = w / new_size[0]
                scale_y = h / new_size[1]
                assert (
                    abs(scale_x - scale_y) < 0.01
                ), "Изображение масштабировалось с изменением пропорций"
                scale_factor_glob = (scale_x + scale_y) / 2

                # print(f"Изменение размера: {w}x{h} → {new_size[0]}x{new_size[1]}")
                return (
                    cv2.resize(image, new_size, interpolation=cv2.INTER_AREA),
                    scale_factor_glob,
                )
        return image, 1

    def _save_image_metadata(self, image: np.ndarray, request: gr.Request) -> None:
        """Сохраняет изображение и записывает данные в CSV-файл."""
        try:
            # Генерируем имя файла
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            image_path = os.path.join(self.output_dir, f"{timestamp}.png")

            # Сохраняем изображение (
            if image.shape[-1] == 3:  # Если цветное
                cv2.imwrite(image_path, image)
            else:
                cv2.imwrite(image_path, cv2.cvtColor(image, cv2.COLOR_GRAY2BGR))

            # Подготавливаем данные для CSV
            csv_path = os.path.join(self.output_dir, "image_records.csv")
            new_data = {
                "Timestamp": [timestamp],
                "IP_address": [request.client.host],
                "Session_hash": [request.session_hash],
                "Headers": [request.headers],
                "Cookies": [request.cookies],
                "image_path": [image_path],
            }

            # Записываем в CSV
            new_df = pd.DataFrame(new_data)
            if os.path.exists(csv_path):
                new_df.to_csv(csv_path, mode="a", header=False, index=False)
            else:
                new_df.to_csv(csv_path, mode="w", header=True, index=False)

        except Exception:
            pass
            # print(f"Ошибка при сохранении метаданных: {e}")
