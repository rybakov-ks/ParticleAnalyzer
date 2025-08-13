import os
import gradio as gr
from gradio_rangeslider import RangeSlider
from particleanalyzer.core.ParticleAnalyzer import ParticleAnalyzer
from particleanalyzer.core.utils import (
    scale_input_visibility,
    sahi_mode_visibility,
    reset_interface,
    reset_interface2,
    log_analytics,
    empty_df_ParticleCharacteristics,
    empty_df_ParticleStatistics,
    save_data_to_csv,
    scale_input_unit_measurement,
    toggleTheme,
    translate_chatbot,
    statistic_an,
    select_particle_from_image,
    particle_removal,
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
    checkbox_label_background_fill="#2196f3",
    checkbox_label_background_fill_dark="#2196f3",
    input_background_fill_focus="f1f5f9",
    input_background_fill_focus_dark="334155",
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
        points_df = gr.State()
        with gr.Column(elem_id="app-container"):
            with gr.Row(equal_height=True, elem_id="gr-head"):
                gr.HTML(
                    f"""
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: inline-block; margin-left: 7px; overflow: hidden;">
                          <img 
                            src="https://rybakov-k.ru/assets/icon/Logo2.png" 
                            alt="ParticleAnalyzer" 
                            style="max-height: 50px; width: auto; height: auto;"
                            class="logo-image"
                          >
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
                    with gr.Row(elem_id="analyze-row"):
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
                                    gr.Video(
                                        f'{assets_path("")}/instruction.mp4',
                                        label=i18n("Видео инструкция"),
                                    )
                            with gr.Row(equal_height=True):
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
                                        image_mode="RGB",
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
                            with gr.Row(visible=False) as output_table_image2_row:
                                with gr.Column():
                                    output_table_image2 = gr.Dataframe(
                                        value=empty_df_ParticleCharacteristics,
                                        label=i18n("Характеристики частицы"),
                                        interactive=True,
                                        elem_id="dataframe-table",
                                        show_copy_button=True,
                                    )
                                    delete_row = gr.Button(
                                        value=i18n("Удалить частицу"),
                                        icon="https://rybakov-k.ru/assets/icon/incorrect.png",
                                        elem_id="delete-row-btn",
                                        elem_classes="custom-btn btn-delete-row",
                                    )

                            with gr.Row(visible=False) as scale_input_row:
                                scale_input = gr.Number(
                                    label="Длина шкалы в мкм",
                                    value=1.0,
                                    elem_id="scale-input",
                                )

                            with gr.Row(elem_id="button-row"):
                                with gr.Column(min_width=140):
                                    process_button = gr.Button(
                                        value=i18n("Анализировать"),
                                        icon="https://rybakov-k.ru/assets/icon/icons8-химия-50.png",
                                        elem_id="process-button",
                                        elem_classes="custom-btn btn-analyze",
                                    )
                                with gr.Column(min_width=140):
                                    clear_button = gr.Button(
                                        value=i18n("Очистить"),
                                        icon="https://rybakov-k.ru/assets/icon/icons8-метла-50.png",
                                        elem_id="clear-btn",
                                        elem_classes="custom-btn btn-clear",
                                    )

                    with gr.Row(elem_id="example-row") as in_image_example_row:
                        gr.Examples(
                            examples=[
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/100%20r-.jpg",
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/Tv30_1.webp",
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/A02-1.webp",
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/Rec-Cu-Ni-Powder_250x_5_SE_V1_png.jpg",
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/Resolution%20in%20SEM%201.jpg",
                                "https://raw.githubusercontent.com/rybakov-ks/ParticleAnalyzer/main/example/image_c_01.webp",
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
                                    with gr.Row(elem_id="button-row"):
                                        with gr.Column(min_width=140):
                                            llm_run = gr.Button(
                                                value=i18n("Запустить ИИ-анализ"),
                                                icon="https://rybakov-k.ru/assets/icon/ai.png",
                                                elem_id="ai-run-btn",
                                                elem_classes="custom-btn btn-ai-run",
                                            )
                                        with gr.Column(min_width=140):
                                            cancel_llm_button = gr.Button(
                                                value=i18n("Отменить"),
                                                icon="https://rybakov-k.ru/assets/icon/incorrect.png",
                                                elem_id="ai-cancel-btn",
                                                elem_classes="custom-btn btn-ai-cancel",
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
                                    with gr.Row(elem_id="button-row"):
                                        with gr.Column(min_width=140):
                                            yes_button = gr.Button(
                                                value=i18n("Да"),
                                                icon="https://rybakov-k.ru/assets/icon/like.png",
                                                elem_id="yes-btn",
                                                elem_classes="custom-btn btn-yes",
                                            )
                                        with gr.Column(min_width=140):
                                            no_button = gr.Button(
                                                value=i18n("Нет"),
                                                icon="https://rybakov-k.ru/assets/icon/dislike.png",
                                                elem_id="no-btn",
                                                elem_classes="custom-btn btn-no",
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
                            number_detections = gr.Slider(
                                minimum=1,
                                maximum=10000,
                                value=1000,
                                step=100,
                                label=i18n("Количество обнаружений"),
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
                        with gr.Column():
                            show_polylines = gr.Checkbox(
                                value=True,
                                label=i18n("Включить"),
                                info=i18n("Включить контур?"),
                            )
                        with gr.Column():
                            outline_color = gr.ColorPicker(
                                value="rgb(0, 255, 0, 1)", label=i18n("Цвет контура")
                            )
                        with gr.Column(min_width=100):
                            show_fillPoly = gr.Checkbox(
                                label=i18n("Включить"),
                                info=i18n("Включить заливку?"),
                            )
                        with gr.Column(min_width=250):
                            fill_type_color = gr.Radio(
                                ("Random", "Permanent"),
                                value="Random",
                                label=i18n("Тип заливки"),
                            )
                        with gr.Column(min_width=300):
                            fill_color = gr.ColorPicker(
                                value="rgb(0, 255, 0, 1)", label=i18n("Цвет заливки")
                            )
                        with gr.Column():
                            fill_alpha = gr.Slider(
                                minimum=0,
                                maximum=1,
                                value=0.3,
                                step=0.01,
                                label=i18n("Прозрачность заливки"),
                            )
                with gr.Tab(i18n("О программе")):
                    gr.HTML(i18n(about_ru))
        with gr.Row(visible=False) as slider:
            with gr.Sidebar(width=400):
                with gr.Row():
                    gr.HTML(
                        f"""<h2 style="display: flex; align-items: center; gap: 8px;">
                            <i class='fa fa-filter' style='color: #2563eb;'></i>
                            {i18n('Параметры фильтрации')}
                           </h2>"""
                    )
                with gr.Row():
                    d_max_slider = RangeSlider(label="Dₘₐₓ")
                with gr.Row():
                    d_min_slider = RangeSlider(label="Dₘᵢₙ")
                with gr.Row():
                    theta_max_slider = RangeSlider(
                        label="θₘₐₓ [°]",
                        minimum=0.00,
                        maximum=180.00,
                        value=(0.00, 180.00),
                        step=0.01,
                    )
                with gr.Row():
                    theta_min_slider = RangeSlider(
                        label="θₘᵢₙ [°]",
                        minimum=0.00,
                        maximum=180.00,
                        value=(0.00, 180.00),
                        step=0.01,
                    )
                with gr.Row():
                    e_slider = RangeSlider(
                        label="e",
                        minimum=0.00,
                        maximum=1.00,
                        value=(0.00, 1.00),
                        step=0.01,
                    )
                with gr.Row():
                    S_slider = RangeSlider(
                        label="S",
                    )
                with gr.Row():
                    P_slider = RangeSlider(
                        label="P",
                    )
                with gr.Row():
                    I_slider = RangeSlider(
                        label=f"I [{i18n('ед.')}]",
                    )
                # with gr.Row():
                # apply_filter = gr.Button(value=i18n('Применить фильтр'), icon='https://rybakov-k.ru/assets/icon/dislike.png', elem_id='filter-btn', elem_classes='custom-btn btn-f')
                # apply_filter = gr.HTML(
                # f"""
                # <button class="custom-btn btn-f" id="filter-btn" style="display: flex; align-items: center; gap: 8px;">
                # <i class="fas fa-filter" style="color: #000000; font-size: 1.1em;"></i>
                # {i18n('Применить фильтр')}
                # </button>
                # """
                # )
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
                show_Feret_diametr,
                outline_color,
                show_fillPoly,
                show_polylines,
                fill_type_color,
                fill_color,
                fill_alpha,
                api_key,
            ],
            outputs=[
                output_image,
                output_table,
                points_df,
                output_plot,
                output_table2,
                chatbot_row,
                results_row,
                d_max_slider,
                d_min_slider,
                theta_max_slider,
                theta_min_slider,
                e_slider,
                S_slider,
                P_slider,
                I_slider,
                slider,
            ],
            show_progress_on=output_image,
        )

        output_image.select(
            select_particle_from_image,
            inputs=[points_df, output_table],
            outputs=[output_table_image2, output_table_image2_row],
        )

        process_button.click(translate_chatbot, None, chatbot)
        delete_row.click(
            particle_removal,
            inputs=[output_table_image2, points_df, output_table],
            outputs=[output_table_image2_row, points_df, output_table],
        ).success(
            fn=statistic_an,
            inputs=[
                output_table,
                points_df,
                scale_selector,
                round_value,
                number_of_bins,
                d_max_slider,
                d_min_slider,
                theta_max_slider,
                theta_min_slider,
                e_slider,
                S_slider,
                P_slider,
                I_slider,
                im,
                in_image,
                solution,
                sahi_mode,
                outline_color,
                show_fillPoly,
                show_polylines,
                fill_type_color,
                fill_color,
                fill_alpha,
            ],
            outputs=[output_table2, output_plot, output_image],
        )
        gr.on(
            triggers=[
                d_max_slider.release,
                d_min_slider.release,
                theta_max_slider.release,
                theta_min_slider.release,
                e_slider.release,
                S_slider.release,
                P_slider.release,
                I_slider.release,
            ],
            fn=statistic_an,
            inputs=[
                output_table,
                points_df,
                scale_selector,
                round_value,
                number_of_bins,
                d_max_slider,
                d_min_slider,
                theta_max_slider,
                theta_min_slider,
                e_slider,
                S_slider,
                P_slider,
                I_slider,
                im,
                in_image,
                solution,
                sahi_mode,
                outline_color,
                show_fillPoly,
                show_polylines,
                fill_type_color,
                fill_color,
                fill_alpha,
            ],
            outputs=[output_table2, output_plot, output_image],
        )

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

        sahi_mode.change(
            sahi_mode_visibility,
            inputs=sahi_mode,
            outputs=[
                slice_row,
                slice_row2,
                solution_and_segment_mode_row,
            ],
            show_progress="hide",
            show_progress_on=slice_row,
        )

        gr.on(
            triggers=[clear_button.click, in_image.clear, im.clear],
            fn=reset_interface,
            inputs=[scale_selector],
            outputs=[
                im,
                output_image,
                output_plot,
                in_image,
                output_table_image2_row,
                chatbot,
                results_row,
                slider,
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
