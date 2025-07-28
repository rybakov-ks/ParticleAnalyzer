import os
import gradio as gr
from particleanalyzer.core.ParticleAnalyzer import ParticleAnalyzer
from particleanalyzer.core.utils import (
    scale_input_visibility,
    segment_mode_visibility,
    sahi_mode_visibility,
    select_section,
    reset_interface,
    reset_interface2,
    log_analytics,
    empty_df_ParticleCharacteristics,
    empty_df_ParticleStatistics,
    save_data_to_csv,
    scale_input_unit_measurement,
    toggleTheme,
    translate_chatbot,
)
from particleanalyzer.core.about import about_ru
from particleanalyzer.core.parameter_information import reference_ru
from particleanalyzer.core.ui_styles import css, custom_head
from particleanalyzer.core.languages import i18n
from particleanalyzer.core.LLMAnalysis import LLMAnalysis
from .YOLOLoader import YOLOLoader

try:
    import detectron2  # noqa: F401
    from .Detectron2Loader import Detectron2Loader

    DETECTRON2_AVAILABLE = True
except ImportError:
    DETECTRON2_AVAILABLE = False


def get_available_models():
    yolo_models = list(YOLOLoader.MODEL_MAPPING.keys())
    if not DETECTRON2_AVAILABLE:
        return yolo_models
    return yolo_models + list(Detectron2Loader.MODEL_MAPPING.keys())


def assets_path(name: str):
    return os.path.join(os.path.dirname(__file__), "..", "assets", name)


analyzer = ParticleAnalyzer()

my_theme = gr.Theme.load(f"{assets_path('')}/themes/theme_schema@0.0.1.json").set(
    checkbox_label_background_fill='#2196f3',
    checkbox_label_background_fill_dark='#2196f3',
    input_background_fill_focus='f1f5f9',
    input_background_fill_focus_dark='334155',
)


