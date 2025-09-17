import gradio as gr
import pandas as pd
import numpy as np
import cv2
from PIL import Image
import csv
import io
import os
from datetime import datetime
from particleanalyzer.core.languages import translations
from particleanalyzer.core.language_context import LanguageContext
from particleanalyzer.core.ParticleAnalyzer import ParticleAnalyzer
from particleanalyzer.core.StatisticsBuilder import StatisticsBuilder
from particleanalyzer.core.ImagePreprocessor import ImagePreprocessor


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
        gr.update(value=(get_columns(scale_value))),
        gr.update(value=(get_columns(scale_value))),
        gr.update(visible=(is_scaled)),
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
    )


def reset_interface():
    """Функция для сброса интерфейса"""
    global selected_particles
    selected_particles = []
    return (
        None,  # Очищаем output_image
        None,  # Очищаем графики
        None,  # Очищаем vector_field
        None,  # Очищаем input_image
        gr.update(visible=False),  # Скрываем строку output_table_image2_row
        gr.update(visible=False),  # Скрываем строку reset_delete_buttons_row
        [(None, None)],  # Очищаем chatbot
        gr.update(visible=False),  # Скрываем строку results_row
        gr.update(visible=False),  # Скрываем sidebar
        gr.update(visible=True),  # Показываем строку row_image_file
        gr.update(visible=False),  # Скрываем строку row_analysis
        None,  # Очищаем image_file
        get_translation(
            "Выберите две крайние точки на шкале"
        ),  # Очищаем scale_input_status
        None,  # Очищаем scale
        gr.update(visible=False),  # Скрываем output_image_row
    )


