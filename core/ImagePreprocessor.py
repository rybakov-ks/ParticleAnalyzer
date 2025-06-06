import os
import pandas as pd
import cv2
import numpy as np
import math
from tqdm import tqdm
import gradio as gr
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

"""Подготовка изображения перед анализом"""
class ImagePreprocessor:
    def __init__(self, output_dir: str = "output"):
        self._processing_profiles = {
            '640x640': (640, 640),
            '1024x1024': (1024, 1024),
            '1280x1280': (1280, 1280),
            '1600x1600': (1600, 1600),
            '2048x2048': (2048, 2048),
            'Оригинал': None
        }
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def preprocess_image(
        self,
        image: np.ndarray,
        image2: Optional[np.ndarray],
        scale_selector: str,
        solution: str,
        request: gr.Request,
        pbar: tqdm,
        sahi_mode: bool
    ):
        """Основной метод предварительной обработки изображения."""
        pbar.set_description("Загрузка изображения...")
        try:
            # Обработка шкалы прибора
            scale = None
            if scale_selector == 'Шкала прибора в мкм':
                scale = self._determine_pixel_scale(image)
                if scale is None:
                    return None, None, None, None
                image = image["background"]
                image = self._convert_image_channels(image)
            else:
                image = np.array(image2)
            
            # Сохранение метаданных
            self._save_image_metadata(image, request)
            
            # Изменение размера
            image = self._resize_image(image, solution, sahi_mode)
            
            # Конвертация цветовых пространств
            orig_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2GRAY)
            pbar.update(1)
            return image, orig_image, gray_image, scale
            
        except Exception as e:
            #print(f"Ошибка при обработке изображения: {e}")
            return None, None, None, None

    def _convert_image_channels(self, image: np.ndarray) -> np.ndarray:
        """Конвертирует изображение в RGB при необходимости."""
        if image.shape[-1] == 4:  # RGBA → RGB
            return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        elif image.shape[-1] == 1:  # Grayscale → RGB
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        return image

    def _resize_image(self, image: np.ndarray, solution: str, sahi_mode: bool) -> np.ndarray:
        """Изменяет размер изображения согласно выбранному профилю."""
        if solution == 'Оригинал' or sahi_mode:
            return image
            
        if solution in self._processing_profiles:
            max_w, max_h = self._processing_profiles[solution]
            h, w = image.shape[:2]
            
            if h > max_h or w > max_w:
                scale = min(max_h / h, max_w / w)
                new_size = (int(w * scale), int(h * scale))
                #print(f"Изменение размера: {w}x{h} → {new_size[0]}x{new_size[1]}")
                return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
        
        return image

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
                "image_path": [image_path]
            }
            
            # Записываем в CSV
            new_df = pd.DataFrame(new_data)
            if os.path.exists(csv_path):
                new_df.to_csv(csv_path, mode='a', header=False, index=False)
            else:
                new_df.to_csv(csv_path, mode='w', header=True, index=False)
                
        except Exception as e:
            pass
            #print(f"Ошибка при сохранении метаданных: {e}")

    def get_error_response(self) -> tuple:
        """Возвращает кортеж с None для обработки ошибок."""
        return (None,) * 13
        
    def _determine_pixel_scale(self, data):
        """Определяет размер пикселя в реальных единицах (μm/px)"""
        layers = data.get("layers", [])
        if layers:
            layer = layers[0]
            if layer.shape[-1] == 4:
                layer = cv2.cvtColor(layer, cv2.COLOR_RGBA2RGB)

            # Создаем маски для разных цветов (зеленый, красный, синий, желтый)
            lower_green = np.array([0, 128, 0])
            upper_green = np.array([100, 255, 100])
            
            lower_red = np.array([0, 0, 128])
            upper_red = np.array([100, 100, 255])
            
            lower_blue = np.array([0, 0, 128])
            upper_blue = np.array([100, 100, 255])
            
            lower_yellow = np.array([128, 128, 0])
            upper_yellow = np.array([255, 255, 100])
            
            # Создаем маску для всех цветов
            mask_green = cv2.inRange(layer, lower_green, upper_green)
            mask_red = cv2.inRange(layer, lower_red, upper_red)
            mask_blue = cv2.inRange(layer, lower_blue, upper_blue)
            mask_yellow = cv2.inRange(layer, lower_yellow, upper_yellow)
            
            # Объединяем все маски
            mask = cv2.bitwise_or(mask_green, cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_blue, mask_yellow)))

            # Находим контуры на маске
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if len(contours) == 2:
                # Рассчитываем центроиды для первых двух контуров
                moments1 = cv2.moments(contours[0])
                moments2 = cv2.moments(contours[1])

                if moments1["m00"] != 0 and moments2["m00"] != 0:
                    cx1 = int(moments1["m10"] / moments1["m00"])
                    cy1 = int(moments1["m01"] / moments1["m00"])
                    cx2 = int(moments2["m10"] / moments2["m00"])
                    cy2 = int(moments2["m01"] / moments2["m00"])

                    # Рассчитываем расстояние между центрами масс двух контуров
                    distance = math.sqrt((cx2 - cx1) ** 2 + (cy2 - cy1) ** 2)
                else:
                    gr.Info("Ошибка в вычислении центроида.")
            elif len(contours) > 2:
                distance = False
                gr.Info("Найдено больше двух точек.")
            else:
                distance = False
                gr.Info("Обозначьте на изображении масштабную шкалу при помощи двух точек.")
             # Возвращаем расстояние   
            return distance
        else:
            # Если слоев нет, возвращаем False
            gr.Info("Обозначьте на изображении масштабную шкалу при помощи двух точек.")
            return False