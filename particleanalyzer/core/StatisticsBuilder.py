import pandas as pd
import numpy as np
from scipy.stats import norm
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.figure_factory as ff
from particleanalyzer.core.languages import translations


class StatisticsBuilder:
    def __init__(self, df, scale_selector, round_value, number_of_bins, lang="ru"):
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

        # Получаем единицу измерения из scale_selector
        unit = self._get_translation(self.scale_selector["unit"])

        # Создаем маппинг колонок с динамической подстановкой единиц измерения
        col_map = {
            "D": "D [{}]".format(unit),
            "Dₘₐₓ": "Dₘₐₓ [{}]".format(unit),
            "Dₘᵢₙ": "Dₘᵢₙ [{}]".format(unit),
            "Dₘₑₐₙ": "Dₘₑₐₙ [{}]".format(unit),
            "θₘₐₓ": "θₘₐₓ [°]",
            "θₘᵢₙ": "θₘᵢₙ [°]",
            "S": "S [{}²]".format(unit),
            "P": "P [{}]".format(unit),
            "e": "e",
            "I": f'I [{self._get_translation("ед.")}]',
        }
        stats = {
            self._get_translation("Параметр"): [
                col_map["D"],
                col_map["Dₘₐₓ"],
                col_map["Dₘᵢₙ"],
                col_map["Dₘₑₐₙ"],
                col_map["θₘₐₓ"],
                col_map["θₘᵢₙ"],
                col_map["S"],
                col_map["P"],
                "e",
                col_map["I"],
            ],
            self._get_translation("Среднее"): [
                round(self.df[col_map[k]].mean(), self.round_value) for k in col_map
            ],
            self._get_translation("Медиана"): [
                round(self.df[col_map[k]].median(), self.round_value) for k in col_map
            ],
            self._get_translation("Максимум"): [
                round(self.df[col_map[k]].max(), self.round_value) for k in col_map
            ],
            self._get_translation("Минимум"): [
                round(self.df[col_map[k]].min(), self.round_value) for k in col_map
            ],
            self._get_translation("СО"): [
                round(self.df[col_map[k]].std(), self.round_value) for k in col_map
            ],
        }

        df = pd.DataFrame(stats)

        empty_row = [""] * len(df.columns)
        empty_row[0] = self._get_translation("Количество частиц")
        empty_row[1] = len(self.df)
        count_row = pd.DataFrame([empty_row], columns=df.columns)
        df = pd.concat([df, count_row], ignore_index=True)

        styled_df = (
            df.style.apply(
                lambda row: [
                    "font-weight: bold" if i == 0 else "" for i in range(len(row))
                ],
                axis=1,
            )
            .apply(
                lambda row: [
                    "background-color: #ED7D31" if row.name == 0 else "" for _ in row
                ],
                axis=1,
            )
            .apply(
                lambda row: [
                    "background-color: #5B9BD5" if row.name == len(df) - 1 else ""
                    for _ in row
                ],
                axis=1,
            )
            .format(self._format_value)
        )

        return styled_df

    def _format_value(self, value):
        if not isinstance(value, (int, float)):  # если не число — не форматируем
            return value
        if pd.isnull(value):
            return ""
        if value == int(value):
            return str(int(value))
        return f"{value:.{self.round_value}f}"

    def build_distribution_fig(self, image):
        if self.df.empty:
            return None, None

        row_heights = [0.2, 0.2, 0.2, 0.2, 0.2]
        fig = make_subplots(
            rows=5,
            cols=2,
            row_heights=row_heights,
            subplot_titles=(
                self._get_translation("Распределение диаметра"),
                self._get_translation("Распределение диаметра Ферета"),
                self._get_translation("Распределение диаметра Ферета"),
                self._get_translation("Распределение диаметра Ферета"),
                self._get_translation("Распределение угла Ферета"),
                self._get_translation("Распределение угла Ферета"),
                self._get_translation("Распределение площади"),
                self._get_translation("Распределение периметра"),
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
            vertical_spacing=0.07,
            horizontal_spacing=0.11,
        )

        base_params = [
            (1, 1, "D", self._get_translation("Диаметр"), "red"),
            (1, 2, "Dₘₑₐₙ", self._get_translation("Средний диаметр"), "darksalmon"),
            (2, 1, "Dₘₐₓ", self._get_translation("Максимальный диаметр"), "goldenrod"),
            (
                2,
                2,
                "Dₘᵢₙ",
                self._get_translation("Минимальный диаметр"),
                "lightsteelblue",
            ),
            (3, 1, "θₘₐₓ", self._get_translation("Максимальный угол"), "olive"),
            (3, 2, "θₘᵢₙ", self._get_translation("Минимальный угол"), "orange"),
            (4, 1, "S", self._get_translation("Площадь"), "green"),
            (4, 2, "P", self._get_translation("Периметр"), "blue"),
            (5, 1, "e", self._get_translation("Эксцентриситет"), "magenta"),
            (5, 2, "I", self._get_translation("Интенсивность"), "cyan"),
        ]

        unit = self._get_translation(self.scale_selector["unit"])

        params = []
        for row, col, short_name, full_name, color in base_params:
            if short_name in ["D", "Dₘₑₐₙ", "Dₘₐₓ", "Dₘᵢₙ", "P"]:
                unit_format = " [{}]".format(unit)
            elif short_name == "S":
                unit_format = " [{}²]".format(unit)
            elif short_name in ["θₘₐₓ", "θₘᵢₙ"]:
                unit_format = " [°]"
            elif short_name == "I":
                unit_format = f' [{self._get_translation("ед.")}]'
            else:
                unit_format = ""

            full_param_name = self._get_translation(full_name) + unit_format
            short_param_name = (
                self._get_translation(short_name) if short_name != "e" else "e"
            ) + unit_format

            params.append((row, col, short_param_name, full_param_name, color))

        for row, col, col_name, label, color in params:
            self._add_distribution(fig, row, col, self.df[col_name], label, color)
            fig.update_traces(
                showlegend=False,
            )

        fig.update_layout(
            height=1150,
            plot_bgcolor="white",
            margin=dict(l=50, r=50, b=50, t=50),
            modebar={
                "orientation": "h",
                "remove": [
                    "zoom",
                    "pan",
                    "select",
                    "lasso",
                    "reset",
                    "zoomIn2d",
                    "zoomOut2d",
                    "autoscale",
                    "resetScale2d",
                    "toggleSpikelines",
                    "hoverCompareCartesian",
                ],
            },
        )

        vector_fig = None
        if "centroid_x" in self.df.columns and "centroid_y" in self.df.columns:
            vector_fig = self._create_vector_field_fig(self.df, image)

        return fig, vector_fig

    def _add_distribution(self, fig, row, col, data, title, color):
        if data.dropna().empty:
            return

        fig.add_trace(
            go.Histogram(
                x=data,
                nbinsx=self.number_of_bins,
                name=title,
                marker_color=color,
                opacity=0.7,
                marker_line_color="black",
                marker_line_width=1.5,
            ),
            row=row,
            col=col,
        )

        mu, std = norm.fit(data.dropna())
        if not np.isclose(std, 0):
            x = np.linspace(min(data), max(data), 100)
            y = norm.pdf(x, mu, std)

            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    name=f'{title} {self._get_translation("(норм. распр.)")}',
                    line=dict(color="black", width=2, dash="dash"),
                ),
                row=row,
                col=col,
                secondary_y=True,
            )

        fig.update_yaxes(
            title_text=self._get_translation("Количество") if col == 1 else "",
            row=row,
            col=col,
            automargin=True,
            mirror=True,
            linewidth=2,
            linecolor="black",
            ticks="inside",
            tickcolor="black",
            tickwidth=2,
            ticklen=5,
            showgrid=False,
        )
        fig.update_yaxes(
            title_text=(
                self._get_translation("Плотность вероятности") if col == 2 else ""
            ),
            secondary_y=True,
            row=row,
            col=col,
            automargin=True,
            mirror=True,
            linewidth=2,
            linecolor="black",
            ticks="inside",
            tickcolor="black",
            tickwidth=2,
            ticklen=5,
            showgrid=False,
        )
        fig.update_xaxes(
            title_text=title,
            row=row,
            col=col,
            mirror=True,
            linewidth=2,
            linecolor="black",
            ticks="inside",
            tickcolor="black",
            tickwidth=2,
            ticklen=5,
            showgrid=False,
        )

    def _create_vector_field_fig(self, df, image):
        vector_fig = go.Figure()

        self._add_vector_field_to_fig(vector_fig, df, image)

        vector_fig.update_layout(
            height=600,
            width=800,
            plot_bgcolor="white",
            margin=dict(l=50, r=130, b=20, t=50),
            legend=dict(
                itemsizing="constant",
                itemclick="toggle",
                itemdoubleclick=False,
                orientation="h",
                yanchor="top",
                y=-0.10,
                xanchor="center",
                x=0.48,
                font=dict(size=14),
            ),
            modebar={
                "orientation": "h",
                "remove": [
                    "zoom",
                    "pan",
                    "select",
                    "lasso",
                    "reset",
                    "zoomIn2d",
                    "zoomOut2d",
                    "autoscale",
                    "resetScale2d",
                    "toggleSpikelines",
                    "hoverCompareCartesian",
                ],
            },
        )

        vector_fig.add_annotation(
            text=self._get_translation("Векторное поле ориентации"),
            xref="paper",
            yref="paper",
            x=0.5,
            y=1.07,
            showarrow=False,
            font=dict(size=18),
            xanchor="center",
            yanchor="top",
        )

        return vector_fig

    def _add_vector_field_to_fig(self, fig, df, image):
        image = np.flipud(image)

        fig.add_trace(
            go.Image(
                z=image,
                opacity=1,
                x0=0,
                y0=0,
                dx=1,
                dy=1,
                hoverinfo="skip",
                name="Background Image",
            )
        )

        df = df.head(1000)
        required_columns = {"centroid_x", "centroid_y"}
        if not required_columns.issubset(df.columns):
            return

        angle_max_col = self._get_translation("θₘₐₓ [°]")
        angle_min_col = self._get_translation("θₘᵢₙ [°]")

        if not all(col in df.columns for col in [angle_max_col, angle_min_col]):
            return

        unit = self._get_translation(self.scale_selector["unit"])
        diameter_max_col = "Dₘₐₓ [{}]".format(unit)
        diameter_min_col = "Dₘᵢₙ [{}]".format(unit)

        if not all(col in df.columns for col in [diameter_max_col, diameter_min_col]):
            return

        x = df["centroid_x"].values
        y = df["centroid_y"].values

        y = image.shape[0] - y

        theta_max_deg = df[angle_max_col].values
        theta_max_rad = np.deg2rad(theta_max_deg)
        diameters_max = df[diameter_max_col].values

        min_length = 20
        max_length = 60
        if len(diameters_max) > 1:
            lengths_max = min_length + (max_length - min_length) * (
                diameters_max - min(diameters_max)
            ) / (max(diameters_max) - min(diameters_max))
        else:
            lengths_max = [min_length]

        u_max = np.cos(theta_max_rad) * lengths_max
        v_max = np.sin(theta_max_rad) * lengths_max

        theta_min_deg = df[angle_min_col].values
        theta_min_rad = np.deg2rad(theta_min_deg)
        diameters_min = df[diameter_min_col].values

        if len(diameters_min) > 1:
            lengths_min = min_length + (max_length - min_length) * (
                diameters_min - min(diameters_min)
            ) / (max(diameters_min) - min(diameters_min))
        else:
            lengths_min = [min_length]

        u_min = np.cos(theta_min_rad) * lengths_min
        v_min = np.sin(theta_min_rad) * lengths_min

        quiver_max = ff.create_quiver(
            x,
            y,
            u_max,
            v_max,
            scale=1,
            arrow_scale=0.3,
            line=dict(width=2, color="yellow", shape="spline"),
            name=self._get_translation("Удлинение"),
        )

        quiver_min = ff.create_quiver(
            x,
            y,
            u_min,
            v_min,
            scale=1,
            arrow_scale=0.25,
            line=dict(width=1.5, color="cyan", shape="spline"),
            name=self._get_translation("Утолщение"),
            visible="legendonly",
        )

        for trace in quiver_max.data + quiver_min.data:
            fig.add_trace(trace)

        fig.update_xaxes(
            title_text=self._get_translation("X"),
            range=[0, image.shape[1]],
            constrain="domain",
            showgrid=False,
        )

        fig.update_yaxes(
            title_text=self._get_translation("Y"),
            range=[0, image.shape[0]],
            scaleanchor="x",
            scaleratio=1,
            constrain="domain",
            showgrid=False,
        )
