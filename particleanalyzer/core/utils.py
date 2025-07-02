import gradio as gr
import pandas as pd
import csv
import os
from datetime import datetime
from particleanalyzer.core.languages import translations
from particleanalyzer.core.language_context import LanguageContext
from particleanalyzer.core.languages import i18n


def assets_path(name: str):
    return os.path.join(base_path, "..", "assets", name)


def get_translation(text):
    lang = LanguageContext.get_language()
    return translations.get(lang, {}).get(text, text)


def scale_input_visibility(scale_value):
    """Показываем масштабную шкалу"""
    return (
        gr.update(visible=(scale_value == get_translation("Instrument scale in µm"))),
        gr.update(visible=(scale_value == get_translation("Instrument scale in µm"))),
        gr.update(visible=(scale_value == get_translation("Pixels"))),
        gr.update(
            value=(empty_df2 if scale_value == get_translation("Pixels") else empty_df1)
        ),
        gr.update(visible=(scale_value == get_translation("Pixels"))),
        gr.update(
            value=(
                empty_df2 if scale_value == get_translation("Pixels") else empty_df2_2
            )
        ),
    )


def segment_mode_visibility(segment_mode):
    """Режим анализа отдельных частиц"""
    return gr.update(visible=None if segment_mode else False), gr.update(
        visible=None if segment_mode else False
    )


def select_section(evt: gr.SelectData, output_table):
    """Режим анализа отдельных частиц. Возвращаем параметры частицы"""
    if 0 <= evt.index < len(output_table):
        return output_table.iloc[[evt.index]], gr.update(visible=True)
    else:
        return empty_df2, gr.update(visible=False)


def sahi_mode_visibility(sahi_mode):
    """Режим SAHI"""
    return (
        gr.update(visible=sahi_mode),
        gr.update(visible=sahi_mode),
        gr.update(visible=not sahi_mode),
        gr.update(visible=not sahi_mode),
        gr.update(value=False if sahi_mode else None),
    )


def reset_interface(scale_value):
    """Функция для сброса интерфейса"""
    return (
        {"background": None, "layers": [], "composite": None},  # Очищаем im
        None,                                    # Очищаем output_image
        pd.DataFrame(
            columns=[
                "№",
                get_translation("S [мкм²]"),     # Площадь в квадратных микрометрах
                get_translation("P [мкм]"),      # Периметр в микрометрах
                get_translation("D [мкм]"),      # Диаметр в микрометрах
                get_translation("Dₘₐₓ [мкм]"),   # Максимальны диаметр Ферета
                get_translation("Dₘᵢₙ  [мкм]"),  # Минимальный диаметр Ферета
                get_translation("Dₘₑₐₙ  [мкм]"), # Средний диаметр Ферета
                get_translation("θₘₐₓ [°]"),     # Угл ориентации для max диаметра
                get_translation("θₘᵢₙ [°]"),     # Угл ориентации для min диаметра
                "e",                             # Эксцентриситет (безразмерная величина)
                get_translation("I [ед.]"),      # Интенсивность в условных единицах
            ]
        ),
        pd.DataFrame(
            columns=[
                get_translation("Параметр"),  # Параметр
                get_translation("Среднее"),   # Среднее
                get_translation("Медиана"),   # Медиана
                get_translation("Максимум"),  # Максимум
                get_translation("Минимум"),   # Минимум
                get_translation("СО"),        # Стандартное отклонение
            ]
        ),
        None,  # Очищаем графики
        gr.update(visible=False),  # Скрываем таблицу
        gr.update(visible=False),  # Скрываем таблицу
        gr.update(visible=False),  # Скрываем графики
        None,                      # Очищаем input_image
        gr.update(visible=False),  # Скрываем таблицу
        None,                     # Очищаем output_image2
        (
            empty_df2 if scale_value == get_translation("Pixels") else empty_df2_2
        ),                         # Очищаем output_table_image2
        gr.update(visible=False),  # Скрываем таблицу
        gr.update(visible=False),  # Скрываем label
        gr.update(visible=False),  # Скрываем строку AnnotatedImage_row
        gr.update(visible=False),  # Скрываем строку output_table_image2_row
        [(None, None)],            # Очищаем строку chatbot_row
        gr.update(visible=False),  # Скрываем строку chatbot_row
    )


def save_data_to_csv(
    data_table: pd.DataFrame, data_table2: pd.DataFrame, output_dir: str = "output"
):
    """Сохраняет данные частиц в CSV файлы"""
    os.makedirs(output_dir, exist_ok=True)

    particle_path = os.path.join(output_dir, "particle_characteristics.csv")
    stats_path = os.path.join(output_dir, "particle_statistics.csv")

    data_table.to_csv(particle_path, index=False, encoding="utf-8-sig")
    data_table2.to_csv(stats_path, index=False, encoding="utf-8-sig")

    return [particle_path, stats_path]


