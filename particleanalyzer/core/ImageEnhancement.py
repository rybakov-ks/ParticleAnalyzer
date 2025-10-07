import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ImageEnhancement:
    """
    Класс для улучшения качества изображений с различными методами.
    Поддерживает денойзинг, увеличение резкости, улучшение контраста и другие операции.
    """

    def __init__(self):
        self.enhancement_methods = {
            "denoise": self._denoise_image,
            "sharpen": self._sharpen_image,
            "contrast": self._enhance_contrast,
            "histogram_eq": self._histogram_equalization,
            "adaptive_eq": self._adaptive_histogram_eq,
            "unsharp_mask": self._unsharp_mask,
            "bilateral_filter": self._bilateral_filter,
            "gaussian_blur": self._gaussian_blur,
            "median_filter": self._median_filter,
            "nlm_denoise": self._nlm_denoise,
            "gamma_correction": self._gamma_correction,
            "log_transform": self._log_transform,
            "power_transform": self._power_transform,
        }

    def enhance_image(
        self, image: np.ndarray, method: str = "sharpen", **kwargs
    ) -> np.ndarray:
        """
        Основной метод для улучшения изображения.

        Args:
            image: Входное изображение (BGR, RGB или Grayscale)
            method: Метод улучшения из доступных
            **kwargs: Дополнительные параметры для метода

        Returns:
            Улучшенное изображение

        Raises:
            ValueError: Если указан неизвестный метод
        """
        if method not in self.enhancement_methods:
            available_methods = list(self.enhancement_methods.keys())
            raise ValueError(
                f"Неизвестный метод '{method}'. Доступные: {available_methods}"
            )

        try:
            logger.info(f"Применяем метод улучшения: {method}")
            enhanced = self.enhancement_methods[method](image, **kwargs)
            logger.info(f"Улучшение изображения завершено. Размер: {enhanced.shape}")
            return enhanced
        except Exception as e:
            logger.error(f"Ошибка при улучшении изображения методом {method}: {e}")
            return image

    def _denoise_image(
        self, image: np.ndarray, method: str = "bilateral", **kwargs
    ) -> np.ndarray:
        """
        Удаление шума с изображения.

        Args:
            image: Входное изображение
            method: Метод денойзинга ('bilateral', 'gaussian', 'median', 'nlm')
            **kwargs: Параметры для конкретного метода

        Returns:
            Очищенное от шума изображение
        """
        if len(image.shape) == 3:
            # Для цветных изображений применяем к каждому каналу
            channels = cv2.split(image)
            denoised_channels = []

            for channel in channels:
                denoised_channel = self._apply_denoise_method(channel, method, **kwargs)
                denoised_channels.append(denoised_channel)

            return cv2.merge(denoised_channels)
        else:
            return self._apply_denoise_method(image, method, **kwargs)

    def _apply_denoise_method(
        self, image: np.ndarray, method: str, **kwargs
    ) -> np.ndarray:
        """Применение конкретного метода денойзинга."""
        if method == "bilateral":
            d = kwargs.get("d", 9)
            sigma_color = kwargs.get("sigma_color", 75)
            sigma_space = kwargs.get("sigma_space", 75)
            return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

        elif method == "gaussian":
            kernel_size = kwargs.get("kernel_size", (5, 5))
            sigma = kwargs.get("sigma", 0)
            return cv2.GaussianBlur(image, kernel_size, sigma)

        elif method == "median":
            kernel_size = kwargs.get("kernel_size", 5)
            return cv2.medianBlur(image, kernel_size)

        elif method == "nlm":
            h = kwargs.get("h", 10)
            template_window_size = kwargs.get("template_window_size", 7)
            search_window_size = kwargs.get("search_window_size", 21)
            return cv2.fastNlMeansDenoising(
                image, None, h, template_window_size, search_window_size
            )

        else:
            raise ValueError(f"Неизвестный метод денойзинга: {method}")

    def _sharpen_image(
        self, image: np.ndarray, strength: float = 1.0, **kwargs
    ) -> np.ndarray:
        """
        Увеличение резкости изображения.

        Args:
            image: Входное изображение
            strength: Сила увеличения резкости (1.0 = стандартная)
            **kwargs: Дополнительные параметры

        Returns:
            Увеличенное в резкости изображение
        """
        # Создаем ядро для увеличения резкости
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) * strength

        # Применяем фильтр
        if len(image.shape) == 3:
            sharpened = cv2.filter2D(image, -1, kernel)
        else:
            sharpened = cv2.filter2D(image, -1, kernel)

        # Ограничиваем значения пикселей
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    def _enhance_contrast(
        self, image: np.ndarray, alpha: float = 1.5, beta: int = 0, **kwargs
    ) -> np.ndarray:
        """
        Улучшение контраста изображения.

        Args:
            image: Входное изображение
            alpha: Коэффициент контраста (>1 увеличивает, <1 уменьшает)
            beta: Яркость (положительное значение увеличивает яркость)
            **kwargs: Дополнительные параметры

        Returns:
            Изображение с улучшенным контрастом
        """
        return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

    def _histogram_equalization(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Гистограммная эквализация для улучшения контраста.

        Args:
            image: Входное изображение
            **kwargs: Дополнительные параметры

        Returns:
            Изображение после гистограммной эквализации
        """
        if len(image.shape) == 3:
            # Для цветных изображений применяем к Y каналу в YUV
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
            return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            return cv2.equalizeHist(image)

    def _adaptive_histogram_eq(
        self,
        image: np.ndarray,
        clip_limit: float = 2.0,
        tile_grid_size: tuple = (8, 8),
        **kwargs,
    ) -> np.ndarray:
        """
        Адаптивная гистограммная эквализация (CLAHE).

        Args:
            image: Входное изображение
            clip_limit: Ограничение контраста
            tile_grid_size: Размер тайлов для локальной эквализации
            **kwargs: Дополнительные параметры

        Returns:
            Изображение после адаптивной гистограммной эквализации
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

        if len(image.shape) == 3:
            # Применяем к L каналу в LAB
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            lab[:, :, 0] = clahe.apply(lab[:, :, 0])
            return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            return clahe.apply(image)

    def _unsharp_mask(
        self,
        image: np.ndarray,
        kernel_size: tuple = (5, 5),
        sigma: float = 1.0,
        amount: float = 1.0,
        threshold: int = 0,
        **kwargs,
    ) -> np.ndarray:
        """
        Увеличение резкости методом нерезкой маски.

        Args:
            image: Входное изображение
            kernel_size: Размер ядра для размытия
            sigma: Стандартное отклонение для Gaussian blur
            amount: Количество резкости (1.0 = стандартное)
            threshold: Пороговое значение для применения резкости
            **kwargs: Дополнительные параметры

        Returns:
            Изображение с увеличенной резкостью
        """
        # Создаем размытую версию
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)

        # Вычисляем нерезкую маску
        mask = cv2.subtract(image, blurred)

        # Применяем маску с заданной силой
        sharpened = cv2.addWeighted(image, 1.0, mask, amount, 0)

        # Применяем пороговое значение
        if threshold > 0:
            low_contrast_mask = np.absolute(mask) < threshold
            np.copyto(sharpened, image, where=low_contrast_mask)

        return sharpened

    def _bilateral_filter(
        self,
        image: np.ndarray,
        d: int = 9,
        sigma_color: float = 75,
        sigma_space: float = 75,
        **kwargs,
    ) -> np.ndarray:
        """
        Бilateral фильтр для сохранения границ при удалении шума.

        Args:
            image: Входное изображение
            d: Диаметр окрестности пикселя
            sigma_color: Фильтрация в цветовом пространстве
            sigma_space: Фильтрация в пространственном пространстве
            **kwargs: Дополнительные параметры

        Returns:
            Отфильтрованное изображение
        """
        return cv2.bilateralFilter(image, d, sigma_color, sigma_space)

    def _gaussian_blur(
        self, image: np.ndarray, kernel_size: tuple = (5, 5), sigma: float = 0, **kwargs
    ) -> np.ndarray:
        """
        Gaussian размытие.

        Args:
            image: Входное изображение
            kernel_size: Размер ядра
            sigma: Стандартное отклонение
            **kwargs: Дополнительные параметры

        Returns:
            Размытое изображение
        """
        return cv2.GaussianBlur(image, kernel_size, sigma)

    def _median_filter(
        self, image: np.ndarray, kernel_size: int = 5, **kwargs
    ) -> np.ndarray:
        """
        Медианный фильтр для удаления соли и перца.

        Args:
            image: Входное изображение
            kernel_size: Размер ядра
            **kwargs: Дополнительные параметры

        Returns:
            Отфильтрованное изображение
        """
        return cv2.medianBlur(image, kernel_size)

    def _nlm_denoise(
        self,
        image: np.ndarray,
        h: float = 10,
        template_window_size: int = 7,
        search_window_size: int = 21,
        **kwargs,
    ) -> np.ndarray:
        """
        Non-local means денойзинг.

        Args:
            image: Входное изображение
            h: Параметр фильтрации
            template_window_size: Размер окна шаблона
            search_window_size: Размер окна поиска
            **kwargs: Дополнительные параметры

        Returns:
            Денойзированное изображение
        """
        return cv2.fastNlMeansDenoising(
            image, None, h, template_window_size, search_window_size
        )

    def _gamma_correction(
        self, image: np.ndarray, gamma: float = 1.0, **kwargs
    ) -> np.ndarray:
        """
        Гамма коррекция для изменения яркости.

        Args:
            image: Входное изображение
            gamma: Значение гаммы (<1 осветляет, >1 затемняет)
            **kwargs: Дополнительные параметры

        Returns:
            Изображение после гамма коррекции
        """
        # Создаем таблицу поиска
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(
            "uint8"
        )

        # Применяем гамма коррекцию
        return cv2.LUT(image, table)

    def _log_transform(self, image: np.ndarray, c: float = 1.0, **kwargs) -> np.ndarray:
        """
        Логарифмическое преобразование для улучшения темных областей.

        Args:
            image: Входное изображение
            c: Константа масштабирования
            **kwargs: Дополнительные параметры

        Returns:
            Преобразованное изображение
        """
        # Нормализуем изображение
        normalized = image.astype(np.float32) / 255.0

        # Применяем логарифмическое преобразование
        log_transformed = c * np.log(1 + normalized)

        # Масштабируем обратно
        return (log_transformed * 255).astype(np.uint8)

    def _power_transform(
        self, image: np.ndarray, gamma: float = 0.5, **kwargs
    ) -> np.ndarray:
        """
        Степенное преобразование (power law transform).

        Args:
            image: Входное изображение
            gamma: Показатель степени
            **kwargs: Дополнительные параметры

        Returns:
            Преобразованное изображение
        """
        # Нормализуем изображение
        normalized = image.astype(np.float32) / 255.0

        # Применяем степенное преобразование
        power_transformed = np.power(normalized, gamma)

        # Масштабируем обратно
        return (power_transformed * 255).astype(np.uint8)