def reset_interface2():
    """Функция для сброса интерфейса"""
    global selected_particles
    selected_particles = []
    return (
        None,  # Очищаем output_image
        None,  # Очищаем графики
        None,  # Очищаем vector_field
        gr.update(visible=False),  # Скрываем строку output_table_image2_row
        gr.update(visible=False),  # Скрываем строку reset_delete_buttons_row
        [(None, None)],  # Очищаем chatbot
        gr.update(visible=False),  # Скрываем строку results_row
        gr.update(visible=False),  # Скрываем sidebar
        gr.update(visible=False),  # Скрываем output_image_row
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


def statistic_an(
    df: pd.DataFrame,
    points_df: pd.DataFrame,
    scale_selector: int,
    round_value: int,
    number_of_bins: int,
    d_max_slider,
    d_min_slider,
    theta_max_slider,
    theta_min_slider,
    e_slider,
    S_slider,
    P_slider,
    I_slider,
    image2: np.ndarray,
    solution,
    sahi_mode,
    outline_color,
    show_fillPoly,
    show_polylines,
    fill_type_color,
    fill_color,
    fill_alpha,
):

    lang = LanguageContext.get_language()
    scale_config = ParticleAnalyzer.SCALE_OPTIONS[scale_selector]
    selected_image = image2
    selected_image = cv2.cvtColor(selected_image, cv2.COLOR_RGB2BGR)
    selected_image, scale_factor_glob = ImagePreprocessor.resize_image(
        selected_image, solution, sahi_mode
    )

    d_max_min, d_max_max = d_max_slider
    d_min_min, d_min_max = d_min_slider
    theta_max_min, theta_max_max = theta_max_slider
    theta_min_min, theta_min_max = theta_min_slider
    e_min, e_max = e_slider
    S_min, S_max = S_slider
    P_min, P_max = P_slider
    I_min, I_max = I_slider

    filtered_df = df[
        (df.iloc[:, 2] >= d_max_min)
        & (df.iloc[:, 2] <= d_max_max)
        & (df.iloc[:, 3] >= d_min_min)
        & (df.iloc[:, 3] <= d_min_max)
        & (df.iloc[:, 5] >= theta_max_min)
        & (df.iloc[:, 5] <= theta_max_max)
        & (df.iloc[:, 6] >= theta_min_min)
        & (df.iloc[:, 6] <= theta_min_max)
        & (df.iloc[:, 9] >= e_min)
        & (df.iloc[:, 9] <= e_max)
        & (df.iloc[:, 7] >= S_min)
        & (df.iloc[:, 7] <= S_max)
        & (df.iloc[:, 8] >= P_min)
        & (df.iloc[:, 8] <= P_max)
        & (df.iloc[:, 10] >= I_min)
        & (df.iloc[:, 10] <= I_max)
    ].copy()

    filtered_points_df = points_df.loc[filtered_df.index].copy()

    builder = StatisticsBuilder(
        filtered_df,
        scale_config,
        round_value=round_value,
        number_of_bins=number_of_bins,
        lang=lang,
    )
    stats_df = builder.build_stats_table()
    fig, vector_fig = builder.build_distribution_fig(selected_image)

    thickness = ParticleAnalyzer._get_scaled_thickness(
        selected_image.shape[1], selected_image.shape[0]
    )

    points_arrays = [
        np.array(p, dtype=np.int32).reshape((-1, 1, 2))
        for p in filtered_points_df.iloc[:, -1]
        if p and len(p) > 0
    ]

    if points_arrays:
        if show_fillPoly:
            overlay = selected_image.copy()
            for contour in points_arrays:
                cv2.fillPoly(
                    overlay,
                    [contour],
                    (
                        ParticleAnalyzer.get_random_color()
                        if fill_type_color == "Random"
                        else ParticleAnalyzer.rgba_to_bgr(fill_color)
                    ),
                )
            alpha = fill_alpha
            cv2.addWeighted(
                overlay, alpha, selected_image, 1 - alpha, 0, selected_image
            )
        if show_polylines:
            cv2.polylines(
                selected_image,
                points_arrays,
                isClosed=True,
                color=ParticleAnalyzer.rgba_to_bgr(outline_color),
                thickness=thickness,
            )
    selected_image = cv2.cvtColor(selected_image, cv2.COLOR_BGR2RGB)

    return (
        selected_image,
        stats_df,
        fig,
        vector_fig,
    )


selected_particles = []  # Глобальный список для хранения выбранных частиц


def select_particle_from_image(points_df, output_table, evt: gr.SelectData):
    global selected_particles
    target_point = (evt.index[0], evt.index[1])

    matching_contours = []
    already_selected = False

    for selected_idx in selected_particles:
        contour_points = points_df.loc[selected_idx, "points"]
        if contour_points and len(contour_points) >= 3:
            contour = np.array(contour_points, dtype=np.int32).reshape((-1, 1, 2))
            if cv2.pointPolygonTest(contour, target_point, measureDist=False) >= 0:
                already_selected = True
                break

    if already_selected:
        return gr.skip(), gr.skip(), gr.skip()

    for idx, contour_points in points_df["points"].items():
        if not contour_points or len(contour_points) < 3:
            continue

        contour = np.array(contour_points, dtype=np.int32).reshape((-1, 1, 2))
        distance = cv2.pointPolygonTest(contour, target_point, measureDist=False)

        if distance >= 0 and idx not in selected_particles:
            matching_contours.append(idx)

    if not matching_contours:
        return gr.skip(), gr.skip(), gr.skip()

    if len(matching_contours) > 1:
        matching_contours.sort(
            key=lambda x: cv2.contourArea(
                np.array(points_df.loc[x, "points"]).reshape((-1, 1, 2))
            )
        )
    selected_particles.append(matching_contours[0])

    return (
        output_table.iloc[selected_particles],
        gr.update(visible=True),
        gr.update(visible=True),
    )


def reset_selection(output_table_image2):
    global selected_particles
    selected_particles = []
    return (
        output_table_image2.iloc[[]],
        gr.update(visible=False),
        gr.update(visible=False),
    )


def particle_removal(
    output_table_image2, points_df, output_table, round_value, scale_selector
):
    global selected_particles
    if not output_table_image2.empty and "№" in output_table_image2.columns:
        try:
            numbers_to_remove = output_table_image2["№"].astype(int).tolist()

            rows_to_remove = output_table[output_table["№"].isin(numbers_to_remove)]

            if not rows_to_remove.empty:
                output_table = output_table.drop(rows_to_remove.index).reset_index(
                    drop=True
                )

                points_df = points_df.drop(rows_to_remove.index).reset_index(drop=True)
                selected_particles = []
        except (ValueError, KeyError) as e:
            print(f"Ошибка при удалении строк: {e}")
    limits = ParticleAnalyzer.calculate_limits(output_table, round_value)
    scale_selector = ParticleAnalyzer.SCALE_OPTIONS[scale_selector]
    return (
        gr.update(visible=False),
        gr.update(visible=False),
        points_df,
        output_table,
        gr.update(
            minimum=limits["d_max_min"],
            maximum=limits["d_max_max"],
            value=(limits["d_max_min"], limits["d_max_max"]),
            step=limits["d_max_max"] * 0.01,
            label=f"Dₘₐₓ [{get_translation(scale_selector['unit'])}]",
        ),
        gr.update(
            minimum=limits["d_min_min"],
            maximum=limits["d_min_max"],
            value=(limits["d_min_min"], limits["d_min_max"]),
            step=limits["d_min_max"] * 0.01,
            label=f"Dₘᵢₙ [{get_translation(scale_selector['unit'])}]",
        ),
        gr.update(
            minimum=limits["theta_max_min"],
            maximum=limits["theta_max_max"],
            value=(limits["theta_max_min"], limits["theta_max_max"]),
        ),
        gr.update(
            minimum=limits["theta_min_min"],
            maximum=limits["theta_min_max"],
            value=(limits["theta_min_min"], limits["theta_min_max"]),
        ),
        gr.update(minimum=0, maximum=1, value=(0, 1)),
        gr.update(
            minimum=limits["S_min"],
            maximum=limits["S_max"],
            value=(limits["S_min"], limits["S_max"]),
            step=limits["S_max"] * 0.01,
            label=f"S [{get_translation(scale_selector['unit'])}²]",
        ),
        gr.update(
            minimum=limits["P_min"],
            maximum=limits["P_max"],
            value=(limits["P_min"], limits["P_max"]),
            step=limits["P_max"] * 0.01,
            label=f"P [{get_translation(scale_selector['unit'])}]",
        ),
        gr.update(
            minimum=limits["I_min"],
            maximum=limits["I_max"],
            value=(limits["I_min"], limits["I_max"]),
        ),
    )


def img_to_numpy_array(file_path, max_size_kb=500, quality=85):
    try:
        with Image.open(file_path) as img:
            img_byte_arr = io.BytesIO()
            
            img.save(img_byte_arr, format="PNG", optimize=True)

            current_size_kb = len(img_byte_arr.getvalue()) / 1024

            if current_size_kb > max_size_kb:
                ratio = (max_size_kb / current_size_kb) ** 0.5
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format="PNG", optimize=True)

            img_byte_arr.seek(0)
            compressed_img = Image.open(img_byte_arr)

            return np.array(compressed_img)

    except (IOError, OSError, ValueError) as e:
        gr.Info(
            get_translation(
                "Не поддерживаемый формат изображения."
            )
        )
        print(f"Ошибка при загрузке изображения {file_path}: {e}")
        return None


def handle_file_upload(file, scale_selector):
    if file is None:
        return gr.skip(), gr.update(visible=True), gr.update(visible=False)

    in_image = img_to_numpy_array(file.name)

    return (
        in_image,
        gr.update(visible=False),
        gr.update(visible=True),
    )


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
