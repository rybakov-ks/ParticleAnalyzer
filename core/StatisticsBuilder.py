import pandas as pd
import numpy as np
from scipy.stats import norm
from plotly.subplots import make_subplots
import plotly.graph_objs as go

class StatisticsBuilder:
    def __init__(self, df, scale_selector, round_value, number_of_bins):
        self.df = df
        self.scale_selector = scale_selector
        self.round_value = round_value
        self.number_of_bins = number_of_bins
        self.units = 'мкм' if scale_selector == 'Шкала прибора в мкм' else 'пикс'
    
    def build_stats_table(self):
        if self.df.empty:
            return pd.DataFrame()

        col_map = {
            "S": f"S [{'мкм²' if self.units == 'мкм' else 'пикс²'}]",
            "P": f"P [{self.units}]",
            "D": f"D [{self.units}]",
            "e": "e",
            "I": "I [ед.]"
        }

        stats = {
            "Параметр": [col_map["S"], col_map["P"], col_map["D"], "e", col_map["I"]],
            "Среднее": [round(self.df[col_map[k]].mean(), self.round_value) for k in col_map],
            "Медиана": [round(self.df[col_map[k]].median(), self.round_value) for k in col_map],
            "Максимум": [round(self.df[col_map[k]].max(), self.round_value) for k in col_map],
            "Минимум": [round(self.df[col_map[k]].min(), self.round_value) for k in col_map],
            "СО": [round(self.df[col_map[k]].std(), self.round_value) for k in col_map],
        }

        return pd.DataFrame(stats)

    def build_distribution_fig(self):
        if self.df.empty:
            return None

        fig = make_subplots(
            rows=5, cols=1,
            subplot_titles=[
                "Распределение площади", "Распределение периметра", "Распределение диаметра",
                "Распределение эксцентриситета", "Распределение интенсивности"
            ],
            specs=[[{"secondary_y": True}]] * 5,
            vertical_spacing=0.05
        )

        params = [
            (1, f"S [{'мкм²' if self.units == 'мкм' else 'пикс²'}]", "Площадь", "green"),
            (2, f"P [{self.units}]", "Периметр", "blue"),
            (3, f"D [{self.units}]", "Диаметр", "red"),
            (4, "e", "Эксцентриситет", "magenta"),
            (5, "I [ед.]", "Интенсивность", "cyan"),
        ]

        for row, col_name, label, color in params:
            self._add_distribution(fig, row, self.df[col_name], f"{label} [{col_name.split('[')[-1]}", color)

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
            x=x, y=y, mode='lines', name=f'{title} (норм. распр.)',
            line=dict(color='black', width=2, dash='dash')
        ), row=row, col=1, secondary_y=True)

        fig.update_yaxes(
            title_text="Количество", row=row, col=1, automargin=True,
            mirror=True, linewidth=2, linecolor='black',
            ticks="inside", tickcolor='black', tickwidth=2, ticklen=5,
            showgrid=False
        )
        fig.update_yaxes(
            title_text="Плотность вероятности", secondary_y=True, row=row, col=1, automargin=True,
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
