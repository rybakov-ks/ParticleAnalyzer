# -*- coding: utf-8 -*-
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
        #self.units = self._get_translation('мкм') if scale_selector == self._get_translation('Instrument scale in µm') else self._get_translation('пикс')

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
                "e": "e",
                "I": self._get_translation("I [ед.]")
            }
        else:
            col_map = {
                "S": self._get_translation("S [пикс²]"),
                "P": self._get_translation("P [пикс]"),
                "D": self._get_translation("D [пикс]"),
                "e": "e",
                "I": self._get_translation("I [ед.]")
            }
        stats = {
            self._get_translation("Параметр"): [col_map["S"], col_map["P"], col_map["D"], "e", col_map["I"]],
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

        fig = make_subplots(
            rows=5, cols=1,
            subplot_titles=self._get_translation(
                                            ("Распределение площади", "Распределение периметра", "Распределение диаметра",
                                            "Распределение эксцентриситета", "Распределение интенсивности")
                                        ),
            specs=[[{"secondary_y": True}]] * 5,
            vertical_spacing=0.05
        )

        if self.scale_selector == self._get_translation('Instrument scale in µm'):
            params = [
            (1, self._get_translation("S [мкм²]"), self._get_translation("Площадь [мкм²]"), "green"),
            (2, self._get_translation("P [мкм]"), self._get_translation("Периметр [мкм]"), "blue"),
            (3, self._get_translation("D [мкм]"), self._get_translation("Диаметр [мкм]"), "red"),
            (4, "e", self._get_translation("Эксцентриситет"), "magenta"),
            (5, self._get_translation("I [ед.]"), self._get_translation("Интенсивность"), "cyan"),
            ]
        else:
            params = [
            (1, self._get_translation("S [пикс²]"), self._get_translation("Площадь [пикс²]"), "green"),
            (2, self._get_translation("P [пикс]"), self._get_translation("Периметр [пикс]"), "blue"),
            (3, self._get_translation("D [пикс]"), self._get_translation("Диаметр [пикс]"), "red"),
            (4, "e", self._get_translation("Эксцентриситет"), "magenta"),
            (5, self._get_translation("I [ед.]"), self._get_translation("Интенсивность"), "cyan"),
            ]

        for row, col_name, label, color in params:
            self._add_distribution(fig, row, self.df[col_name], f"{label}", color)

        fig.update_layout(
            height=2000,
            showlegend=False,
            plot_bgcolor="white",
            modebar={
                'orientation': 'h',
                'remove': [
                    "zoom", "pan", "select", "lasso", "reset", "zoomIn2d", "zoomOut2d",
                    "autoscale", "resetScale2d", "toggleSpikelines", "hoverCompareCartesian"
                ]
            }
        )
        return fig

    def _add_distribution(self, fig, row, data, title, color):
        if data.dropna().empty:
            return

        fig.add_trace(go.Histogram(
            x=data, nbinsx=self.number_of_bins, name=title, marker_color=color, opacity=0.7,
            marker_line_color='black', marker_line_width=1.5
        ), row=row, col=1)

        mu, std = norm.fit(data.dropna())
        x = np.linspace(min(data), max(data), 100)
        y = norm.pdf(x, mu, std)

        fig.add_trace(go.Scatter(
            x=x, y=y, mode='lines', name=f'{title} {self._get_translation("(норм. распр.)")}',
            line=dict(color='black', width=2, dash='dash')
        ), row=row, col=1, secondary_y=True)

        fig.update_yaxes(
            title_text=self._get_translation("Количество"), row=row, col=1, automargin=True,
            mirror=True, linewidth=2, linecolor='black',
            ticks="inside", tickcolor='black', tickwidth=2, ticklen=5,
            showgrid=False
        )
        fig.update_yaxes(
            title_text=self._get_translation("Плотность вероятности"), secondary_y=True, row=row, col=1, automargin=True,
            mirror=True, linewidth=2, linecolor='black',
            ticks="inside", tickcolor='black', tickwidth=2, ticklen=5,
            showgrid=False
        )
        fig.update_xaxes(
            title_text=title,
            mirror=True, linewidth=2, linecolor='black',
            ticks="inside", tickcolor='black', tickwidth=2, ticklen=5,
            row=row, col=1, showgrid=False
        )
