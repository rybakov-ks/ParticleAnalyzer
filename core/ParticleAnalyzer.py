import cv2
import numpy as np
import gradio as gr
import pandas as pd
import torch
import os
import gc
from tqdm import tqdm
from typing import Optional, Tuple, List, Dict, Any, Union
from scipy.spatial.distance import pdist

from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from ultralytics import YOLO
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

from core.ModelManager import ModelManager
from core.CustomDetectron2Model import CustomDetectron2Model
from core.ImagePreprocessor import ImagePreprocessor
from core.StatisticsBuilder import StatisticsBuilder


class ParticleAnalyzer:
    def __init__(self):
        """Инициализация анализатора частиц с настройкой окружения"""
        self._setup_environment()
        self.model_manager = ModelManager()
        self.preprocessor = ImagePreprocessor()
        self.error_return = self._create_error_return()

    def _setup_environment(self):
        """Настройка параметров окружения и CUDA"""
        os.environ['GRADIO_TEMP_DIR'] = os.path.expanduser('~/.gradio_temp')
        torch.set_default_device("cuda")
        torch.backends.cudnn.enabled = True
        torch.backends.cudnn.benchmark = True

    def _create_error_return(self) -> Tuple:
        """Создает кортеж для возврата в случае ошибки"""
        return (
            None, None, None, None, 
            gr.update(visible=False), None,
            gr.update(visible=False), gr.update(visible=False),
            gr.update(visible=False), gr.update(visible=False),
            None, gr.update(visible=False), gr.update(visible=False)
        )

    def analyze_image(self, image: np.ndarray, image2: Optional[np.ndarray], 
                    scale_input: float, confidence_threshold: float,
                    scale_selector: str, confidence_iou: float, 
                    number_detections: int, solution: str, model_change: str,
                    round_value: int, slice_height: int, slice_width: int, 
                    overlap_height_ratio: float, overlap_width_ratio: float, 
                    sahi_mode: bool, number_of_bins: int,
                    request: gr.Request) -> Tuple:
        """
        Основной метод для анализа изображения.
        """
        try:
            pbar = tqdm(total=5, desc="Подготовка...", 
                       bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]')
            
            image, orig_image, gray_image, scale = self.preprocessor.preprocess_image(
                image=image,
                image2=image2,
                scale_selector=scale_selector,
                solution=solution,
                request=request,
                pbar=pbar,
                sahi_mode=sahi_mode
            )

            if image is None or (isinstance(image, np.ndarray) and image.size == 0):
                gr.Warning("Ошибка: изображение отсутствует...")
                return self._create_error_return() 
            if not scale and scale_selector == 'Шкала прибора в мкм':
                return self._create_error_return()
                
            # Выбор стратегии обработки
            processor = self._select_processor(model_change, sahi_mode)
            output_image, particle_data, annotations = processor(image, 
                    scale_input, confidence_threshold,
                    scale_selector, confidence_iou, 
                    number_detections, model_change,
                    round_value, slice_height, slice_width, 
                    overlap_height_ratio, overlap_width_ratio, 
                    pbar, orig_image, gray_image, scale)

            output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
            df = pd.DataFrame(particle_data)

            pbar.set_description("Построение таблицы...")
            builder = StatisticsBuilder(df, scale_selector, round_value=round_value, number_of_bins=number_of_bins)
            stats_df = builder.build_stats_table()
            pbar.update(1)

            pbar.set_description("Построение графиков...")
            fig = builder.build_distribution_fig()
            pbar.update(1)
            
            return (
                    output_image, df, fig, stats_df, gr.update(visible=True), len(df), 
                    gr.update(visible=True), gr.update(visible=True),  gr.update(visible=True), gr.update(visible=True), 
                    (orig_image, annotations), gr.update(visible=True),  gr.update(visible=True)
                    )
                    
        except Exception as e:
            self._handle_error(e)
            self._cleanup(pbar)
            return self._create_error_return()
        finally:
            self._cleanup(pbar)

    def _select_processor(self, model_change: str, sahi_mode: bool):
        """Выбор стратегии обработки в зависимости от модели и режима"""
        model_type = self.model_manager.model_types[model_change]
        if sahi_mode:
            return self._process_with_sahi
        elif model_type == 'yolo':
            return self._process_with_yolo
        elif model_type == 'detectron':
            return self._process_with_detectron
        else:
            raise ValueError(f"Неизвестный тип модели: {model_type}")
            
    def _process_with_yolo(self, image, 
                    scale_input, confidence_threshold,
                    scale_selector, confidence_iou, 
                    number_detections, model_change,
                    round_value, slice_height, slice_width, 
                    overlap_height_ratio, overlap_width_ratio, 
                    pbar, orig_image, gray_image, scale):
        """Обработка с использованием YOLO"""
        model = self.model_manager.get_model(model_change)
        pbar.set_description("YOLO обрабатывает изображение...")
        
        try:
            with torch.no_grad():
                results = model(
                    image, verbose=False, 
                    conf=confidence_threshold,
                    retina_masks=True, iou=confidence_iou,
                    max_det=number_detections, device="cuda:0"
                )
        except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
            self._handle_gpu_error(e)
            return self._create_error_return()
        except Exception as e:
            self._handle_error(e)
            return self._create_error_return()
            
        if torch.cuda.is_available():
            torch.cuda.synchronize()

        if len(results[0].boxes) == 0:
            gr.Info("Объекты не обнаружены.")
            return Error
        elif len(results[0].boxes) == number_detections:
           gr.Info("Достигнут предел количества обнаружений. Увеличьте максимальное количество обнаружений в настройках.")
        pbar.update(1)
        
        pbar.set_description("Обработка частиц...")
        output_image = orig_image.copy()
        thickness = self._get_scaled_thickness(output_image.shape[1], output_image.shape[0])
        particle_counter, particle_data, annotations = 1, [], []
        for r in results:
            if r.masks is not None and len(r.masks.xy) > 0:
                for mask, mask2 in zip(r.masks.xy, r.masks.data.cpu().numpy()):
                    particle_counter = self._analyze_particle(
                        points=mask,
                        gray_image=gray_image,
                        output_image=output_image,
                        scale_selector=scale_selector,
                        scale_input=scale_input,
                        scale=scale,
                        particle_counter=particle_counter,
                        round_value=round_value,
                        thickness=thickness,
                        particle_data=particle_data,
                        annotations=annotations,
                        raw_mask=mask2
                    )
        pbar.update(1)  
        return output_image, particle_data, annotations
    
    def _process_with_detectron(self, image, 
                    scale_input, confidence_threshold,
                    scale_selector, confidence_iou, 
                    number_detections, model_change,
                    round_value, slice_height, slice_width, 
                    overlap_height_ratio, overlap_width_ratio,
                    pbar, orig_image, gray_image, scale) -> Dict:
        """Обработка с использованием Detectron2"""
        cfg = self.model_manager.get_model(model_change)
        cfg.TEST.DETECTIONS_PER_IMAGE = number_detections
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confidence_threshold
        cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = confidence_iou

        pbar.set_description("Detectron2 обрабатывает изображение...")
        try:
            predictor = DefaultPredictor(cfg)
            results = predictor(image)
            masks = results['instances'].pred_masks.to("cpu").numpy()
        except Exception as e:
            self._handle_error(e)
            return self._create_error_return()
        if len(masks) == 0:
            gr.Info("Объекты не обнаружены.")
            return self._create_error_return()
        elif len(masks) == number_detections:
            gr.Info("Достигнут предел количества обнаружений. Увеличьте максимальное количество обнаружений в настройках.")
        pbar.update(1)
        
        pbar.set_description("Обработка частиц...")
        output_image = orig_image.copy()
        thickness = self._get_scaled_thickness(output_image.shape[1], output_image.shape[0])
        particle_counter, particle_data, annotations = 1, [], []
        for mask in masks:
            contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                continue
            contour = max(contours, key=cv2.contourArea)
            points = contour.squeeze()
            particle_counter = self._analyze_particle(
                points=points,
                gray_image=gray_image,
                output_image=output_image,
                scale_selector=scale_selector,
                scale_input=scale_input,
                scale=scale,
                particle_counter=particle_counter,
                round_value=round_value,
                thickness=thickness,
                particle_data=particle_data,
                annotations=annotations,
                raw_mask=mask
            )
        pbar.update(1)    
        return output_image, particle_data, annotations 
     
    def _process_with_sahi(self, image, 
                    scale_input, confidence_threshold,
                    scale_selector, confidence_iou, 
                    number_detections, model_change,
                    round_value, slice_height, slice_width, 
                    overlap_height_ratio, overlap_width_ratio,
                    pbar, orig_image, gray_image, scale) -> Dict:
        """Обработка с использованием SAHI"""
        model_type = self.model_manager.model_types[model_change]
       
        if model_type == 'yolo':
            detection_model = AutoDetectionModel.from_pretrained(
                model_type='ultralytics',
                model_path=self.model_manager.get_model_path(model_change),
                confidence_threshold=confidence_threshold,
                device="cuda",
            )
        else:
            detection_model = CustomDetectron2Model(
                model_path=self.model_manager.get_model_path(model_change),
                config_path=self.model_manager.get_config_path(model_change),
                confidence_threshold=confidence_threshold,
                device="cuda",
            )

        pbar.set_description("SAHI обрабатывает изображение...")
        try:
            results = get_sliced_prediction(
                image,
                detection_model,
                slice_height=slice_height,
                slice_width=slice_width,
                overlap_height_ratio=overlap_height_ratio,
                overlap_width_ratio=overlap_width_ratio,
                postprocess_match_threshold=confidence_iou,
                verbose=0,
            )
        except torch.cuda.OutOfMemoryError as e:
            self._handle_gpu_error(e)
            return self._create_error_return()        
        if len(results.object_prediction_list) == 0:
            gr.Info("Объекты не обнаружены.")
            return self._create_error_return()
        pbar.update(1) 
        
        pbar.set_description("Обработка частиц...")  
        output_image = orig_image.copy()
        thickness = self._get_scaled_thickness(output_image.shape[1], output_image.shape[0])
        particle_counter, particle_data, annotations = 1, [], []        
        for r in results.object_prediction_list:
            mask = r.mask.segmentation
            if isinstance(mask, list) and len(mask) > 0:
                flat_coords = np.concatenate(mask).astype(np.int32) if isinstance(mask[0], list) else np.array(mask, dtype=np.int32)
                if flat_coords.shape[0] < 6:
                    continue
                points = flat_coords.reshape(-1, 1, 2)
                particle_counter = self._analyze_particle(
                    points=points,
                    gray_image=gray_image,
                    output_image=output_image,
                    scale_selector=scale_selector,
                    scale_input=scale_input,
                    scale=scale,
                    particle_counter=particle_counter,
                    round_value=round_value,
                    thickness=thickness,
                    particle_data=particle_data,
                    annotations=None,
                    raw_mask=None
                )
        pbar.update(1)
        return output_image, particle_data, annotations 
     
    def _analyze_particle(self, points, gray_image,
                         output_image, scale_selector,
                         scale_input, scale, particle_counter,
                         round_value, thickness, particle_data,
                         annotations, raw_mask) -> int:
        """Анализ отдельной частицы"""
        if len(points) < 3:
            return particle_counter

        points = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        
        # Вычисление характеристик частицы
        area = cv2.contourArea(points)
        perimeter = cv2.arcLength(points, closed=True)
        distances = pdist(points[:, 0, :])
        diameter = np.max(distances) if len(distances) > 0 else 0
        
        # Эксцентриситет
        eccentricity = 0
        if len(points) >= 5:
            ellipse = cv2.fitEllipse(points)
            (xc, yc), (major_axis, minor_axis), angle = ellipse
            a, b = max(major_axis, minor_axis) / 2, min(major_axis, minor_axis) / 2
            eccentricity = np.sqrt(1 - (b ** 2 / a ** 2)) if a > b else 0

        # Средняя интенсивность
        mask_img = np.zeros_like(gray_image, dtype=np.uint8)
        cv2.fillPoly(mask_img, [points], 255)
        mean_intensity = cv2.mean(gray_image, mask=mask_img)[0]

        # Отрисовка контура
        cv2.polylines(output_image, [points], isClosed=True, color=(0, 255, 0), thickness=thickness)

        # Сохранение аннотации
        if annotations is not None and raw_mask is not None:
            annotations.append((raw_mask, f"Particle {particle_counter}"))

        # Масштабирование
        scale_factor = float(scale_input) / float(scale) if scale_selector == 'Шкала прибора в мкм' else 1
        scale_area = scale_factor ** 2

        # Добавление данных частицы
        particle_data.append({
            "№": round(particle_counter, round_value),
            "S [мкм²]" if scale_selector == 'Шкала прибора в мкм' else "S [пикс²]": round(area * scale_area, round_value),
            "P [мкм]" if scale_selector == 'Шкала прибора в мкм' else "P [пикс]": round(perimeter * scale_factor, round_value),
            "D [мкм]" if scale_selector == 'Шкала прибора в мкм' else "D [пикс]": round(diameter * scale_factor, round_value),
            "e": round(eccentricity, round_value),
            "I [ед.]": round(mean_intensity, round_value)
        })

        return particle_counter + 1

    def _get_scaled_thickness(self, image_width: int, image_height: int, 
                             base_width: int = 300, base_thickness: int = 1) -> int:
        """Вычисление толщины линии в зависимости от разрешения"""
        if image_width < base_width or image_height < base_width:
            return 1
        return max(1, int(base_thickness * (image_width / base_width)))
   
    def _handle_error(self, error: Exception):
        """Обработка ошибок"""
        gr.Warning(f"Критическая ошибка: {error}")
        print(f"Критическая ошибка: {error}")

    def _handle_gpu_error(self, error: Exception):
        """Обработка ошибок GPU"""
        gr.Warning("Ошибка: недостаточно памяти CUDA. Освобождаем память...")
        print("Ошибка: недостаточно памяти CUDA. Освобождаем память...")

    def _cleanup(self, pbar: Optional[tqdm] = None):
        """Очистка ресурсов"""
        if pbar:
            pbar.close()
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()