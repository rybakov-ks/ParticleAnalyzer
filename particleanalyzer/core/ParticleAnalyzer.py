import cv2
import numpy as np
import gradio as gr
import pandas as pd
import torch
from torch import device as torch_device
import os
import gc
from tqdm import tqdm
from typing import Optional, Tuple
from scipy.spatial.distance import pdist

try:
    from detectron2.engine import DefaultPredictor
    from particleanalyzer.core.CustomDetectron2Model import CustomDetectron2Model

    DETECTRON2_AVAILABLE = True
except ImportError:
    DETECTRON2_AVAILABLE = False
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

from particleanalyzer.core.ModelManager import ModelManager
from particleanalyzer.core.ImagePreprocessor import ImagePreprocessor
from particleanalyzer.core.StatisticsBuilder import StatisticsBuilder
from particleanalyzer.core.languages import translations
from particleanalyzer.core.language_context import LanguageContext

lang = "ru"


class ParticleAnalyzer:
    def __init__(self, default_lang="ru", device=None):
        """Инициализация анализатора частиц с настройкой окружения"""
        self._setup_environment(device)
        self.model_manager = ModelManager(device=self.device)
        self.preprocessor = ImagePreprocessor()
        self.error_return = self._create_error_return()
        self.default_lang = default_lang
        # Устанавливаем язык в контекст
        LanguageContext.set_language(default_lang)

    def _setup_environment(self, device=None):
        """Настройка параметров окружения и CUDA"""
        os.environ["GRADIO_TEMP_DIR"] = os.path.expanduser("~/.gradio_temp")
        if device is None:
            self.device = torch_device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch_device(device)
        if self.device.type == "cuda":
            torch.set_default_device("cuda")
            torch.backends.cudnn.enabled = True
            torch.backends.cudnn.benchmark = True
            # Дополнительные настройки для лучшей производительности
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            print(f"CUDA device in use: {torch.cuda.get_device_name(0)}")
        else:
            print("CUDA not available, using CPU")
            torch.set_default_device("cpu")

    def _get_translation(self, text):
        """Получение перевода текста на текущий язык"""
        return translations.get(self.lang, translations[self.default_lang]).get(
            text, text
        )

    def _determine_language(self, accept_language: str):
        """Определение языка на основе заголовка Accept-Language"""
        if not accept_language:
            return self.default_lang

        lang_code = accept_language.split(",")[0].lower()

        language_mapping = {
            "en-us": "en",
            "en": "en",
            "ru": "ru",
            "zh-cn": "zh-cn",
            "zh-tw": "zh-tw",
        }

        return language_mapping.get(
            lang_code, language_mapping.get(lang_code.split("-")[0], self.default_lang)
        )

    def _create_error_return(self) -> Tuple:
        """Создает кортеж для возврата в случае ошибки"""
        return (
            None,
            None,
            None,
            None,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            None,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )

    def analyze_image(
        self,
        image: np.ndarray,
        image2: Optional[np.ndarray],
        scale_input: float,
        confidence_threshold: float,
        scale_selector: str,
        confidence_iou: float,
        number_detections: int,
        solution: str,
        model_change: str,
        round_value: int,
        slice_height: int,
        slice_width: int,
        overlap_height_ratio: float,
        overlap_width_ratio: float,
        sahi_mode: bool,
        number_of_bins: int,
        segment_mode: bool,
        show_Feret_diametr: bool,
        api_key: bool,
        request: gr.Request,
    ) -> Tuple:
        """
        Основной метод для анализа изображения.
        """
        lang = self._determine_language(request.headers.get("Accept-Language", ""))
        LanguageContext.set_language(lang)
        self.lang = lang  # Для обратной совместимости
        try:
            pbar = tqdm(
                total=5,
                desc=self._get_translation("Подготовка..."),
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
            )

            if (
                image["background"] is None
                and image["composite"] is None
                and not image["layers"]
            ) and (image2 is None):
                gr.Warning(self._get_translation("Ошибка: изображение отсутствует..."))
                return self._create_error_return()

            image, orig_image, gray_image, scale, scale_factor_glob = (
                self.preprocessor.preprocess_image(
                    image=image,
                    image2=image2,
                    scale_selector=scale_selector,
                    solution=solution,
                    request=request,
                    pbar=pbar,
                    sahi_mode=sahi_mode,
                    lang=self.lang,
                )
            )

            if not scale and scale_selector == self._get_translation(
                "Instrument scale in µm"
            ):
                return self._create_error_return()

            # Выбор стратегии обработки
            processor = self._select_processor(model_change, sahi_mode)
            output_image, particle_data, annotations = processor(
                image,
                scale_input,
                confidence_threshold,
                scale_selector,
                confidence_iou,
                number_detections,
                model_change,
                round_value,
                slice_height,
                slice_width,
                overlap_height_ratio,
                overlap_width_ratio,
                pbar,
                orig_image,
                gray_image,
                scale,
                scale_factor_glob,
                show_Feret_diametr,
            )
            if output_image is None:
                return self._create_error_return()

            output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
            df = pd.DataFrame(particle_data)

            pbar.set_description(self._get_translation("Построение таблицы..."))
            builder = StatisticsBuilder(
                df,
                scale_selector,
                round_value=round_value,
                number_of_bins=number_of_bins,
                lang=self.lang,
            )
            stats_df = builder.build_stats_table()
            pbar.update(1)

            pbar.set_description(self._get_translation("Построение графиков..."))
            fig = builder.build_distribution_fig(image)
            pbar.update(1)

            return (
                output_image,
                df,
                fig,
                stats_df,
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                (orig_image, annotations) if segment_mode else None,
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=segment_mode),
                gr.update(visible=api_key),
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
        elif model_type == "yolo":
            return self._process_with_yolo
        elif model_type == "detectron":
            return self._process_with_detectron
        else:
            raise ValueError(f"Неизвестный тип модели: {model_type}")

    def _process_with_yolo(
        self,
        image,
        scale_input,
        confidence_threshold,
        scale_selector,
        confidence_iou,
        number_detections,
        model_change,
        round_value,
        slice_height,
        slice_width,
        overlap_height_ratio,
        overlap_width_ratio,
        pbar,
        orig_image,
        gray_image,
        scale,
        scale_factor_glob,
        show_Feret_diametr,
    ):
        """Обработка с использованием YOLO"""
        model = self.model_manager.get_model(model_change)
        pbar.set_description(self._get_translation("YOLO обрабатывает изображение..."))

        try:
            with torch.no_grad():
                results = model(
                    image,
                    verbose=False,
                    conf=confidence_threshold,
                    retina_masks=True,
                    iou=confidence_iou,
                    max_det=number_detections,
                    device=self.device,
                )
        except (torch.cuda.OutOfMemoryError, RuntimeError) as e:
            self._handle_gpu_error(e)
            return None, None, None
        except Exception as e:
            self._handle_error(e)
            return None, None, None

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        if len(results[0].boxes) == 0:
            gr.Info(self._get_translation("Объекты не обнаружены."))
            return None, None, None
        elif len(results[0].boxes) == number_detections:
            gr.Info(
                self._get_translation(
                    "Достигнут предел количества обнаружений. Увеличьте максимальное количество обнаружений в настройках."
                )
            )
        pbar.update(1)

        pbar.set_description(self._get_translation("Обработка частиц..."))
        output_image = orig_image.copy()
        thickness = self._get_scaled_thickness(
            output_image.shape[1], output_image.shape[0]
        )
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
                        raw_mask=mask2,
                        scale_factor_glob=scale_factor_glob,
                        show_Feret_diametr=show_Feret_diametr,
                    )
        pbar.update(1)
        return output_image, particle_data, annotations

    def _process_with_detectron(
        self,
        image,
        scale_input,
        confidence_threshold,
        scale_selector,
        confidence_iou,
        number_detections,
        model_change,
        round_value,
        slice_height,
        slice_width,
        overlap_height_ratio,
        overlap_width_ratio,
        pbar,
        orig_image,
        gray_image,
        scale,
        scale_factor_glob,
        show_Feret_diametr,
    ):
        """Обработка с использованием Detectron2"""
        cfg = self.model_manager.get_model(model_change)
        cfg.TEST.DETECTIONS_PER_IMAGE = number_detections
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = confidence_threshold
        cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = confidence_iou

        pbar.set_description(
            self._get_translation("Detectron2 обрабатывает изображение...")
        )
        try:
            predictor = DefaultPredictor(cfg)
            results = predictor(image)
            masks = results["instances"].pred_masks.to("cpu").numpy()
        except Exception as e:
            self._handle_error(e)
            return None, None, None
        if len(masks) == 0:
            gr.Info(self._get_translation("Объекты не обнаружены."))
            return None, None, None
        elif len(masks) == number_detections:
            gr.Info(
                self._get_translation(
                    "Достигнут предел количества обнаружений. Увеличьте максимальное количество обнаружений в настройках."
                )
            )
        pbar.update(1)

        pbar.set_description(self._get_translation("Обработка частиц..."))
        output_image = orig_image.copy()
        thickness = self._get_scaled_thickness(
            output_image.shape[1], output_image.shape[0]
        )
        particle_counter, particle_data, annotations = 1, [], []
        for mask in masks:
            contours, _ = cv2.findContours(
                mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
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
                raw_mask=mask,
                scale_factor_glob=scale_factor_glob,
                show_Feret_diametr=show_Feret_diametr,
            )
        pbar.update(1)
        return output_image, particle_data, annotations

    def _process_with_sahi(
        self,
        image,
        scale_input,
        confidence_threshold,
        scale_selector,
        confidence_iou,
        number_detections,
        model_change,
        round_value,
        slice_height,
        slice_width,
        overlap_height_ratio,
        overlap_width_ratio,
        pbar,
        orig_image,
        gray_image,
        scale,
        scale_factor_glob,
        show_Feret_diametr,
    ):
        """Обработка с использованием SAHI"""
        model_type = self.model_manager.model_types[model_change]

        if model_type == "yolo":
            detection_model = AutoDetectionModel.from_pretrained(
                model_type="ultralytics",
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

        pbar.set_description(self._get_translation("SAHI обрабатывает изображение..."))
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
            return None, None, None
        if len(results.object_prediction_list) == 0:
            gr.Info(self._get_translation("Объекты не обнаружены."))
            return None, None, None
        pbar.update(1)

        pbar.set_description(self._get_translation("Обработка частиц..."))
        output_image = orig_image.copy()
        thickness = self._get_scaled_thickness(
            output_image.shape[1], output_image.shape[0]
        )
        particle_counter, particle_data, annotations = 1, [], []
        for r in results.object_prediction_list:
            mask = r.mask.segmentation
            if isinstance(mask, list) and len(mask) > 0:
                flat_coords = (
                    np.concatenate(mask).astype(np.int32)
                    if isinstance(mask[0], list)
                    else np.array(mask, dtype=np.int32)
                )
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
                    raw_mask=None,
                    scale_factor_glob=scale_factor_glob,
                    show_Feret_diametr=show_Feret_diametr,
                )
        pbar.update(1)
        return output_image, particle_data, annotations

    def _analyze_particle(
        self,
        points,
        gray_image,
        output_image,
        scale_selector,
        scale_input,
        scale,
        particle_counter,
        round_value,
        thickness,
        particle_data,
        annotations,
        raw_mask,
        scale_factor_glob,
        show_Feret_diametr,
    ) -> int:
        """Анализ отдельной частицы с расчетом Feret-диаметров"""
        if len(points) < 3:
            return particle_counter

        points = np.array(points, dtype=np.int32).reshape((-1, 1, 2))

        # Вычисление центроида (геометрического центра)
        moments = cv2.moments(points)
        if moments["m00"] != 0:
            centroid_x = moments["m10"] / moments["m00"]
            centroid_y = moments["m01"] / moments["m00"]
        else:
            centroid_x, centroid_y = np.mean(points[:, 0, :], axis=0)

        # Вычисление базовых характеристик
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
            eccentricity = np.sqrt(1 - (b**2 / a**2)) if a > b else 0

        # Расчет Feret-диаметров и углов
        def get_feret(contour, angles=np.arange(0, 180, 1)):
            feret_values = []
            feret_angles = []

            for angle in angles:
                M = cv2.getRotationMatrix2D((0, 0), angle, 1)
                rotated = cv2.transform(contour, M)
                x_coords = rotated[:, 0, 0]
                feret = x_coords.max() - x_coords.min()
                feret_values.append(feret)
                feret_angles.append(angle)

            feret_max = max(feret_values)
            feret_min = min(feret_values)
            feret_mean = np.mean(feret_values)
            angle_max = feret_angles[feret_values.index(feret_max)]
            angle_min = feret_angles[feret_values.index(feret_min)]

            return feret_max, feret_min, feret_mean, angle_max, angle_min

        feret_max, feret_min, feret_mean, angle_max, angle_min = get_feret(points)

        # Средняя интенсивность
        mask_img = np.zeros_like(gray_image, dtype=np.uint8)
        cv2.fillPoly(mask_img, [points], 255)
        mean_intensity = cv2.mean(gray_image, mask=mask_img)[0]

        # Отрисовка контура и Feret-линий (опционально)
        cv2.polylines(
            output_image,
            [points],
            isClosed=True,
            color=(0, 255, 0),
            thickness=thickness,
        )
        if show_Feret_diametr:
            self._draw_feret_lines(
                output_image, points, angle_max, (0, 255, 255)
            )  # Желтый - Feret max
            self._draw_feret_lines(
                output_image, points, angle_min, (255, 0, 0)
            )  # Синий - Feret min

        # Сохранение аннотации
        if annotations is not None and raw_mask is not None:
            annotations.append((raw_mask, f"Particle {particle_counter}"))

        # Масштабирование
        scale_factor = (
            float(scale_input) / float(scale) * scale_factor_glob
            if scale_selector == "Instrument scale in µm"
            else 1 * scale_factor_glob
        )
        scale_area = scale_factor**2

        # Добавление данных частицы
        particle_data.append(
            {
                "№": round(particle_counter, round_value),
                "centroid_x": round(centroid_x, round_value),
                "centroid_y": round(centroid_y, round_value),
                (
                    self._get_translation("D [мкм]")
                    if scale_selector == self._get_translation("Instrument scale in µm")
                    else self._get_translation("D [пикс]")
                ): round(diameter * scale_factor, round_value),
                (
                    self._get_translation("Dₘₐₓ [мкм]")
                    if scale_selector == self._get_translation("Instrument scale in µm")
                    else self._get_translation("Dₘₐₓ [пикс]")
                ): round(feret_max * scale_factor, round_value),
                (
                    self._get_translation("Dₘᵢₙ [мкм]")
                    if scale_selector == self._get_translation("Instrument scale in µm")
                    else self._get_translation("Dₘᵢₙ [пикс]")
                ): round(feret_min * scale_factor, round_value),
                (
                    self._get_translation("Dₘₑₐₙ [мкм]")
                    if scale_selector == self._get_translation("Instrument scale in µm")
                    else self._get_translation("Dₘₑₐₙ [пикс]")
                ): round(feret_mean * scale_factor, round_value),
                (
                    self._get_translation("θₘₐₓ [°]")
                    if scale_selector == self._get_translation("Instrument scale in µm")
                    else self._get_translation("θₘₐₓ [°]")
                ): round(angle_max, round_value),
                (
                    self._get_translation("θₘᵢₙ [°]")
                    if scale_selector == self._get_translation("Instrument scale in µm")
                    else self._get_translation("θₘᵢₙ [°]")
                ): round(angle_min, round_value),
                (
                    self._get_translation("S [мкм²]")
                    if scale_selector == self._get_translation("Instrument scale in µm")
                    else self._get_translation("S [пикс²]")
                ): round(area * scale_area, round_value),
                (
                    self._get_translation("P [мкм]")
                    if scale_selector == self._get_translation("Instrument scale in µm")
                    else self._get_translation("P [пикс]")
                ): round(perimeter * scale_factor, round_value),
                "e": round(eccentricity, round_value),
                self._get_translation("I [ед.]"): round(mean_intensity, round_value),
            }
        )

        return particle_counter + 1

    def _draw_feret_lines(self, image, contour, angle, color=(0, 255, 0), thickness=2):
        """Отрисовка Feret-линий"""
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            return
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        center = (cx, cy)

        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        rotated = cv2.transform(contour, M)

        x_coords = rotated[:, 0, 0]
        if len(x_coords) == 0:
            return

        x_min, x_max = np.min(x_coords), np.max(x_coords)
        y_center = np.mean(rotated[:, 0, 1])

        pt1_rotated = np.array([[[x_min, y_center]]], dtype=np.float32)
        pt2_rotated = np.array([[[x_max, y_center]]], dtype=np.float32)

        M_inv = cv2.getRotationMatrix2D(center, -angle, 1.0)
        pt1 = cv2.transform(pt1_rotated, M_inv)[0][0]
        pt2 = cv2.transform(pt2_rotated, M_inv)[0][0]

        cv2.line(
            image, tuple(pt1.astype(int)), tuple(pt2.astype(int)), color, thickness
        )

    def _get_scaled_thickness(
        self,
        image_width: int,
        image_height: int,
        base_width: int = 300,
        base_thickness: int = 1,
    ) -> int:
        """Вычисление толщины линии в зависимости от разрешения"""
        if image_width < base_width or image_height < base_width:
            return 1
        return max(1, int(base_thickness * (image_width / base_width)))

    def _handle_error(self, error: Exception):
        """Обработка ошибок"""
        gr.Warning(f"{self._get_translation('Критическая ошибка')}: {error}")
        print(f"{self._get_translation('Критическая ошибка')}: {error}")

    def _handle_gpu_error(self, error: Exception):
        """Обработка ошибок GPU"""
        gr.Warning(
            self._get_translation(
                "Ошибка: недостаточно памяти CUDA. Освобождаем память. Попробуйте уменьшить разрешение изображения или включите режим SAHI..."
            )
        )
        print(
            self._get_translation(
                "Ошибка: недостаточно памяти CUDA. Освобождаем память. Попробуйте уменьшить разрешение изображения или включите режим SAHI..."
            )
        )

    def _cleanup(self, pbar: Optional[tqdm] = None):
        """Очистка ресурсов"""
        if pbar:
            pbar.close()
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
