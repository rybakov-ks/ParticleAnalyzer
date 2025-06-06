import gradio as gr
from core.ParticleAnalyzer import ParticleAnalyzer 
from core.utils import (
    scale_input_visibility, segment_mode_visibility,
    sahi_mode_visibility, select_section, reset_interface, log_analytics,
    empty_df2, empty_df3, save_data_to_csv, toggle_theme
)
from core.ui_styles import css, custom_head

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
            gr.Markdown(
                """
                # 🔎 ParticleAnalyzer
                При помощи данного инструмента можно анализировать размерные характеристики частиц на изображениях SEM.
                """
            )
            mode_state = gr.State(value="Тёмный режим")
            with gr.Tabs():
                with gr.Tab("Анализ"):
                    # Основной интерфейс
                    with gr.Row():
                        with gr.Column(visible=False) as Paint_row:
                            # Вход: изображение
                            im = gr.Paint(
                                label="Изображение СЭМ",
                                type="numpy",
                                canvas_size=(600, 600),  # Увеличиваем размер канваса
                                sources=['upload'],
                                brush=gr.Brush(color_mode='fixed', default_color='green', colors=['green']),
                                transforms='crop',
                                layers=False,
                                eraser=gr.Eraser(default_size=200),
                            )
                        with gr.Column() as Image_row:
                            in_image = gr.Image(sources=["upload"], label="Изображение СЭМ")
                        
                        with gr.Column():
                            # Выход: изображение с контурами
                            output_image = gr.Image(label="Результат сегментации")

                    with gr.Row(visible=False) as AnnotatedImage_row:
                        # Анализ отдельных частиц
                        output_image2 = gr.AnnotatedImage(label="Результат сегментации")
                    with gr.Row(visible=False) as output_table_image2_row:
                        # Таблица с характеристиками
                        output_table_image2 = gr.Dataframe(
                            value=empty_df2,
                            label="Характеристики частицы",
                            interactive=False,
                            elem_id="dataframe-table"
                        )
                    with gr.Row() as in_image_example_row:   
                            gr.Examples(['assets/example/100 r-.jpg', 
                            'assets/example/Tv30_1.png', 
                            'assets/example/A02-1.bmp',
                            'assets/example/Rec-Cu-Ni-Powder_250x_5_SE_V1_png.jpg',
                            'assets/example/Resolution in SEM 1.jpg',
                            'assets/example/left_half.jpg'], in_image, label='Примеры')
                    with gr.Row(visible=False) as im_example_row:   
                            gr.Examples(['assets/example/100 r-.jpg', 
                            'assets/example/Tv30_1.png', 
                            'assets/example/A02-1.bmp',
                            'assets/example/Rec-Cu-Ni-Powder_250x_5_SE_V1_png.jpg',
                            'assets/example/Resolution in SEM 1.jpg',], im, label='Примеры')
                    with gr.Row(visible=False) as scale_input_row:
                        scale_input = gr.Number(label="Шкала прибора в мкм", value=1.0)
                    with gr.Row():
                        process_button = gr.Button("Анализировать", variant="primary", size="md", icon='assets/icon/icons8-химия-50.png')
                        clear_button = gr.Button("Очистить", size="md", icon='assets/icon/icons8-метла-50.png')
                    # Таблица и графики на новой строке
                    with gr.Row():
                        label = gr.Label(label="Количество частиц", visible=False)
                    # Таблица и графики на новой строке
                    with gr.Row():
                        # Таблица с характеристиками
                        output_table2 = gr.Dataframe(
                            value=empty_df3,
                            label="Статистика по частицам",
                            interactive=False,
                            visible=False,
                            elem_id="dataframe-table2",
                            show_copy_button=True
                        )
                    with gr.Row():
                        # Таблица с характеристиками
                        output_table = gr.Dataframe(
                            value=empty_df2,
                            label="Характеристики частиц",
                            interactive=False,
                            visible=False,
                            elem_id="dataframe-table",
                            show_search='filter',
                            show_copy_button=True
                        )
                    with gr.Row():
                        download_output = gr.Files(label="Файлы для скачивания", visible=False)
                    with gr.Row():
                        # Графики распределения
                        output_plot = gr.Plot(
                            label="Графики распределения",
                            visible=False 
                        )
                    with gr.Row(visible=False) as question_row:
                        gr.Markdown(
                            """
                                Вы удовлетворены качеством сегментации?
                            """
                        )
                    with gr.Row(visible=False) as buttons_row:
                        with gr.Column(scale=1):
                            yes_button = gr.Button("Да", variant="secondary", size="sm", icon='assets/icon/like.png')
                        with gr.Column(scale=1):
                            no_button = gr.Button("Нет", variant="stop", size="sm", icon='assets/icon/dislike.png')
                            
                with gr.Tab("Настройки"):
                    with gr.Row():    
                        toggle_dark = gr.Button(value="Тёмный режим", size="sm", icon='assets/icon/icons8-темный-режим-50.png')
                    with gr.Row():
                        model_change = gr.Dropdown(["Yolo11 (dataset 1)", "Yolo12 (dataset 1)", "Yolo11 (dataset 2)", "Yolo12 (dataset 2)", "R101",
                        "X101", "Cascade_R50", "Cascade_X152"], value="Yolo11 (dataset 2)", label="Модель обнаружения")
                    with gr.Row():
                        sahi_mode = gr.Checkbox(label="Включить", info="Включить обработку с разбиением на фрагменты?")       
                    with gr.Row(visible=False) as slice_row:
                        slice_height = gr.Number(value=640, label="Высота слайса")
                        slice_width = gr.Number(value=640, label="Ширина слайса")
                    with gr.Row(visible=False) as slice_row2:
                        overlap_height_ratio = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.1,
                            step=0.01,
                            label="Перекрытие по высоте")
                        overlap_width_ratio = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.1,
                            step=0.01, 
                            label="Перекрытие по ширине")
                        
                    with gr.Row():
                        # Слайдер для точности обнаружения
                        confidence_threshold = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.5,
                            step=0.01,
                            label="Точность обнаружения (порог уверенности)"
                        )
                    with gr.Row():
                        # Слайдер для iou 
                        confidence_iou = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.7,
                            step=0.01,
                            label="Порог перекрытия (IoU)"
                        )
                    with gr.Row() as number_detections_row:
                        # Слайдер для number_detections 
                        number_detections = gr.Slider(
                            minimum=1,
                            maximum=10000,
                            value=300,
                            step=100,
                            label="Максимальное количество обнаружений"
                        )
                    with gr.Row():
                        # Селектор для масштаба
                        scale_selector = gr.Radio(["Пиксели", "Шкала прибора в мкм"], value="Пиксели", label="Режим масштабирования")
                    with gr.Row() as solution_row:
                        # Переключатель разрешения
                        solution = gr.Radio(["Оригинал", "640x640", "1024x1024"], value="1024x1024", label="Разрешение изображения")
                    with gr.Row():
                        # Выпадающий список для округления
                        round_value = gr.Dropdown([0, 1, 2, 3, 4, 5, 6], value=2, label="Округлять результаты до")
                    with gr.Row() as segment_mode_row:
                        segment_mode = gr.Checkbox(label="Включить", info="Включить режим анализа отдельных частиц?")    
                    with gr.Row():
                        # Слайдер для number_of_bins 
                        number_of_bins = gr.Slider(
                            minimum=0.0,
                            maximum=100,
                            value=20,
                            step=1,
                            label="Количество интервалов на гистограмме"
                        )
                        
            # Основная функция обработки изображений при нажатии кнопки
            process_button.click(
                fn=analyzer.analyze_image,
                inputs=[im, in_image, scale_input, confidence_threshold, scale_selector, 
                        confidence_iou, number_detections, solution, model_change, round_value, 
                        slice_height, slice_width, overlap_height_ratio, overlap_width_ratio, sahi_mode,
                        number_of_bins],
                outputs=[output_image, output_table, output_plot, output_table2, download_output, label, label,
                        output_table, output_plot, output_table2, output_image2, question_row, buttons_row]
            )

            scale_selector.change(scale_input_visibility, inputs=scale_selector, outputs=[scale_input_row, Paint_row, Image_row, output_table, in_image_example_row, output_table_image2])

            segment_mode.change(segment_mode_visibility, inputs=segment_mode, outputs=[AnnotatedImage_row, output_table_image2_row])
                
            sahi_mode.change(sahi_mode_visibility, inputs=sahi_mode, outputs=[slice_row, slice_row2, number_detections_row, segment_mode_row, segment_mode, solution_row])

            output_image2.select(select_section, output_table, output_table_image2)

            clear_button.click(
                fn=reset_interface,
                inputs=[scale_selector],
                outputs=[im, output_image, output_table, output_table2, output_plot, output_table, output_table2, output_plot, in_image, download_output,
                label, output_image2, output_table_image2, question_row, buttons_row]
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