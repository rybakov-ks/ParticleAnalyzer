import cv2
import gradio as gr
import pandas as pd
import csv
import os
from datetime import datetime

# Создаем пустые DataFrame с нужными заголовками
empty_df1 = pd.DataFrame(columns=[
    "№", 
    "S [мкм²]",  # Площадь в квадратных микрометрах
    "P [мкм]",   # Периметр в микрометрах
    "D [мкм]",   # Диаметр в микрометрах
    "e",         # Эксцентриситет (безразмерная величина)
    "I [ед.]"    # Интенсивность в условных единицах
])
empty_df2 = pd.DataFrame(columns=[
    "№", 
    "S [пикс²]", # Площадь в квадратных пикселях 
    "P [пикс]",  # Периметр в пикселях
    "D [пикс]",  # Диаметр в пикселях
    "e",         # Эксцентриситет (безразмерная величина)
    "I [ед.]"    # Интенсивность в условных единицах
]).fillna("")
empty_df2_2 = pd.DataFrame(columns=[
    "№", 
    "S [мкм²]",  # Площадь в квадратных микрометрах
    "P [мкм]",   # Периметр в микрометрах
    "D [мкм]",   # Диаметр в микрометрах
    "e",         # Эксцентриситет (безразмерная величина)
    "I [ед.]"    # Интенсивность в условных единицах
]).fillna("")
empty_df3 = pd.DataFrame(columns=[
    "Параметр",  # Параметр
    "Среднее",   # Среднее
    "Медиана",    # Медиана
    "Максимум",   # Максимум
    "Минимум",    # Минимум
    "СО"      # Стандартное отклонение
])

def scale_input_visibility(scale_value):
    """Показываем масштабную шкалу"""
    return (
            gr.update(visible=(scale_value == "Шкала прибора в мкм")), 
            gr.update(visible=(scale_value == "Шкала прибора в мкм")), 
            gr.update(visible=(scale_value == "Пиксели")), 
            gr.update(value=(empty_df2 if scale_value == "Пиксели" else empty_df1)), 
            gr.update(visible=(scale_value == "Пиксели")),
            gr.update(value=(empty_df2 if scale_value == "Пиксели" else empty_df2_2))
           )

def segment_mode_visibility(segment_mode):
    """Режим анализа отдельных частиц"""
    return gr.update(visible=segment_mode), gr.update(visible=segment_mode)

def select_section(evt: gr.SelectData, output_table):
    """Режим анализа отдельных частиц. Возвращаем параметры частицы"""
    if 0 <= evt.index < len(output_table):
        return output_table.iloc[[evt.index]]
    else:
        return empty_df2  
        
def sahi_mode_visibility(sahi_mode):
    """Режим SAHI"""
    return (
        gr.update(visible=sahi_mode),
        gr.update(visible=sahi_mode),
        gr.update(visible=not sahi_mode),
        gr.update(visible=not sahi_mode),
        gr.update(value=False if sahi_mode else None),
        gr.update(visible=not sahi_mode)
    )

def reset_interface(scale_value):
    """Функция для сброса интерфейса"""
    return (
        None,  # Очищаем im
        None,  # Очищаем output_image
        pd.DataFrame(columns=[
            "№", 
            "S [мкм²]",  # Площадь в квадратных микрометрах
            "P [мкм]",   # Периметр в микрометрах
            "D [мкм]",   # Диаметр в микрометрах
            "e",         # Эксцентриситет (безразмерная величина)
            "I [ед.]"    # Интенсивность в условных единицах
        ]),
        pd.DataFrame(columns=[
            "Параметр",  # Параметр
            "Среднее",   # Среднее
            "Медиана",    # Медиана
            "Максимум",   # Максимум
            "Минимум",    # Минимум
            "СО"      # Стандартное отклонение
        ]),
        None,  # Очищаем графики
        gr.update(visible=False),  # Скрываем таблицу
        gr.update(visible=False),  # Скрываем таблицу
        gr.update(visible=False),  # Скрываем графики
        None,  # Очищаем input_image
        gr.update(visible=False),  # Скрываем таблицу
        gr.update(visible=False),  # Скрываем label
        None,  # Очищаем output_image2
        empty_df2 if scale_value == "Пиксели" else empty_df2_2, # Очищаем output_table_image2
        gr.update(visible=False),  # Скрываем таблицу
        gr.update(visible=False),  # Скрываем label
    )
    
def save_data_to_csv(data_table: pd.DataFrame, data_table2: pd.DataFrame, output_dir: str = "output"):
    """Сохраняет данные частиц в CSV файлы"""
    os.makedirs(output_dir, exist_ok=True)
    
    particle_path = os.path.join(output_dir, "particle_characteristics.csv")
    stats_path = os.path.join(output_dir, "particle_statistics.csv")
    
    data_table.to_csv(particle_path, index=False, encoding="utf-8-sig")
    data_table2.to_csv(stats_path, index=False, encoding="utf-8-sig")
    
    return [particle_path, stats_path]

def toggle_theme(current_mode: str):
    """Переключает между темной и светлой темой"""
    if current_mode == "Тёмный режим":
        return 'Светлый режим', gr.Button(value='Светлый режим', icon='assets/icon/icons8-солнце-50.png')
    return 'Тёмный режим', gr.Button(value='Тёмный режим', icon='assets/icon/icons8-темный-режим-50.png')

def log_analytics(
    confidence_threshold: float,
    confidence_iou: float,
    model_name: str,
    feedback: str,
    output_dir: str = "output"
):
    """Логирует аналитические данные о работе модели"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Находим последний обработанный файл
    files = [f for f in os.listdir(output_dir) 
             if not f.endswith('.csv') and os.path.isfile(os.path.join(output_dir, f))]
    
    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(output_dir, x))) if files else "N/A"
    
    analytic_path = os.path.join(output_dir, "analytics.csv")
    file_exists = os.path.isfile(analytic_path)
    
    with open(analytic_path, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Model", "Confidence", "IoU", 
                "Feedback", "ProcessedFile"
            ])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            model_name,
            confidence_threshold,
            confidence_iou,
            feedback,
            latest_file
        ])
    
    return gr.update(visible=False), gr.update(visible=False)
    

