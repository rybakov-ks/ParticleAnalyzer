import os
import gradio as gr
from particleanalyzer.core.ParticleAnalyzer import ParticleAnalyzer
from particleanalyzer.core.utils import (
    scale_input_visibility,
    segment_mode_visibility,
    sahi_mode_visibility,
    select_section,
    reset_interface,
    log_analytics,
    empty_df2,
    empty_df3,
    save_data_to_csv,
)
from particleanalyzer.core.ui_styles import css, custom_head
from particleanalyzer.core.languages import i18n
from particleanalyzer.core.LLMAnalysis import LLMAnalysis
from .YOLOLoader import YOLOLoader
try:
    import detectron2 # noqa: F401
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
    return os.path.join(base_path, "..", "assets", name)

base_path = os.path.dirname(__file__)
analyzer = ParticleAnalyzer()

def create_interface(api_key):
    llm_amalysis = LLMAnalysis(api_key)
    
    demo = gr.Blocks(
        theme="snehilsanyal/scikit-learn",
        title="ParticleAnalyzer — SEM Image Analysis Tool",
        head=custom_head,
        css=css,
        analytics_enabled=False,
    )

    with demo:
        api_key = gr.State(True if api_key else False)
        with gr.Column(elem_id="app-container"):
            gr.HTML(
                """
                <a href="https://github.com/rybakov-ks/ParticleAnalyzer" target="_blank" 
                   style="position: fixed; bottom: 20px; right: 20px;">
                   <img src="https://rybakov-k.ru/images/pngwing.com.png" 
                        width="60" height="60">
                </a>
            """
            )
            with gr.Group(elem_id="gr-head"):
                with gr.Row(equal_height=True):
                    gr.Markdown("# 🔎 ParticleAnalyzer v0.1.26")
                    gr.HTML(
                        """
                        <div style="display: flex; justify-content: flex-end;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <i class="fas fa-sun" style="font-size: 18px;"></i>
                                <label class="switch">
                                    <input type="checkbox" id="darkModeToggle">
                                    <span class="slider"></span>
                                </label>
                                <i class="fas fa-moon" style="font-size: 18px;"></i>
                            </div>
                        </div>
                    """)
                    demo.load(
                        None,
                        None,
                        js="""
                        () => {
                            function toggleTheme() {
                                document.body.classList.toggle('dark');
                                localStorage.setItem('gradioDarkMode', document.body.classList.contains('dark'));
                            }
                            
                            const toggle = document.getElementById('darkModeToggle');
                            if (toggle) {
                                toggle.addEventListener('change', toggleTheme);
                            }

                            const isDark = localStorage.getItem('gradioDarkMode') === 'true';
                            if (isDark) {
                                document.body.classList.add('dark');
                                if (toggle) toggle.checked = true;
                            }
                        }
                        """
                    )
                gr.Markdown(
                    i18n(
                        "При помощи данного инструмента можно анализировать размерные характеристики частиц на изображениях SEM.<br>В случае проблем с сегментацией изображения или возникновения ошибок, пожалуйста, направляйте материалы на электронную почту: rybakov-ks@ya.ru"
                    )
                )
            with gr.Tabs():
                with gr.Tab(i18n("Анализ")):
                    with gr.Row():
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
                            )
                        with gr.Column() as Image_row:
                            in_image = gr.Image(
                                sources=["upload"], label=i18n("Изображение СЭМ")
                            )

                        with gr.Column():
                            output_image = gr.Image(label=i18n("Результат сегментации"))

                    with gr.Row(visible=False) as AnnotatedImage_row:
                        output_image2 = gr.AnnotatedImage(
                            label=i18n("Результат сегментации")
                        )
                    with gr.Row(visible=False) as output_table_image2_row:
                        output_table_image2 = gr.Dataframe(
                            value=empty_df2,
                            label=i18n("Характеристики частицы"),
                            interactive=False,
                            elem_id="dataframe-table",
                        )
                    with gr.Row() as in_image_example_row:
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
                        )
                    with gr.Row(visible=False) as scale_input_row:
                        scale_input = gr.Number(
                            label=i18n("Instrument scale in µm"), value=1.0
                        )
                    with gr.Row():
                        process_button = gr.Button(
                            value=i18n("Анализировать"),
                            variant="primary",
                            size="md",
                            icon=f'{assets_path("")}/icon/icons8-химия-50.png',
                        )
                        clear_button = gr.Button(
                            value=i18n("Очистить"),
                            size="md",
                            icon=f'{assets_path("")}/icon/icons8-метла-50.png',
                        )

                    with gr.Row():
                        output_table2 = gr.Dataframe(
                            value=empty_df3,
                            label=i18n("Статистика по частицам"),
                            interactive=False,
                            visible=False,
                            elem_id="dataframe-table2",
                            show_copy_button=True,
                        )
                    with gr.Row(visible=False):
                        output_table = gr.Dataframe(
                            value=empty_df2,
                            label=i18n("Характеристики частиц"),
                            interactive=False,
                            visible=False,
                            elem_id="dataframe-table",
                            show_search="filter",
                            show_copy_button=True,
                        )
                    with gr.Row():
                        download_output = gr.Files(
                            label=i18n("Файлы для скачивания"), visible=False
                        )
                    with gr.Row():
                        output_plot = gr.Plot(
                            label=i18n("Графики распределения"), visible=False
                        )
                    with gr.Group(visible=False) as chatbot_row:
                        with gr.Column(scale=1):

                            model_llm = gr.Dropdown(
                                llm_amalysis.model_list,
                                value=llm_amalysis.model_list[0],
                                label=i18n("Языковая модель (LLM)"),
                            )
                            with gr.Row():
                                chatbot = gr.Chatbot(
                                    label=i18n("ИИ-интерпретация SEM-данных"),
                                    height=600,
                                    show_copy_all_button=True,
                                    avatar_images=(None, f'{assets_path("")}/icon/ai.jpg'),
                                    autoscroll=False,
                                )
                            llm_run = gr.Button(
                                value=i18n("Запустить ИИ-анализ"),
                                variant="primary",
                                size="md",
                                icon=f'{assets_path("")}/icon/ai.png',
                            )
                    with gr.Row(visible=False) as question_row:
                        gr.Markdown(i18n("Вы удовлетворены качеством сегментации?"))
                    with gr.Row(visible=False) as buttons_row:
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
                with gr.Tab(i18n("Настройки")):
                    with gr.Row():
                        scale_selector = gr.Radio(
                            ("Pixels", "Instrument scale in µm"),
                            value="Pixels",
                            label=i18n("Режим масштабирования"),
                        )
                    with gr.Group():
                        with gr.Row():
                            model_change = gr.Dropdown(
                                get_available_models(),
                                value="Yolo11 (dataset 2)",
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
                    with gr.Group():
                        with gr.Row():
                            sahi_mode = gr.Checkbox(
                                label=i18n("Включить"),
                                info=i18n(
                                    "Включить обработку с разбиением на фрагменты (SAHI)?"
                                ),
                            )
                        with gr.Row(visible=False) as slice_row:
                            slice_height = gr.Number(value=640, label=i18n("Высота слайса"))
                            slice_width = gr.Number(value=640, label=i18n("Ширина слайса"))
                        with gr.Row(visible=False) as slice_row2:
                            overlap_height_ratio = gr.Slider(
                                minimum=0.0,
                                maximum=1.0,
                                value=0.1,
                                step=0.01,
                                label=i18n("Перекрытие по высоте"),
                            )
                            overlap_width_ratio = gr.Slider(
                                minimum=0.0,
                                maximum=1.0,
                                value=0.1,
                                step=0.01,
                                label=i18n("Перекрытие по ширине"),
                            )
                    with gr.Row(equal_height=True) as solution_and_segment_mode_row:
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
                        )
                    with gr.Row(visible=False):
                        round_value = gr.Dropdown(
                            [0, 1, 2, 3, 4, 5, 6],
                            value=4,
                            label=i18n("Округлять результаты до"),
                        )
                    with gr.Row(equal_height=True):
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

            process_button.click(
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
                    download_output,
                    output_table,
                    output_plot,
                    output_table2,
                    output_image2,
                    question_row,
                    buttons_row,
                    AnnotatedImage_row,
                    chatbot_row,
                ],
            )
            # llm_run.click(
                # fn=chatbot_visibility, inputs=None, outputs=[chatbot_row2]
            # )
            llm_run.click(
                fn=llm_amalysis.analyze, inputs=[output_table, model_llm], outputs=[chatbot]
            )
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
                ],
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
                    output_table,
                    output_table2,
                    output_plot,
                    output_table,
                    output_table2,
                    output_plot,
                    in_image,
                    download_output,
                    output_image2,
                    output_table_image2,
                    question_row,
                    buttons_row,
                    AnnotatedImage_row,
                    output_table_image2_row,
                    chatbot,
                    chatbot_row,
                ],
            )

            scale_selector.change(
                fn=reset_interface,
                inputs=[scale_selector],
                outputs=[
                    im,
                    output_image,
                    output_table,
                    output_table2,
                    output_plot,
                    output_table,
                    output_table2,
                    output_plot,
                    in_image,
                    download_output,
                    output_image2,
                    output_table_image2,
                    question_row,
                    buttons_row,
                    AnnotatedImage_row,
                    output_table_image2_row,
                    chatbot,
                    chatbot_row,
                ],
            )

            yes_button.click(
                fn=log_analytics,
                inputs=[
                    confidence_threshold,
                    confidence_iou,
                    model_change,
                    gr.State("yes"),
                ],
                outputs=[question_row, buttons_row],
            )

            no_button.click(
                fn=log_analytics,
                inputs=[
                    confidence_threshold,
                    confidence_iou,
                    model_change,
                    gr.State("no"),
                ],
                outputs=[question_row, buttons_row],
            )

            output_table.change(
                fn=save_data_to_csv,
                inputs=[output_table, output_table2],
                outputs=download_output,
            )

    return demo