def create_interface(api_key):
    llm_amalysis = LLMAnalysis(api_key)

    demo = gr.Blocks(
        theme=my_theme,
        title="ParticleAnalyzer — SEM Image Analysis Tool",
        head=custom_head,
        css=css,
        analytics_enabled=False,
    )

    with demo:
        api_key = gr.State(True if api_key else False)
        with gr.Column(elem_id="app-container"):
            with gr.Row(equal_height=True, elem_id="gr-head"):
                gr.HTML(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: inline-block; margin-right: 20px;">
                            <svg width="250" height="55" viewBox="0 0 250 55" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                                <image x="2" y="4" width="46" height="46" preserveAspectRatio="xMidYMid meet"
                                       xlink:href="https://rybakov-k.ru/assets/icon/305079-2196f3.svg"/>
                                <g font-family="'Segoe UI', 'Helvetica Neue', Arial, sans-serif" text-rendering="optimizeLegibility">
                                    <text x="55" y="29" font-size="22" font-weight="600" letter-spacing="-0.3">
                                        <tspan fill="#3b82f6">ParticleAnalyzer</tspan>
                                    </text>
                                    <text x="56" y="44" font-size="11" fill="#64748b" font-weight="500">
                                        SEM Image Analysis Tool
                                    </text>
                                </g>
                                <line x1="49" y1="4" x2="49" y2="54" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="3,2"/>
                            </svg>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <button onclick="startIntro()" style="
                                background: #4285f4;
                                color: white;
                                border: none;
                                border-radius: 20px;
                                padding: 7px 16px 7px 12px;
                                cursor: pointer;
                                font-size: 14px;
                                font-weight: 500;
                                display: flex;
                                align-items: center;
                                gap: 8px;
                                transition: all 0.3s;
                                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                                position: relative;
                                top: 3px;
                            " onmouseover="this.style.background='#3367d6'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.2)'" 
                             onmouseout="this.style.background='#4285f4'; this.style.boxShadow='0 2px 5px rgba(0,0,0,0.1)'">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 1px;">
                                    <circle cx="12" cy="12" r="10" fill="white"/>
                                    <circle cx="12" cy="9" r="3" fill="#4285f4"/>
                                    <path d="M12 12C15.5 12 18 14 18 16V18H6V16C6 14 8.5 12 12 12Z" fill="#4285f4"/>
                                </svg>
                                {i18n('Помощь')}
                            </button>
                            <i class="fas fa-sun" style="font-size: 18px;"></i>
                            <label class="switch">
                                <input type="checkbox" id="darkModeToggle">
                                <span class="slider"></span>
                            </label>
                            <i class="fas fa-moon" style="font-size: 18px;"></i>
                        </div>
                    </div>
                    """
                )
                demo.load(None, None, js=toggleTheme)
            with gr.Tabs(elem_id="tabs"):
                with gr.Tab(i18n("Анализ")):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row():
                                scale_selector = gr.Dropdown(
                                    list(analyzer.SCALE_OPTIONS.keys()),
                                    value=list(analyzer.SCALE_OPTIONS.keys())[0],
                                    label=i18n("Режим масштабирования"),
                                    elem_id="scale-selector",
                                )
                            with gr.Row(
                                visible=False, variant="default"
                            ) as row_instruction:
                                with gr.Accordion(
                                    i18n("Как задать масштаб?"), open=False
                                ):
                                    gr.HTML(
                                        """
                                        <img src="https://rybakov-k.ru/images/instruction.gif" alt="Instructions for setting the scale">
                                    """
                                    )
                            with gr.Row(equal_height=True, elem_id="analyze-row"):
                                with gr.Column(visible=False) as Paint_row:
                                    im = gr.Paint(
                                        label=i18n("Изображение СЭМ"),
                                        type="numpy",
                                        canvas_size=(600, 600),
                                        sources=["upload"],
                                        brush=gr.Brush(
                                            color_mode="fixed",
                                            default_color="green",
                                            colors=["green"],
                                        ),
                                        transforms="crop",
                                        layers=False,
                                        eraser=gr.Eraser(default_size=200),
                                        elem_id="in-image-paint",
                                    )
                                with gr.Column() as Image_row:
                                    in_image = gr.Image(
                                        sources=["upload"],
                                        label=i18n("Изображение СЭМ"),
                                        elem_id="in-image",
                                    )

                                with gr.Column():
                                    output_image = gr.Image(
                                        label=i18n("Результат сегментации"),
                                        elem_id="output-image",
                                    )
                                with gr.Row(visible=False) as AnnotatedImage_row:
                                    output_image2 = gr.AnnotatedImage(
                                        label=i18n("Результат сегментации")
                                    )
                                with gr.Row(visible=False) as output_table_image2_row:
                                    output_table_image2 = gr.Dataframe(
                                        value=empty_df_ParticleCharacteristics,
                                        label=i18n("Характеристики частицы"),
                                        interactive=False,
                                        elem_id="dataframe-table",
                                    )

                                with gr.Row(visible=False) as scale_input_row:
                                    scale_input = gr.Number(
                                        label="Длина шкалы в мкм",
                                        value=1.0,
                                        elem_id="scale-input",
                                    )

                    with gr.Row(elem_id="button-row"):
                        with gr.Column():
                            process_button = gr.HTML(
                                f"""
                            <button class="custom-btn btn-analyze" id="process-button" onclick="analyze()">
                                <img src='https://rybakov-k.ru/assets/icon/icons8-химия-50.png' 
                                     alt='Chemistry icon'/> 
                                {i18n('Анализировать')}
                            </button>
                            """
                            )
                        with gr.Column():
                            clear_button = gr.HTML(
                                f"""
                            <button class="custom-btn btn-clear" id="clear-btn" onclick="clear()">
                                <img src='https://rybakov-k.ru/assets/icon/icons8-метла-50.png' 
                                     alt='Chemistry icon'/> 
                                {i18n('Очистить')}
                            </button>
                            """
                            )

                    with gr.Row(elem_id="example-row") as in_image_example_row:
                        gr.Examples(
                            examples=[
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/100%20r-.jpg",
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/Tv30_1.png",
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/A02-1.bmp",
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/Rec-Cu-Ni-Powder_250x_5_SE_V1_png.jpg",
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/Resolution%20in%20SEM%201.jpg",
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/left_half.jpg",
                            ],
                            inputs=in_image,
                            label=i18n("Примеры"),
                            elem_id="examples_images",
                        )
                    with gr.Row(visible=False, min_height=650) as results_row:
                        with gr.Column():
                            gr.HTML(
                                f"""
                                    <div style="text-align: center;">
                                        <h2>{i18n("Результаты сегментации частиц")}</h2>
                                    </div>
                                    """
                            )
                            with gr.Tabs(elem_id="tabs_result") as tabs_row:
                                with gr.Tab(i18n("Статистика"), id=1):
                                    with gr.Row():
                                        output_table2 = gr.Dataframe(
                                            value=empty_df_ParticleStatistics,
                                            label=i18n("Статистика по частицам"),
                                            interactive=False,
                                            elem_id="dataframe-table2",
                                            show_copy_button=True,
                                        )
                                    with gr.Row():
                                        with gr.Accordion(
                                            i18n("Справочник параметров"), open=False
                                        ):
                                            gr.HTML(i18n(reference_ru))
                                    with gr.Row(visible=False):
                                        output_table = gr.Dataframe(
                                            value=empty_df_ParticleCharacteristics,
                                            label=i18n("Характеристики частиц"),
                                            interactive=False,
                                            elem_id="dataframe-table",
                                            show_search="filter",
                                            show_copy_button=True,
                                        )
                                with gr.Tab(i18n("Графики"), id=2):
                                    with gr.Row():
                                        output_plot = gr.Plot(
                                            label=i18n("Графики распределения")
                                        )
                                with gr.Tab(
                                    i18n("ИИ-анализ"), id=3, visible=False
                                ) as chatbot_row:
                                    with gr.Group():
                                        with gr.Column(scale=1):
                                            model_llm = gr.Dropdown(
                                                llm_amalysis.model_list,
                                                value=llm_amalysis.model_list[0],
                                                label=i18n("Языковая модель (LLM)"),
                                            )
                                            with gr.Row():
                                                chatbot = gr.Chatbot(
                                                    label=i18n(
                                                        "ИИ-интерпретация SEM-данных"
                                                    ),
                                                    height=600,
                                                    show_copy_all_button=True,
                                                    avatar_images=(
                                                        None,
                                                        f'{assets_path("")}/icon/ai.jpg',
                                                    ),
                                                    autoscroll=False,
                                                )
                                    with gr.Row(elem_classes="btn-group"):
                                        llm_run = gr.Button(
                                            value=i18n("Запустить ИИ-анализ"),
                                            variant="primary",
                                            size="md",
                                            icon=f'{assets_path("")}/icon/ai.png',
                                        )
                                        cancel_llm_button = gr.Button(
                                            value=i18n("Отменить"),
                                            size="md",
                                            variant="stop",
                                            icon=f'{assets_path("")}/icon/incorrect.png',
                                            elem_classes="custom-cancel-btn",
                                        )
                                with gr.Tab(i18n("Файлы"), id=4):
                                    with gr.Row():
                                        download_output = gr.Files(
                                            label=i18n("Файлы для скачивания")
                                        )
                                with gr.Tab(
                                    i18n("Оценить результаты"), id=5
                                ) as question_row:
                                    with gr.Row():
                                        gr.Markdown(
                                            i18n(
                                                "Вы удовлетворены качеством сегментации?"
                                            )
                                        )
                                    with gr.Row():
                                        with gr.Column(scale=1):
                                            yes_button = gr.Button(
                                                value=i18n("Да"),
                                                variant="secondary",
                                                size="sm",
                                                icon=f'{assets_path("")}/icon/like.png',
                                            )
                                        with gr.Column(scale=1):
                                            no_button = gr.Button(
                                                value=i18n("Нет"),
                                                variant="stop",
                                                size="sm",
                                                icon=f'{assets_path("")}/icon/dislike.png',
                                            )
                with gr.Tab(i18n("Настройки"), elem_id="setting"):
                    with gr.Group(elem_id="model-setting"):
                        with gr.Row():
                            model_change = gr.Dropdown(
                                get_available_models(),
                                value=get_available_models()[0],
                                label=i18n("Модель обнаружения"),
                            )
                        with gr.Row():
                            confidence_threshold = gr.Slider(
                                minimum=0.0,
                                maximum=1.0,
                                value=0.5,
                                step=0.01,
                                label=i18n("Точность обнаружения"),
                            )
                            confidence_iou = gr.Slider(
                                minimum=0.0,
                                maximum=1.0,
                                value=0.7,
                                step=0.01,
                                label=i18n("Порог перекрытия (IoU)"),
                            )
                    with gr.Group(elem_id="sahi-setting"):
                        with gr.Row():
                            sahi_mode = gr.Checkbox(
                                label=i18n("Включить"),
                                info=i18n(
                                    "Включить обработку с разбиением на фрагменты (SAHI)?"
                                ),
                            )
                        with gr.Row(visible=False) as slice_row:
                            slice_height = gr.Number(
                                value=400, label=i18n("Высота слайса")
                            )
                            slice_width = gr.Number(
                                value=400, label=i18n("Ширина слайса")
                            )
                        with gr.Row(visible=False) as slice_row2:
                            overlap_height_ratio = gr.Slider(
                                minimum=0.0,
                                maximum=1.0,
                                value=0.2,
                                step=0.01,
                                label=i18n("Перекрытие по высоте"),
                            )
                            overlap_width_ratio = gr.Slider(
                                minimum=0.0,
                                maximum=1.0,
                                value=0.2,
                                step=0.01,
                                label=i18n("Перекрытие по ширине"),
                            )
                    with gr.Row(
                        equal_height=True, elem_id="solution-segment-mode-setting"
                    ) as solution_and_segment_mode_row:
                        with gr.Column():
                            solution = gr.Radio(
                                ("Original", "640x640", "1024x1024"),
                                value="1024x1024",
                                label=i18n("Разрешение изображения"),
                            )
                        with gr.Column():
                            segment_mode = gr.Checkbox(
                                label=i18n("Включить"),
                                info=i18n("Включить режим анализа отдельных частиц?"),
                            )
                    with gr.Row() as number_detections_row:
                        number_detections = gr.Slider(
                            minimum=1,
                            maximum=10000,
                            value=1000,
                            step=100,
                            label=i18n("Максимальное количество обнаружений"),
                            elem_id="number-detections",
                        )
                    with gr.Row(visible=False):
                        round_value = gr.Dropdown(
                            [0, 1, 2, 3, 4, 5, 6],
                            value=4,
                            label=i18n("Округлять результаты до"),
                        )
                    with gr.Row(equal_height=True, elem_id="bins-feret-diametr"):
                        with gr.Column(scale=1):
                            number_of_bins = gr.Slider(
                                minimum=0.0,
                                maximum=100,
                                value=20,
                                step=1,
                                label=i18n("Интервалов на гистограмме"),
                            )
                        with gr.Column(scale=1):
                            show_Feret_diametr = gr.Checkbox(
                                label=i18n("Включить"),
                                info=i18n("Включить отображение диаметров Ферета?"),
                            )
                with gr.Tab(i18n("О программе")):
                    gr.HTML(i18n(about_ru))

            analyze = process_button.click(
                fn=analyzer.analyze_image,
                inputs=[
                    im,
                    in_image,
                    scale_input,
                    confidence_threshold,
                    scale_selector,
                    confidence_iou,
                    number_detections,
                    solution,
                    model_change,
                    round_value,
                    slice_height,
                    slice_width,
                    overlap_height_ratio,
                    overlap_width_ratio,
                    sahi_mode,
                    number_of_bins,
                    segment_mode,
                    show_Feret_diametr,
                    api_key,
                ],
                outputs=[
                    output_image,
                    output_table,
                    output_plot,
                    output_table2,
                    output_image2,
                    AnnotatedImage_row,
                    chatbot_row,
                    results_row,
                ],
                show_progress_on=output_image,
            )

            process_button.click(translate_chatbot, None, chatbot)

            llm_start = llm_run.click(
                fn=llm_amalysis.analyze,
                inputs=[output_table, model_llm],
                outputs=[chatbot],
            )
            cancel_llm_button.click(None, None, None, cancels=[llm_start])

            scale_selector.change(
                scale_input_visibility,
                inputs=scale_selector,
                outputs=[
                    scale_input_row,
                    Paint_row,
                    Image_row,
                    output_table,
                    in_image_example_row,
                    output_table_image2,
                    row_instruction,
                ],
                show_progress="hide",
                show_progress_on=scale_input_row,
            )

            segment_mode.change(
                segment_mode_visibility,
                inputs=segment_mode,
                outputs=[AnnotatedImage_row, output_table_image2_row],
            )

            sahi_mode.change(
                sahi_mode_visibility,
                inputs=sahi_mode,
                outputs=[
                    slice_row,
                    slice_row2,
                    number_detections_row,
                    solution_and_segment_mode_row,
                    segment_mode,
                ],
                show_progress="hide",
                show_progress_on=slice_row,
            )

            output_image2.select(
                select_section,
                inputs=output_table,
                outputs=[output_table_image2, output_table_image2_row],
            )

            clear_button.click(
                fn=reset_interface,
                inputs=[scale_selector],
                outputs=[
                    im,
                    output_image,
                    output_plot,
                    in_image,
                    output_image2,
                    AnnotatedImage_row,
                    output_table_image2_row,
                    chatbot,
                    results_row,
                ],
                cancels=[analyze],
                show_progress="hide",
                show_progress_on=question_row,
            )

            in_image.clear(
                fn=reset_interface,
                inputs=[scale_selector],
                outputs=[
                    im,
                    output_image,
                    output_plot,
                    in_image,
                    output_image2,
                    AnnotatedImage_row,
                    output_table_image2_row,
                    chatbot,
                    results_row,
                ],
                cancels=[analyze],
                show_progress="hide",
                show_progress_on=question_row,
            )

            im.clear(
                fn=reset_interface,
                inputs=[scale_selector],
                outputs=[
                    im,
                    output_image,
                    output_plot,
                    in_image,
                    output_image2,
                    AnnotatedImage_row,
                    output_table_image2_row,
                    chatbot,
                    results_row,
                ],
                cancels=[analyze],
                show_progress="hide",
                show_progress_on=question_row,
            )

            scale_selector.change(
                fn=reset_interface2,
                inputs=[scale_selector],
                outputs=[
                    output_image,
                    output_plot,
                    in_image,
                    output_image2,
                    AnnotatedImage_row,
                    output_table_image2_row,
                    chatbot,
                    results_row,
                ],
                show_progress="hide",
                show_progress_on=question_row,
            )

            scale_selector.change(
                fn=scale_input_unit_measurement,
                inputs=[scale_selector],
                outputs=[scale_input],
                show_progress="hide",
                show_progress_on=question_row,
            )

            yes_button.click(
                fn=log_analytics,
                inputs=[
                    confidence_threshold,
                    confidence_iou,
                    model_change,
                    gr.State("yes"),
                ],
                outputs=[question_row, tabs_row],
            )

            no_button.click(
                fn=log_analytics,
                inputs=[
                    confidence_threshold,
                    confidence_iou,
                    model_change,
                    gr.State("no"),
                ],
                outputs=[question_row, tabs_row],
            )

            output_table.change(
                fn=save_data_to_csv,
                inputs=[output_table, output_table2],
                outputs=download_output,
            )

    return demo