def toggle_theme(current_mode: str):
    """Переключает между темной и светлой темой"""
    if (
        current_mode == get_translation("Тёмный режим")
        or current_mode.__class__.__name__ == "I18nData"
    ):
        return get_translation("Светлый режим"), gr.Button(
            value=i18n("Светлый режим"),
            icon=f'{assets_path("")}/icon/icons8-солнце-50.png',
        )
    return get_translation("Тёмный режим"), gr.Button(
        value=i18n("Тёмный режим"),
        icon=f'{assets_path("")}/icon/icons8-темный-режим-50.png',
    )


def log_analytics(
    confidence_threshold: float,
    confidence_iou: float,
    model_name: str,
    feedback: str,
    output_dir: str = "output",
):
    """Логирует аналитические данные о работе модели"""
    os.makedirs(output_dir, exist_ok=True)

    # Находим последний обработанный файл
    files = [
        f
        for f in os.listdir(output_dir)
        if not f.endswith(".csv") and os.path.isfile(os.path.join(output_dir, f))
    ]

    latest_file = (
        max(files, key=lambda x: os.path.getmtime(os.path.join(output_dir, x)))
        if files
        else "N/A"
    )

    analytic_path = os.path.join(output_dir, "analytics.csv")
    file_exists = os.path.isfile(analytic_path)

    with open(analytic_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                ["Timestamp", "Model", "Confidence", "IoU", "Feedback", "ProcessedFile"]
            )
        writer.writerow(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                model_name,
                confidence_threshold,
                confidence_iou,
                feedback,
                latest_file,
            ]
        )

    return gr.update(visible=False), gr.update(visible=False)
    
def chatbot_visibility():
    return gr.update(visible=True)

base_path = os.path.dirname(__file__)

empty_df1 = pd.DataFrame(
    columns=[
        "№",
        get_translation("S [мкм²]"),     # Площадь в квадратных микрометрах
        get_translation("P [мкм]"),      # Периметр в микрометрах
        get_translation("D [мкм]"),      # Диаметр в микрометрах
        get_translation("Dₘₐₓ [мкм]"),   # Максимальны диаметр Ферета
        get_translation("Dₘᵢₙ  [мкм]"),  # Минимальный диаметр Ферета
        get_translation("Dₘₑₐₙ  [мкм]"), # Средний диаметр Ферета
        get_translation("θₘₐₓ [°]"),     # Угл ориентации для max диаметра
        get_translation("θₘᵢₙ [°]"),     # Угл ориентации для min диаметра
        "e",                             # Эксцентриситет (безразмерная величина)
        get_translation("I [ед.]"),      # Интенсивность в условных единицах
    ]
)
empty_df2 = pd.DataFrame(
    columns=[
        "№",
        get_translation("S [пикс²]"),     # Площадь в квадратных пикселях
        get_translation("P [пикс]"),      # Периметр в пикселях
        get_translation("D [пикс]"),      # Диаметр в пикселях
        get_translation("Dₘₐₓ [пикс]"),   # Максимальны диаметр Ферета
        get_translation("Dₘᵢₙ  [пикс]"),  # Минимальный диаметр Ферета
        get_translation("Dₘₑₐₙ  [пикс]"), # Средний диаметр Ферета
        get_translation("θₘₐₓ [°]"),      # Угл ориентации для max диаметра
        get_translation("θₘᵢₙ [°]"),      # Угл ориентации для min диаметра
        "e",                              # Эксцентриситет (безразмерная величина)
        get_translation("I [ед.]"),       # Интенсивность в условных единицах
    ]
).fillna("")
empty_df2_2 = pd.DataFrame(
    columns=[
        "№",
        get_translation("S [мкм²]"),     # Площадь в квадратных микрометрах
        get_translation("P [мкм]"),      # Периметр в микрометрах
        get_translation("D [мкм]"),      # Диаметр в микрометрах
        get_translation("Dₘₐₓ [мкм]"),   # Максимальны диаметр Ферета
        get_translation("Dₘᵢₙ  [мкм]"),  # Минимальный диаметр Ферета
        get_translation("Dₘₑₐₙ  [мкм]"), # Средний диаметр Ферета
        get_translation("θₘₐₓ [°]"),     # Угл ориентации для max диаметра
        get_translation("θₘᵢₙ [°]"),     # Угл ориентации для min диаметра
        "e",                             # Эксцентриситет (безразмерная величина)
        get_translation("I [ед.]"),      # Интенсивность в условных единицах
    ]
).fillna("")
empty_df3 = pd.DataFrame(
    columns=[
        get_translation("Параметр"),  # Параметр
        get_translation("Среднее"),   # Среднее
        get_translation("Медиана"),   # Медиана
        get_translation("Максимум"),  # Максимум
        get_translation("Минимум"),   # Минимум
        get_translation("СО"),        # Стандартное отклонение
    ]
)
