import pandas as pd
import numpy as np
from scipy.stats import norm
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.figure_factory as ff
from particleanalyzer.core.languages import translations

from PIL import Image
from io import BytesIO
import base64


class StatisticsBuilder:
    def __init__(self, df, scale_selector, round_value, number_of_bins, lang='ru'):
        self.df = df
        self.scale_selector = scale_selector
        self.round_value = round_value
        self.number_of_bins = number_of_bins
        self.lang = lang

    def _get_translation(self, text):
        return translations.get(self.lang, {}).get(text, text)
 
    def build_stats_table(self):
        if self.df.empty:
            return pd.DataFrame()
        
        if self.scale_selector == self._get_translation('Instrument scale in µm'):
            col_map = {
                "S": self._get_translation("S [мкм²]"),
                "P": self._get_translation("P [мкм]"),
                "D": self._get_translation("D [мкм]"),
                "Dₘₐₓ": self._get_translation("Dₘₐₓ [мкм]"),
                "Dₘᵢₙ": self._get_translation("Dₘᵢₙ [мкм]"),
                "Dₘₑₐₙ": self._get_translation("Dₘₑₐₙ [мкм]"),
                "θₘₐₓ": self._get_translation("θₘₐₓ [°]"),
                "θₘᵢₙ": self._get_translation("θₘᵢₙ [°]"),
                "e": "e",
                "I": self._get_translation("I [ед.]")
            }
        else:
            col_map = {
                "S": self._get_translation("S [пикс²]"),
                "P": self._get_translation("P [пикс]"),
                "D": self._get_translation("D [пикс]"),
                "Dₘₐₓ": self._get_translation("Dₘₐₓ [пикс]"),
                "Dₘᵢₙ": self._get_translation("Dₘᵢₙ [пикс]"),
                "Dₘₑₐₙ": self._get_translation("Dₘₑₐₙ [пикс]"),
                "θₘₐₓ": self._get_translation("θₘₐₓ [°]"),
                "θₘᵢₙ": self._get_translation("θₘᵢₙ [°]"),
                "e": "e",
                "I": self._get_translation("I [ед.]")
            }
        stats = {
            self._get_translation("Параметр"): [col_map["S"], col_map["P"], col_map["D"], col_map["Dₘₐₓ"], col_map["Dₘᵢₙ"], 
                                    col_map["Dₘₑₐₙ"], col_map["θₘₐₓ"], col_map["θₘᵢₙ"], "e", col_map["I"]],
            self._get_translation("Среднее"): [round(self.df[col_map[k]].mean(), self.round_value) for k in col_map],
            self._get_translation("Медиана"): [round(self.df[col_map[k]].median(), self.round_value) for k in col_map],
            self._get_translation("Максимум"): [round(self.df[col_map[k]].max(), self.round_value) for k in col_map],
            self._get_translation("Минимум"): [round(self.df[col_map[k]].min(), self.round_value) for k in col_map],
            self._get_translation("СО"): [round(self.df[col_map[k]].std(), self.round_value) for k in col_map],
        }

        return pd.DataFrame(stats)

    def build_distribution_fig(self, image):
        if self.df.empty:
            return None
        row_heights = [0.14, 0.14, 0.14, 0.14, 0.14, 0.30]
        # Создаем 3 строки и 2 колонки (последний график будет один в третьей строке)
        fig = make_subplots(
            rows=6, cols=2, row_heights=row_heights,
            subplot_titles=(
                self._get_translation("Распределение площади"), 
                self._get_translation("Распределение периметра"),
                self._get_translation("Распределение диаметра"),
                self._get_translation("Распределение диаметра Ферета"),
                self._get_translation("Распределение диаметра Ферета"),
                self._get_translation("Распределение диаметра Ферета"),
                self._get_translation("Распределение угла Ферета"),
                self._get_translation("Распределение угла Ферета"),
                self._get_translation("Распределение эксцентриситета"), 
                self._get_translation("Распределение интенсивности"),
                self._get_translation("Векторное поле ориентации"),
                ""
            ),
            specs=[
                [{"secondary_y": True}, {"secondary_y": True}],
                [{"secondary_y": True}, {"secondary_y": True}],
                [{"secondary_y": True}, {"secondary_y": True}],
                [{"secondary_y": True}, {"secondary_y": True}],
                [{"secondary_y": True}, {"secondary_y": True}], 
                [{"secondary_y": True, "colspan": 2}, None] 
            ],
            vertical_spacing=0.05,
            horizontal_spacing=0.2
        )

        if self.scale_selector == self._get_translation('Instrument scale in µm'):
            params = [
                (1, 1, self._get_translation("S [мкм²]"), self._get_translation("Площадь [мкм²]"), "green"),
                (1, 2, self._get_translation("P [мкм]"), self._get_translation("Периметр [мкм]"), "blue"),
                (2, 1, self._get_translation("D [мкм]"), self._get_translation("Диаметр [мкм]"), "red"),
                (2, 2, self._get_translation("Dₘₑₐₙ [мкм]"), self._get_translation("Средний диаметр [мкм]"), "darksalmon"),
                (3, 1, self._get_translation("Dₘₐₓ [мкм]"), self._get_translation("Максимальный диаметр [мкм]"), "goldenrod"),
                (3, 2, self._get_translation("Dₘᵢₙ [мкм]"), self._get_translation("Минимальный диаметр [мкм]"), "lightsteelblue"),
                (4, 1, self._get_translation("θₘₐₓ [°]"), self._get_translation("Максимальный угол [°]"), "olive"),
                (4, 2, self._get_translation("θₘᵢₙ [°]"), self._get_translation("Минимальный угол [°]"), "orange"),                
                (5, 1, "e", self._get_translation("Эксцентриситет"), "magenta"),
                (5, 2, self._get_translation("I [ед.]"), self._get_translation("Интенсивность"), "cyan"),
            ]
        else:
            params = [
                (1, 1, self._get_translation("S [пикс²]"), self._get_translation("Площадь [пикс²]"), "green"),
                (1, 2, self._get_translation("P [пикс]"), self._get_translation("Периметр [пикс]"), "blue"),
                (2, 1, self._get_translation("D [пикс]"), self._get_translation("Диаметр [пикс]"), "red"),
                (2, 2, self._get_translation("Dₘₑₐₙ [пикс]"), self._get_translation("Средний диаметр [пикс]"), "darksalmon"),
                (3, 1, self._get_translation("Dₘₐₓ [пикс]"), self._get_translation("Максимальный диаметр [пикс]"), "goldenrod"),
                (3, 2, self._get_translation("Dₘᵢₙ [пикс]"), self._get_translation("Минимальный диаметр [пикс]"), "lightsteelblue"),
                (4, 1, self._get_translation("θₘₐₓ [°]"), self._get_translation("Максимальный угол [°]"), "olive"),
                (4, 2, self._get_translation("θₘᵢₙ [°]"), self._get_translation("Минимальный угол [°]"), "orange"),  
                (5, 1, "e", self._get_translation("Эксцентриситет"), "magenta"),
                (5, 2, self._get_translation("I [ед.]"), self._get_translation("Интенсивность"), "cyan"),
            ]

        for row, col, col_name, label, color in params:
            self._add_distribution(fig, row, col, self.df[col_name], label, color)

        if 'centroid_x' in self.df.columns and 'centroid_y' in self.df.columns:
            self._add_vector_field(fig, self.df, row=6, col=1, image=image)

        fig.update_layout(
            height=1600,
            showlegend=False,
            plot_bgcolor="white",
            margin=dict(l=50, r=50, b=50, t=50),
            modebar={
                'orientation': 'h',
                'remove': [
                    "zoom", "pan", "select", "lasso", "reset", "zoomIn2d", "zoomOut2d",
                    "autoscale", "resetScale2d", "toggleSpikelines", "hoverCompareCartesian"
                ]
            }
        )

        return fig

    def _add_distribution(self, fig, row, col, data, title, color):
        if data.dropna().empty:
            return

        fig.add_trace(go.Histogram(
            x=data, nbinsx=self.number_of_bins, name=title, marker_color=color, opacity=0.7,
            marker_line_color='black', marker_line_width=1.5
        ), row=row, col=col)

        mu, std = norm.fit(data.dropna())
        x = np.linspace(min(data), max(data), 100)
        y = norm.pdf(x, mu, std)

        fig.add_trace(go.Scatter(
            x=x, y=y, mode='lines', name=f'{title} {self._get_translation("(норм. распр.)")}',
            line=dict(color='black', width=2, dash='dash')
        ), row=row, col=col, secondary_y=True)

        # Обновляем оси только для текущего подграфика
        fig.update_yaxes(
            title_text=self._get_translation("Количество"), 
            row=row, col=col, 
            automargin=True,
            mirror=True, linewidth=2, linecolor='black',
            ticks="inside", tickcolor='black', tickwidth=2, ticklen=5,
            showgrid=False
        )
        fig.update_yaxes(
            title_text=self._get_translation("Плотность вероятности"), 
            secondary_y=True, 
            row=row, col=col,
            automargin=True,
            mirror=True, linewidth=2, linecolor='black',
            ticks="inside", tickcolor='black', tickwidth=2, ticklen=5,
            showgrid=False
        )
        fig.update_xaxes(
            title_text=title,
            row=row, col=col,
            mirror=True, linewidth=2, linecolor='black',
            ticks="inside", tickcolor='black', tickwidth=2, ticklen=5,
            showgrid=False
        )
        


    def _add_vector_field(self, fig, df, row, col, image):
        image = np.flipud(image)
        image_pil = Image.fromarray(image.astype(np.uint8))
        buffer = BytesIO()
        image_pil.save(buffer, format="PNG")
        encoded_image = base64.b64encode(buffer.getvalue()).decode()
        
        fig.add_trace(
            go.Image(
                z=image,
                opacity=1,
                x0=0,
                y0=image.shape[0],
                dx=1,
                dy=-1,
                hoverinfo='skip',
                name="Background Image"
            ),
            row=row,
            col=col
        )
        
        if not {'centroid_x', 'centroid_y'}.issubset(df.columns):
            return

        angle_column = self._get_translation("θₘₐₓ [°]")
        if angle_column not in df.columns:
            return

        if self.scale_selector == self._get_translation('Instrument scale in µm'):
            diameter_col = self._get_translation("Dₘₐₓ [мкм]")
        else:
            diameter_col = self._get_translation("Dₘₐₓ [пикс]")

        if diameter_col not in df.columns:
            return

        x = df['centroid_x'].values
        y = df['centroid_y'].values
        theta_deg = df[angle_column].values
        theta_rad = np.deg2rad(theta_deg)
        diameters = df[diameter_col].values

        min_length = 20  # минимальная длина стрелки
        max_length = 60  # максимальная длина стрелки
        if len(diameters) > 1:
            normalized_lengths = min_length + (max_length - min_length) * (diameters - min(diameters)) / (max(diameters) - min(diameters))
        else:
            normalized_lengths = [min_length]

        u = np.cos(theta_rad) * normalized_lengths
        v = np.sin(theta_rad) * normalized_lengths

        quiver_fig = ff.create_quiver(
                                        x, y, u, v,
                                        scale=1,
                                        arrow_scale=0.3,
                                        line=dict(
                                            width=2,
                                            color='yellow',
                                            shape='spline'
                                        )
                                    )

        for trace in quiver_fig.data:
            fig.add_trace(trace, row=row, col=col)

        fig.update_xaxes(
            title_text=self._get_translation("X"),
            row=row,
            col=col,
            range=[0, image.shape[1]],
            constrain='domain',
            showgrid=False
        )

        fig.update_yaxes(
            title_text=self._get_translation("Y"),
            row=row,
            col=col,
            range=[image.shape[0], 0],
            scaleanchor=f"x{2*(row-1)+col}",
            scaleratio=1,
            constrain='domain',
            showgrid=False
        )