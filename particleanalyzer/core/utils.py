import gradio as gr
import pandas as pd
import csv
import os
from datetime import datetime
from particleanalyzer.core.languages import translations
from particleanalyzer.core.language_context import LanguageContext
from particleanalyzer.core.ParticleAnalyzer import ParticleAnalyzer


def assets_path(name: str):
    return os.path.join(os.path.dirname(__file__), "..", "assets", name)


def determine_language(accept_language: str):
    """Определение языка на основе заголовка Accept-Language"""
    if not accept_language:
        return "en"

    lang_code = accept_language.split(",")[0].lower()

    language_mapping = {
        "en-us": "en",
        "en": "en",
        "ru": "ru",
        "zh-cn": "zh-cn",
        "zh-tw": "zh-tw",
    }

    return language_mapping.get(
        lang_code, language_mapping.get(lang_code.split("-")[0], "en")
    )


def get_translation(text):
    lang = LanguageContext.get_language()
    return translations.get(lang, {}).get(text, text)


def translate_chatbot():
    text_chatbot = get_translation(
        """🔬 **Добро пожаловать в систему анализа SEM-изображений!**
        Я – ваш виртуальный ассистент в сканирующей электронной микроскопии. Готов провести детальный анализ морфологии и размерных характеристик частиц."""
    )
    return gr.update(value=[[None, text_chatbot]])


def get_columns(scale_value):
    """Генерирует колонки DataFrame в зависимости от выбранного масштаба"""
    unit = get_translation(ParticleAnalyzer.SCALE_OPTIONS[scale_value]["unit"])
    columns = [
        "№",
        f"S [{unit}²]",
        f"P [{unit}]",
        f"D [{unit}]",
        f"Dₘₐₓ [{unit}]",
        f"Dₘᵢₙ' [{unit}]",
        f"Dₘₑₐₙ [{unit}]",
        "'θₘₐₓ' [°]",
        "'θₘᵢₙ' [°]",
        "e",
        f"I [{get_translation('ед.')}]" f"{get_translation('Количество частиц')}",
    ]
    return pd.DataFrame(columns=columns)


def get_stats_columns():
    """Возвращает колонки для таблицы статистики"""
    columns = [
        get_translation("Параметр"),
        get_translation("Среднее"),
        get_translation("Медиана"),
        get_translation("Максимум"),
        get_translation("Минимум"),
        get_translation("СО"),
    ]
    return pd.DataFrame(columns=columns)


def scale_input_visibility(scale_value):
    """Показываем масштабную шкалу"""
    is_scaled = ParticleAnalyzer.SCALE_OPTIONS[scale_value]["scale"]
    return (
        gr.update(visible=(is_scaled)),
        gr.update(visible=(is_scaled)),
        gr.update(visible=(not is_scaled)),
        gr.update(value=(get_columns(scale_value))),
        gr.update(visible=(not is_scaled)),
        gr.update(value=(get_columns(scale_value))),
        gr.update(visible=(is_scaled)),
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
        return empty_df_ParticleCharacteristics, gr.update(visible=False)


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
        None,  # Очищаем output_image
        None,  # Очищаем графики
        None,  # Очищаем input_image
        None,  # Очищаем output_image2
        gr.update(visible=False),  # Скрываем строку AnnotatedImage_row
        gr.update(visible=False),  # Скрываем строку output_table_image2_row
        [(None, None)],  # Очищаем chatbot
        gr.update(visible=False),  # Скрываем строку results_row
    )


def reset_interface2(scale_value):
    """Функция для сброса интерфейса"""
    return (
        None,  # Очищаем output_image
        None,  # Очищаем графики
        None,  # Очищаем input_image
        None,  # Очищаем output_image2
        gr.update(visible=False),  # Скрываем строку AnnotatedImage_row
        gr.update(visible=False),  # Скрываем строку output_table_image2_row
        [(None, None)],  # Очищаем chatbot
        gr.update(visible=False),  # Скрываем строку results_row
    )


def scale_input_unit_measurement(scale_selector, request: gr.Request):
    """Установка лейбла для длины шкалы прибора"""
    lang = determine_language(request.headers.get("Accept-Language", ""))
    LanguageContext.set_language(lang)
    unit = ParticleAnalyzer.SCALE_OPTIONS[scale_selector]["unit"]
    label = get_translation(f"Длина шкалы в {unit}")
    return gr.update(label=label)


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

    return gr.update(visible=False), gr.update(selected=1)


def chatbot_visibility():
    return gr.update(visible=True)


empty_df_ParticleCharacteristics = get_columns("Pixels").fillna("")
empty_df_ParticleStatistics = get_stats_columns()

toggleTheme = """
() => {
    function toggleTheme() {
        const isDark = document.body.classList.toggle('dark');
        localStorage.setItem('gradioDarkMode', isDark);
    }

    function getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;

    const savedTheme = localStorage.getItem('gradioDarkMode');
    const systemTheme = getSystemTheme();

    const isDark = savedTheme !== null 
        ? savedTheme === 'true' 
        : systemTheme === 'dark';

    if (isDark) {
        document.body.classList.add('dark');
        toggle.checked = true;
    } else {
        document.body.classList.remove('dark');
        toggle.checked = false;
    }

    toggle.addEventListener('change', toggleTheme);

    if (savedTheme === null) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        const handleSystemThemeChange = (e) => {
            if (e.matches) {
                document.body.classList.add('dark');
                toggle.checked = true;
            } else {
                document.body.classList.remove('dark');
                toggle.checked = false;
            }
        };

        handleSystemThemeChange(mediaQuery);

        mediaQuery.addEventListener('change', handleSystemThemeChange);
    }
}

"""
