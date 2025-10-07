import cv2
import numpy as np
import easyocr
from PIL import Image, ImageDraw, ImageFont
import re


class ScaleProcessor:
    """
    Класс инкапсулирует логику: предобработка, OCR, безопасные вырезки и обработку изображения моделью YOLO.
    """

    def __init__(self, model, device) -> None:
        # Инициализация OCR и модели детекции
        self.device = device
        self.reader = easyocr.Reader(
            ["en"], gpu=self.device.type == "cuda", verbose=False
        )
        self.model = model

    def preprocess_text_region(self, image_region, method: str = "adaptive"):
        if image_region.size == 0:
            return image_region

        h, w = image_region.shape[:2]
        if w < 150 or h < 50:
            scale = max(4, 150 // max(w, 1), 50 // max(h, 1))
            new_w, new_h = w * scale, h * scale
            image_region = cv2.resize(
                image_region, (new_w, new_h), interpolation=cv2.INTER_CUBIC
            )

        # ОБРАБОТКА РАЗНЫХ ТИПОВ ИЗОБРАЖЕНИЙ
        if len(image_region.shape) == 3:
            # Цветное изображение - конвертируем в grayscale
            gray = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)
        else:
            # Уже grayscale - используем как есть
            gray = image_region

        # Убеждаемся, что тип данных правильный
        if gray.dtype != np.uint8:
            gray = gray.astype(np.uint8)

        if method == "adaptive":
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
            binary = cv2.adaptiveThreshold(
                enhanced,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2,
            )
        elif method == "otsu":
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            _, binary = cv2.threshold(
                enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
        elif method == "inverse":
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            _, binary = cv2.threshold(
                enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )
        else:
            binary = gray

        return binary

    def try_additional_preprocessing(self, image_region):
        additional_methods = []
        gray = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)
        enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=30)
        additional_methods.append(enhanced)
        median = cv2.medianBlur(gray, 3)
        additional_methods.append(median)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        additional_methods.append(closed)
        return additional_methods

    def extract_scale_text_from_region(self, image_region):
        try:
            if image_region.size == 0:
                return "Empty region"

            ocr_corrections = {
                "O": "0",
                "o": "0",
                "Q": "0",
                "D": "0",
                "l": "1",
                "I": "1",
                "|": "1",
                "i": "1",
                "j": "1",
                "Z": "2",
                "z": "2",
                "B": "8",
                "b": "8",
                "A": "4",
                "a": "4",
                "S": "5",
                "s": "5",
                "G": "6",
                "g": "6",
                "T": "7",
                "t": "7",
                "q": "9",
                ",": ".",
                ";": ".",
                ":": ".",
            }

            reverse_corrections = {
                "1m": "im",
                "1n": "in",
            }

            preprocessing_methods = ["adaptive", "otsu", "inverse"]
            all_results = []

            for method in preprocessing_methods:
                try:
                    processed_region = self.preprocess_text_region(image_region, method)
                    results = self.reader.readtext(
                        processed_region,
                        detail=1,
                        width_ths=0.7,
                        height_ths=0.7,
                        paragraph=False,
                        batch_size=1,
                    )
                    if results:
                        for bbox, text, confidence in results:
                            if confidence > 0.2:
                                all_results.append((text, confidence, method))
                except Exception as e:
                    print(f"Ошибка в методе {method}: {e}")
                    continue

            if not all_results:
                additional_images = self.try_additional_preprocessing(image_region)
                for i, additional_img in enumerate(additional_images):
                    try:
                        results = self.reader.readtext(
                            additional_img,
                            detail=1,
                            width_ths=0.5,
                            height_ths=0.5,
                            paragraph=False,
                            batch_size=1,
                        )
                        if results:
                            for bbox, text, confidence in results:
                                if confidence > 0.15:
                                    all_results.append(
                                        (text, confidence, f"additional_{i}")
                                    )
                    except Exception as e:
                        print(f"Ошибка в дополнительном методе {i}: {e}")
                        continue

            if not all_results:
                return None

            all_results.sort(key=lambda x: x[1], reverse=True)

            all_texts = []
            all_units = []
            combined_texts = []

            direct_pattern = re.compile(
                r"(\d+[.,]?\d*)\s*(µm|um|nm|mm|m)", re.IGNORECASE
            )

            for text, confidence, method in all_results:
                normalized_text = (
                    text.replace("µ m", "µm").replace("u m", "um").replace(" U m", "um")
                )
                m = direct_pattern.search(normalized_text)
                if m and confidence > 0.15:
                    num_part = m.group(1)
                    unit_part = m.group(2)
                    unit_part = (
                        "µm" if unit_part.lower() in ["um", "µm"] else unit_part.lower()
                    )
                    combined_texts.append(
                        (f"{num_part}{unit_part}", float(confidence), method, text)
                    )

                corrected_text = text
                for wrong, right in ocr_corrections.items():
                    corrected_text = corrected_text.replace(wrong, right)
                for wrong, right in reverse_corrections.items():
                    corrected_text = corrected_text.replace(wrong, right)
                cleaned = "".join(
                    c for c in corrected_text if c.isdigit() or c in ".,nmµ"
                )
                has_numbers = any(c.isdigit() for c in cleaned)
                has_units = any(
                    c in cleaned.lower() for c in ["nm", "µm", "mm", "m", "n", "µ"]
                )
                if len(cleaned) <= 3 and has_units and not has_numbers:
                    all_units.append((cleaned, confidence, method, text))
                elif has_numbers and has_units:
                    combined_texts.append((cleaned, confidence, method, text))
                elif has_numbers:
                    all_texts.append((cleaned, confidence, method, text))
                elif has_units:
                    all_units.append((cleaned, confidence, method, text))

            valid_combined_texts = [
                (cleaned, conf, method, original)
                for cleaned, conf, method, original in combined_texts
                if conf > 0.5
            ]

            if valid_combined_texts:
                number_patterns = [r"\d+\.\d+", r"\d+,\d+", r"\d+"]
                best_combined = None
                best_confidence = 0
                for cleaned, confidence, method, original in valid_combined_texts:
                    numbers = []
                    for pattern in number_patterns:
                        matches = re.findall(pattern, cleaned)
                        numbers.extend(matches)
                    if numbers:
                        number = numbers[0]
                        try:
                            num_value = float(number.replace(",", "."))
                            if num_value <= 0 or num_value > 10000:
                                continue
                        except Exception:
                            continue
                        units = "µm"
                        if "nm" in cleaned.lower() or "n" in cleaned.lower():
                            units = "nm"
                        elif "µm" in cleaned.lower() or "µ" in cleaned.lower():
                            units = "µm"
                        elif "mm" in cleaned.lower():
                            units = "mm"
                        if (
                            len(cleaned) >= 3
                            and confidence > best_confidence
                            and 0.1 <= num_value <= 1000
                        ):
                            best_combined = (
                                number,
                                units,
                                confidence,
                                method,
                                original,
                            )
                            best_confidence = confidence
                if best_combined:
                    main_number, units, conf, method, original = best_combined
                    try:
                        num_value = float(main_number.replace(",", "."))
                        if num_value <= 0 or num_value > 10000:
                            return f"Unreasonable value: {main_number}"
                    except Exception:
                        return f"Invalid number: {main_number}"
                    return f"{main_number}{units}"

            if not all_texts:
                return None

            filtered_texts = []
            for cleaned, confidence, method, original in all_texts:
                if (
                    len(cleaned) <= 8
                    and any(c.isdigit() for c in cleaned)
                    and not any(c in cleaned for c in ["|"])
                ):
                    filtered_texts.append((cleaned, confidence, method, original))
            if not filtered_texts:
                return None

            number_patterns = [r"\d+\.\d+", r"\d+,\d+", r"\d+"]
            all_numbers = []
            for cleaned, confidence, method, original in filtered_texts:
                for pattern in number_patterns:
                    matches = re.findall(pattern, cleaned)
                    for match in matches:
                        all_numbers.append((match, confidence, method, original))
            if not all_numbers:
                return None

            main_number, num_conf, num_method, num_original = max(
                all_numbers, key=lambda x: x[1]
            )

            units = "µm"
            if all_units:
                best_units_text, units_conf, units_method, units_original = max(
                    all_units, key=lambda x: x[1]
                )
                if "nm" in best_units_text.lower() or "n" in best_units_text.lower():
                    units = "nm"
                elif "µm" in best_units_text.lower() or "µ" in best_units_text.lower():
                    units = "µm"
                elif "mm" in best_units_text.lower():
                    units = "mm"
                elif "m" in best_units_text.lower():
                    units = "µm"
            else:
                for cleaned, confidence, method, original in all_texts:
                    if (
                        "um" in original.lower()
                        or "µm" in original.lower()
                        or "u m" in original.lower()
                        or "µ m" in original.lower()
                    ):
                        units = "µm"
                        break
                    if "nm" in cleaned.lower() or "n" in cleaned.lower():
                        units = "nm"
                        break
                    elif "µm" in cleaned.lower() or "µ" in cleaned.lower():
                        units = "µm"
                        break
                    elif "mm" in cleaned.lower():
                        units = "mm"
                        break

            try:
                num_value = float(main_number.replace(",", "."))
                if num_value <= 0 or num_value > 10000:
                    return f"Unreasonable value: {main_number}"
            except Exception:
                return f"Invalid number: {main_number}"

            return f"{main_number}{units}"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def safe_crop(image, bbox, padding: int = 0):
        x1, y1, x2, y2 = map(int, bbox)
        h, w = image.shape[:2]
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(w, x2 + padding)
        y2 = min(h, y2 + padding)
        if x2 <= x1 or y2 <= y1:
            return None
        region = image[y1:y2, x1:x2]
        if region.size == 0:
            return None
        return region

    def process_image(self, input_image, confidence_threshold):
        if isinstance(input_image, str):
            image = cv2.imread(input_image)
        else:
            image = cv2.cvtColor(np.array(input_image), cv2.COLOR_RGB2BGR)

        original_image = image.copy()

        results = self.model(image, conf=confidence_threshold, device=self.device)
        # annotated_image = results[0].plot()
        annotated_image = image

        info_bar_height = None
        scale_bar_width = None
        scale_text_value = "Not detected"

        info_bar_image = None
        scale_bar_image = None
        scale_text_image = None

        scale_bar_left_mid = None
        scale_bar_right_mid = None

        detected_elements = {
            "info_bar": [],
            "scale_bar": [],
            "scale_text": [],
        }

        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy()
                if class_name in ["info_bar", "scale_bar", "scale_text"]:
                    detected_elements[class_name].append((bbox, confidence))

        if detected_elements["info_bar"]:
            bbox, confidence = max(detected_elements["info_bar"], key=lambda x: x[1])
            height_pixels = bbox[3] - bbox[1]
            info_bar_height = int(height_pixels)
            info_bar_region = self.safe_crop(original_image, bbox)
            if info_bar_region is not None:
                info_bar_image = cv2.cvtColor(info_bar_region, cv2.COLOR_BGR2RGB)

        if detected_elements["scale_bar"]:
            bbox, confidence = max(detected_elements["scale_bar"], key=lambda x: x[1])
            width_pixels = bbox[2] - bbox[0]
            scale_bar_width = int(width_pixels)

            x1, y1, x2, y2 = bbox
            mid_y = (y1 + y2) / 2

            scale_bar_left_mid = (int(x1), int(mid_y))
            scale_bar_right_mid = (int(x2), int(mid_y))

            scale_bar_region = self.safe_crop(original_image, bbox)
            if scale_bar_region is not None:
                scale_bar_image = cv2.cvtColor(scale_bar_region, cv2.COLOR_BGR2RGB)

        if detected_elements["scale_text"]:
            bbox, confidence = max(detected_elements["scale_text"], key=lambda x: x[1])
            scale_text_region_ocr = self.safe_crop(original_image, bbox, padding=10)
            if scale_text_region_ocr is not None:
                scale_text_value = self.extract_scale_text_from_region(
                    scale_text_region_ocr
                )
            scale_text_region_display = self.safe_crop(original_image, bbox)
            if scale_text_region_display is not None:
                scale_text_image = cv2.cvtColor(
                    scale_text_region_display, cv2.COLOR_BGR2RGB
                )

        if info_bar_height is not None:
            crop_height = original_image.shape[0] - info_bar_height
            cropped_image = original_image[:crop_height, :]
            final_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        else:
            final_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

        placeholder = np.zeros((100, 300, 3), dtype=np.uint8)
        cv2.putText(
            placeholder,
            "Not detected",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        placeholder_rgb = cv2.cvtColor(placeholder, cv2.COLOR_BGR2RGB)

        if (
            scale_bar_width is not None
            and isinstance(scale_text_value, str)
            and scale_text_value not in ["Not detected", None]
        ):
            final_image = self.draw_scale_overlay_pil_cv2(
                final_image, scale_bar_width, scale_text_value
            )

        # result_text = "📊 MEASUREMENT RESULTS:\n\n"
        # result_text += f"📏 Info bar height: {info_bar_height if info_bar_height else 'Not detected'} pixels\n"
        # result_text += f"📐 Scale bar width: {scale_bar_width if scale_bar_width else 'Not detected'} pixels\n"
        # result_text += f"🔢 Scale: {scale_text_value[:-2]} {scale_text_value[-2:]}\n"

        if scale_text_value is None:
            scale_type = None
            scale_value = 1
        else:
            scale_type = scale_text_value[-2:]
            scale_value = scale_text_value[:-2]

        return (
            final_image,
            info_bar_image if info_bar_image is not None else placeholder_rgb,
            scale_bar_image if scale_bar_image is not None else placeholder_rgb,
            scale_text_image if scale_text_image is not None else placeholder_rgb,
            (scale_bar_width, scale_value, scale_type),
            (scale_bar_left_mid, scale_bar_right_mid),
        )

    def draw_scale_overlay_pil_cv2(
        self,
        rgb_image: np.ndarray,
        scale_bar_width_px: int,
        scale_text: str,
        anchor: str = "top-right",
        margin: int = 20,
        bar_height: int = 8,
        color: tuple = (255, 255, 255),
        bg_color: tuple = (0, 0, 0),
        text_color: tuple = (255, 255, 255),
        font_size: int = 20,
        bg_alpha: float = 0.4,
    ) -> np.ndarray:
        image = rgb_image.copy()
        h, w = image.shape[:2]

        if scale_bar_width_px is None or scale_bar_width_px <= 0:
            return image

        bar_length = int(scale_bar_width_px)
        padding = 10

        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)
            except (OSError, IOError):
                font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), scale_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        box_width = max(bar_length, text_width) + 2 * padding
        box_height = bar_height + text_height + 3 * padding

        if anchor == "top-right":
            x = w - box_width - margin
            y = margin
        elif anchor == "top-left":
            x = margin
            y = margin
        elif anchor == "bottom-right":
            x = w - box_width - margin
            y = h - box_height - margin
        else:  # bottom-left
            x = margin
            y = h - box_height - margin

        overlay = image.copy()
        cv2.rectangle(overlay, (x, y), (x + box_width, y + box_height), bg_color, -1)
        image = cv2.addWeighted(overlay, bg_alpha, image, 1 - bg_alpha, 0)

        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)

        bar_x = x + (box_width - bar_length) // 2
        bar_y = y + box_height - padding - bar_height
        draw.rectangle(
            [bar_x, bar_y, bar_x + bar_length, bar_y + bar_height],
            fill=color,
            outline=None,
        )

        text_x = x + (box_width - text_width) // 2
        text_y = y + padding

        draw.text((text_x, text_y), scale_text, fill=text_color, font=font)

        result_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        return result_image
