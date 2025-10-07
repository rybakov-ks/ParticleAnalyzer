import os
import onnxruntime as ort
import numpy as np
import cv2
import supervision as sv


class ONNXLoader:
    MODEL_MAPPING = {
        "RF-DETR Seg (Preview)": "rf_detr_model.onnx",
    }

    def __init__(self, device="cpu"):
        self._base_path = os.path.join(os.path.dirname(__file__), "..", "model")
        self.device = device
        self.models = {}

        for display_name, file_name in self.MODEL_MAPPING.items():
            model_path = self._model_path(file_name)
            if os.path.exists(model_path):
                try:
                    providers = ["CPUExecutionProvider"]
                    if (
                        device == "cuda"
                        and "CUDAExecutionProvider" in ort.get_available_providers()
                    ):
                        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]

                    session = ort.InferenceSession(model_path, providers=providers)
                    self.models[display_name] = {
                        "session": session,
                        "input_name": session.get_inputs()[0].name,
                        "output_names": [
                            output.name for output in session.get_outputs()
                        ],
                    }
                    # print(f"ONNX модель {display_name} загружена")
                except Exception as e:
                    print(f"❌ Ошибка загрузки ONNX модели {display_name}: {e}")

    def _model_path(self, name: str) -> str:
        return os.path.join(self._base_path, name)

    def get_model(self, model_name: str):
        return self.models.get(model_name)

    def get_model_path(self, model_name: str):
        if model_name in self.MODEL_MAPPING:
            return self._model_path(self.MODEL_MAPPING[model_name])
        return None

    def predict_from_numpy(
        self,
        model_name: str,
        image_np: np.ndarray,
        confidence_threshold=0.3,
        max_detections=300,
    ):
        """Предсказание из numpy массива"""
        model_info = self.get_model(model_name)
        if not model_info:
            raise ValueError(f"Модель {model_name} не найдена")

        # Препроцессинг
        input_tensor, original_size = self._preprocess_numpy(image_np, model_name)

        # Инференс
        outputs = model_info["session"].run(
            model_info["output_names"], {model_info["input_name"]: input_tensor}
        )

        # Постпроцессинг
        return self._postprocess_rfdetr(
            outputs, original_size, confidence_threshold, max_detections
        )

    def _preprocess_numpy(self, image_np: np.ndarray, model_name: str):
        """Препроцессинг numpy массива"""
        original_size = (image_np.shape[1], image_np.shape[0])

        if "RF-DETR" in model_name:
            target_size = (432, 432)
        else:
            target_size = (640, 640)

        image_resized = cv2.resize(
            image_np, target_size, interpolation=cv2.INTER_LINEAR
        )

        if len(image_resized.shape) == 3 and image_resized.shape[2] == 3:
            image_resized = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)

        image_processed = image_resized.astype(np.float32) / 255.0
        image_processed = (
            image_processed - np.array([0.485, 0.456, 0.406], dtype=np.float32)
        ) / np.array([0.229, 0.224, 0.225], dtype=np.float32)
        image_processed = image_processed.transpose(2, 0, 1)
        image_processed = np.expand_dims(image_processed, axis=0)

        return image_processed, original_size

    def _postprocess_rfdetr(
        self, outputs, original_size, confidence_threshold, max_detections
    ):
        """Постпроцессинг для RF-DETR"""
        dets = outputs[0][0]  # [200, 4]
        labels = outputs[1][0]  # [200, 2]
        masks = outputs[2][0]  # [200, 108, 108]

        confidences = labels[:, 1]
        class_ids = labels[:, 0]

        valid_indices = confidences > confidence_threshold

        if not np.any(valid_indices):
            return sv.Detections.empty()

        filtered_dets = dets[valid_indices]
        filtered_confidences = confidences[valid_indices]
        filtered_class_ids = class_ids[valid_indices]
        filtered_masks = masks[valid_indices]

        if len(filtered_dets) > max_detections:
            indices = np.argsort(filtered_confidences)[::-1][:max_detections]
            filtered_dets = filtered_dets[indices]
            filtered_confidences = filtered_confidences[indices]
            filtered_class_ids = filtered_class_ids[indices]
            filtered_masks = filtered_masks[indices]

        scale_x = original_size[0] / 432
        scale_y = original_size[1] / 432

        bboxes = filtered_dets.copy()

        if bboxes.max() <= 1.0:
            bboxes[:, [0, 2]] *= 432
            bboxes[:, [1, 3]] *= 432

        bboxes[:, [0, 2]] *= scale_x
        bboxes[:, [1, 3]] *= scale_y

        scaled_masks = []
        for mask in filtered_masks:
            mask_resized = cv2.resize(
                mask, original_size, interpolation=cv2.INTER_LINEAR
            )
            scaled_masks.append(mask_resized > 0.5)

        return sv.Detections(
            xyxy=bboxes,
            confidence=filtered_confidences,
            class_id=filtered_class_ids.astype(int),
            mask=np.array(scaled_masks),
        )
