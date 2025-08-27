import numpy as np
import gradio as gr
from PIL import Image, ImageDraw, ImageFont
from particleanalyzer.core.languages import translations
from particleanalyzer.core.language_context import LanguageContext


class PointManager:
    def __init__(self, lang="ru"):
        self.points = []
        self.lang = lang

    def _get_translation(self, text):
        return translations.get(self.lang, {}).get(text, text)

    def add_point(self, point):
        if len(self.points) >= 2:
            self.points = [point]
        else:
            self.points.append(point)
        return self.points

    def clear_points(self):
        self.points = []
        return self.points

    def handle_select(self, scale_selector, evt: gr.SelectData):
        self.lang = LanguageContext.get_language()
        if scale_selector != "Pixels":
            self.add_point(evt.index)
            if len(self.points) == 2:
                point1, point2 = self.points[0], self.points[1]
                distance = np.sqrt(
                    (point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2
                )
                return (
                    f"{self._get_translation('Расстояние равно')}: {distance:.0f} {self._get_translation('пикселей')}",
                    distance,
                    (point1, point2),
                )
            else:
                return (
                    f"{self._get_translation('Выбрано точек')}: {len(self.points)}/2",
                    None,
                    None,
                )
        else:
            return gr.skip(), gr.skip(), gr.skip()

    def draw_scale_on_image(self, image, scale_factor, distance, point1, point2):
        pil_image = Image.fromarray(image)
        draw = ImageDraw.Draw(pil_image)

        scaled_line_width = max(1, int(3))
        scaled_font_size = max(10, int(20))
        scaled_circle_radius = max(2, int(5))
        scaled_padding = max(2, int(5))

        LINE_COLOR = (255, 0, 0)
        TEXT_COLOR = (255, 255, 255)
        BG_COLOR = (0, 0, 0)

        try:
            font = ImageFont.truetype("arial.ttf", scaled_font_size)
        except IOError:
            font = ImageFont.load_default()

        scaled_point1 = (int(point1[0] / scale_factor), int(point1[1] / scale_factor))
        scaled_point2 = (int(point2[0] / scale_factor), int(point2[1] / scale_factor))

        draw.line(
            [scaled_point1, scaled_point2], fill=LINE_COLOR, width=scaled_line_width
        )

        def draw_circle(center, radius):
            x, y = center
            draw.ellipse(
                [x - radius, y - radius, x + radius, y + radius], fill=LINE_COLOR
            )

        draw_circle(scaled_point1, scaled_circle_radius)
        draw_circle(scaled_point2, scaled_circle_radius)

        mid_x = (scaled_point1[0] + scaled_point2[0]) // 2
        mid_y = (scaled_point1[1] + scaled_point2[1]) // 2

        text = f"{distance:.0f} px"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

        bg_x1 = mid_x - text_width // 2 - scaled_padding
        bg_y1 = mid_y - text_height // 2 - scaled_padding
        bg_x2 = mid_x + text_width // 2 + scaled_padding
        bg_y2 = mid_y + text_height // 2 + scaled_padding

        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=BG_COLOR)
        draw.text(
            (bg_x1 + scaled_padding, bg_y1 + scaled_padding),
            text,
            fill=TEXT_COLOR,
            font=font,
        )

        return np.array(pil_image)
