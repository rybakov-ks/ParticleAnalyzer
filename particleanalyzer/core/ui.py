# -*- coding: utf-8 -*-
import os
import gradio as gr
from particleanalyzer.core.ParticleAnalyzer import ParticleAnalyzer 
from particleanalyzer.core.utils import (
    scale_input_visibility, segment_mode_visibility,
    sahi_mode_visibility, select_section, reset_interface, log_analytics,
    empty_df2, empty_df3, save_data_to_csv, toggle_theme
)
from particleanalyzer.core.ui_styles import css, custom_head
from particleanalyzer.core.languages import i18n

try:
    import detectron2
    model_list = ["Yolo11 (dataset 1)", "Yolo12 (dataset 1)", "Yolo11 (dataset 2)", "Yolo12 (dataset 2)", "R101",
                        "X101", "Cascade_R50", "Cascade_X152"]
except ImportError:
    model_list = ["Yolo11 (dataset 1)", "Yolo12 (dataset 1)", "Yolo11 (dataset 2)", "Yolo12 (dataset 2)"]

base_path = os.path.dirname(__file__)
assets_path = lambda name: os.path.join(base_path, "..", "assets", name)

analyzer = ParticleAnalyzer()

def create_interface():
    demo = gr.Blocks(
        theme='snehilsanyal/scikit-learn',
        title='ParticleAnalyzer — Инструмент для анализа изображений SEM',
        head=custom_head,
        css=css,
        analytics_enabled=False
    )

    with demo:
        with gr.Column(elem_id="app-container"):
            gr.Markdown("# 🔎 ParticleAnalyzer")
            gr.Markdown(i18n("При помощи данного инструмента можно анализировать размерные характеристики частиц на изображениях SEM."))
            mode_state = gr.State(value=i18n("Тёмный режим"))
            with gr.Tabs():
                with gr.Tab(i18n("Анализ")):
                    # Основной интерфейс
                    with gr.Row():
                        with gr.Column(visible=False) as Paint_row:
                            # Вход: изображение
                            im = gr.Paint(
                                label=i18n("Изображение СЭМ"),
                                type="numpy",
                                canvas_size=(600, 600),  # Увеличиваем размер канваса
                                sources=['upload'],
                                brush=gr.Brush(color_mode='fixed', default_color='green', colors=['green']),
                                transforms='crop',
                                layers=False,
                                eraser=gr.Eraser(default_size=200),
                            )
                        with gr.Column() as Image_row:
                            in_image = gr.Image(sources=["upload"], label=i18n("Изображение СЭМ"))
                        
                        with gr.Column():
                            # Выход: изображение с контурами
                            output_image = gr.Image(label=i18n("Результат сегментации"))

                    with gr.Row(visible=False) as AnnotatedImage_row:
                        # Анализ отдельных частиц
                        output_image2 = gr.AnnotatedImage(label=i18n("Результат сегментации"))
                    with gr.Row(visible=False) as output_table_image2_row:
                        # Таблица с характеристиками
                        output_table_image2 = gr.Dataframe(
                            value=empty_df2,
                            label=i18n("Характеристики частицы"),
                            interactive=False,
                            elem_id="dataframe-table"
                        )
                    with gr.Row() as in_image_example_row:   
                            gr.Examples([f'{assets_path("")}/example/100 r-.jpg', 
                            f'{assets_path("")}/example/Tv30_1.png', 
                            f'{assets_path("")}/example/A02-1.bmp',
                            f'{assets_path("")}/example/Rec-Cu-Ni-Powder_250x_5_SE_V1_png.jpg',
                            f'{assets_path("")}/example/Resolution in SEM 1.jpg',
                            f'{assets_path("")}/example/left_half.jpg'], in_image, label=i18n('Примеры'))
                    with gr.Row(visible=False) as im_example_row:   
                            gr.Examples([f'{assets_path("")}/example/100 r-.jpg', 
                            f'{assets_path("")}/example/Tv30_1.png', 
                            f'{assets_path("")}/example/A02-1.bmp',
                            f'{assets_path("")}/example/Rec-Cu-Ni-Powder_250x_5_SE_V1_png.jpg',
                            f'{assets_path("")}/example/Resolution in SEM 1.jpg',], im, label=i18n('Примеры'))
                    with gr.Row(visible=False) as scale_input_row:
                        scale_input = gr.Number(label=i18n("Instrument scale in µm"), value=1.0)
                    with gr.Row():
                        process_button = gr.Button(value=i18n("Анализировать"), variant="primary", size="md", icon=f'{assets_path("")}/icon/icons8-химия-50.png')
                        clear_button = gr.Button(value=i18n("Очистить"), size="md", icon=f'{assets_path("")}/icon/icons8-метла-50.png')
                    # Таблица и графики на новой строке
                    with gr.Row():
                        label = gr.Label(label=i18n("Количество частиц"), visible=False)
                    # Таблица и графики на новой строке
                    with gr.Row():
                        # Таблица с характеристиками
                        output_table2 = gr.Dataframe(
                            value=empty_df3,
                            label=i18n("Статистика по частицам"),
                            interactive=False,
                            visible=False,
                            elem_id="dataframe-table2",
                            show_copy_button=True
                        )
                    with gr.Row():
                        # Таблица с характеристиками
                        output_table = gr.Dataframe(
                            value=empty_df2,
                            label=i18n("Характеристики частиц"),
                            interactive=False,
                            visible=False,
                            elem_id="dataframe-table",
                            show_search='filter',
                            show_copy_button=True
                        )
                    with gr.Row():
                        download_output = gr.Files(label=i18n("Файлы для скачивания"), visible=False)
                    with gr.Row():
                        # Графики распределения
                        output_plot = gr.Plot(
                            label=i18n("Графики распределения"),
                            visible=False 
                        )
                    with gr.Row(visible=False) as question_row:
                        gr.Markdown(i18n("Вы удовлетворены качеством сегментации?"))
                    with gr.Row(visible=False) as buttons_row:
                        with gr.Column(scale=1):
                            yes_button = gr.Button(value=i18n("Да"), variant="secondary", size="sm", icon=f'{assets_path("")}/icon/like.png')
                        with gr.Column(scale=1):
                            no_button = gr.Button(value=i18n("Нет"), variant="stop", size="sm", icon=f'{assets_path("")}/icon/dislike.png')
                            
                with gr.Tab(i18n("Настройки")):
                    with gr.Row():    
                        toggle_dark = gr.Button(value=i18n("Тёмный режим"), size="sm", icon=f'{assets_path("")}/icon/icons8-темный-режим-50.png')
                    with gr.Row():
                        # Селектор для масштаба
                        scale_selector = gr.Radio(("Pixels", "Instrument scale in µm"), value="Pixels", label=i18n("Режим масштабирования"))
                    with gr.Row():
                        model_change = gr.Dropdown(model_list, value="Yolo11 (dataset 2)", label=i18n("Модель обнаружения"))
                    with gr.Row():
                        # Слайдер для точности обнаружения
                        confidence_threshold = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.5,
                            step=0.01,
                            label=i18n("Точность обнаружения (порог уверенности)")
                        )
                    with gr.Row():
                        # Слайдер для iou 
                        confidence_iou = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.7,
                            step=0.01,
                            label=i18n("Порог перекрытия (IoU)")
                        )
                    with gr.Row() as solution_row:
                        # Переключатель разрешения
                        solution = gr.Radio(("Original", "640x640", "1024x1024"), value="1024x1024", label=i18n("Разрешение изображения"))
                    with gr.Row():
                        sahi_mode = gr.Checkbox(label=i18n("Включить"), info=i18n("Включить обработку с разбиением на фрагменты (SAHI)?"))       
                    with gr.Row(visible=False) as slice_row:
                        slice_height = gr.Number(value=640, label=i18n("Высота слайса"))
                        slice_width = gr.Number(value=640, label=i18n("Ширина слайса"))
                    with gr.Row(visible=False) as slice_row2:
                        overlap_height_ratio = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.1,
                            step=0.01,
                            label=i18n("Перекрытие по высоте"))
                        overlap_width_ratio = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.1,
                            step=0.01, 
                            label=i18n("Перекрытие по ширине"))
                    with gr.Row() as segment_mode_row:
                        segment_mode = gr.Checkbox(label=i18n("Включить"), info=i18n("Включить режим анализа отдельных частиц?")) 
                    with gr.Row() as number_detections_row:
                        # Слайдер для number_detections 
                        number_detections = gr.Slider(
                            minimum=1,
                            maximum=10000,
                            value=1000,
                            step=100,
                            label=i18n("Максимальное количество обнаружений")
                        )
                    with gr.Row():
                        # Выпадающий список для округления
                        round_value = gr.Dropdown([0, 1, 2, 3, 4, 5, 6], value=2, label=i18n("Округлять результаты до"))   
                    with gr.Row():
                        # Слайдер для number_of_bins 
                        number_of_bins = gr.Slider(
                            minimum=0.0,
                            maximum=100,
                            value=20,
                            step=1,
                            label=i18n("Количество интервалов на гистограмме")
                        )
                        
            # Основная функция обработки изображений при нажатии кнопки
            process_button.click(
                fn=analyzer.analyze_image,
                inputs=[im, in_image, scale_input, confidence_threshold, scale_selector, 
                        confidence_iou, number_detections, solution, model_change, round_value, 
                        slice_height, slice_width, overlap_height_ratio, overlap_width_ratio, sahi_mode,
                        number_of_bins, segment_mode],
                outputs=[output_image, output_table, output_plot, output_table2, download_output, label, label,
                        output_table, output_plot, output_table2, output_image2, question_row, buttons_row,
                        AnnotatedImage_row]
            )

            scale_selector.change(scale_input_visibility, inputs=scale_selector, outputs=[scale_input_row, Paint_row, Image_row, output_table, 
                                in_image_example_row, output_table_image2])

            segment_mode.change(segment_mode_visibility, inputs=segment_mode, outputs=[AnnotatedImage_row, output_table_image2_row])
                
            sahi_mode.change(sahi_mode_visibility, inputs=sahi_mode, outputs=[slice_row, slice_row2, number_detections_row, segment_mode_row, segment_mode, solution_row])

            output_image2.select(select_section, inputs=output_table, outputs=[output_table_image2, output_table_image2_row])

            clear_button.click(
                fn=reset_interface,
                inputs=[scale_selector],
                outputs=[im, output_image, output_table, output_table2, output_plot, output_table, output_table2, output_plot, in_image, download_output,
                label, output_image2, output_table_image2, question_row, buttons_row, AnnotatedImage_row, output_table_image2_row]
            )
            
            scale_selector.change(
                fn=reset_interface,
                inputs=[scale_selector],
                outputs=[im, output_image, output_table, output_table2, output_plot, output_table, output_table2, output_plot, in_image, download_output,
                label, output_image2, output_table_image2, question_row, buttons_row, AnnotatedImage_row, output_table_image2_row]
            )
            
            yes_button.click(
                fn=log_analytics,
                inputs=[confidence_threshold, confidence_iou, model_change, gr.State("yes")],  # Передаем "yes"
                outputs=[question_row, buttons_row]
            )
            
            no_button.click(
                fn=log_analytics,
                inputs=[confidence_threshold, confidence_iou, model_change, gr.State("no")],  # Передаем "no"
                outputs=[question_row, buttons_row]
            )
            
            output_table.change(fn=save_data_to_csv, inputs=[output_table, output_table2], outputs=download_output)

            toggle_dark.click(toggle_theme, inputs=[mode_state], outputs=[mode_state, toggle_dark],
                js="""
                () => {
                    document.body.classList.toggle('dark')
                }
                """)

    return demo