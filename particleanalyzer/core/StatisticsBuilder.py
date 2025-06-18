import pandas as pd
import numpy as np
from scipy.stats import norm
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from particleanalyzer.core.languages import translations

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

    def build_distribution_fig(self):
        if self.df.empty:
            return None

        # Создаем 3 строки и 2 колонки (последний график будет один в третьей строке)
        fig = make_subplots(
            rows=5, cols=2,
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
            ),
            specs=[
                [{"secondary_y": True}, {"secondary_y": True}],
                [{"secondary_y": True}, {"secondary_y": True}],
                [{"secondary_y": True}, {"secondary_y": True}],
                [{"secondary_y": True}, {"secondary_y": True}],
                [{"secondary_y": True}, {"secondary_y": True}], 
            ],
            vertical_spacing=0.08,
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

        fig.update_layout(
            height=1200,  # Уменьшил высоту, так как графики компактнее
            showlegend=False,
            plot_bgcolor="white",
            margin=dict(l=50, r=50, b=50, t=50),  # Уменьшил отступы
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