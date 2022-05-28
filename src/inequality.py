import sys
import pathlib

import pandas as pd
import altair as alt

alt.data_transformers.disable_max_rows()

import common

DATA_URL = "https://raw.githubusercontent.com/jackblun/Globalinc/master/GCIPrawdata.csv"


def plot_income(data):
    data = common.reindex_multiple_columns(data, "Country", "Year")
    data["Inequality"] = data["Decile 10 Income"] / data["Decile 1 Income"]
    inequality = data.Inequality.copy()

    income = data.melt(
        value_vars=[f"Decile {i} Income" for i in range(1, 11)],
        value_name="Income",
        var_name="Decile",
        ignore_index=False,
    )
    income.Decile = income.Decile.str.split(expand=True)[1].astype(int)
    income = income.join(inequality)
    income = income.reset_index()

    width, height = 2, 16
    width_ratio = 0.1
    scale = 150

    deciles_width = scale * (1 - width_ratio) * width
    inequality_width = scale * width_ratio * width

    income_label = "GDP (US$ PPP)"

    chart = alt.Chart(income)
    select_year = common.altair_range_input(
        field="Year",
        init=income.Year.min(),
        min=income.Year.min(),
        max=income.Year.max(),
    )
    deciles_heatmap = (
        chart.mark_rect()
        .encode(
            x=alt.X(
                "Decile",
                type="ordinal",
                axis=alt.Axis(title="Income decile", orient="top", labelAngle=0),
                scale=alt.Scale(padding=0),
            ),
            y=alt.Y(
                "Country",
                type="nominal",
                sort=alt.Sort(op="median", field="Income", order="descending"),
                axis=alt.Axis(title=None),
                scale=alt.Scale(padding=0),
            ),
            color=alt.Color(
                "Income",
                type="quantitative",
                legend=alt.Legend(
                    title=income_label,
                    gradientLength=deciles_width,
                    orient="top",
                    direction="horizontal",
                    titleAnchor="middle",
                ),
                scale=alt.Scale(
                    scheme="yellowgreen",
                    domainMin=income.Income.min(),
                    domainMax=income.Income.max(),
                ),
            ),
            tooltip=[
                "Country",
                "Year",
                "Decile",
                alt.Tooltip(field="Income", title=income_label, format=","),
            ],
        )
        .properties(
            width=deciles_width,
            height=scale * height,
        )
    )
    inequality_heatmap = (
        chart.mark_rect()
        .encode(
            y=common.altair_replace(
                deciles_heatmap.encoding.y,
                axis=alt.Axis(title=None, labels=False),
            ),
            color=alt.Color(
                "Inequality",
                type="quantitative",
                legend=None,
                scale=alt.Scale(scheme="reds"),
            ),
            tooltip=[
                "Country",
                "Year",
                alt.Tooltip(field="Inequality", format=".1f"),
            ],
        )
        .properties(
            title="Inequality",
            width=inequality_width,
            height=scale * height,
        )
    )
    chart = alt.hconcat(
        deciles_heatmap,
        inequality_heatmap,
        usermeta={"inputsOnTop": True},
    )
    chart = (
        chart.resolve_scale(color="independent")
        .add_selection(select_year)
        .transform_filter(select_year)
        .configure_view(strokeWidth=0)
        .configure_axis(grid=False)
    )
    chart = common.configure_altair_fonts(chart)
    return chart, income


def main():
    data = common.download_data(DATA_URL, header=2)
    chart, data = plot_income(data)
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
