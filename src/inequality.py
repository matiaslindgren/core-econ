import sys
import pathlib

import pandas as pd
import altair as alt

alt.data_transformers.disable_max_rows()

import common

DATA_URL = "https://raw.githubusercontent.com/jackblun/Globalinc/master/GCIPrawdata.csv"


def plot_income(data):
    data["Inequality"] = data["Decile 10 Income"] / data["Decile 1 Income"]
    inequality = data[["Country", "Year", "Inequality"]].copy()

    income = data.melt(
        id_vars=["Country", "Year"],
        value_vars=[f"Decile {i} Income" for i in range(1, 11)],
        value_name="Income",
        var_name="Decile",
    )
    income.Decile = income.Decile.str.split(expand=True)[1].astype(int)
    income = income.reset_index()
    income = income.merge(inequality, how="left", on=["Country", "Year"])
    income = income.drop(["index"], axis="columns")

    font_config = dict(
        titleFontSize=16,
        labelFontSize=14,
        titleFont="Georgia",
        labelFont="Georgia",
    )
    width, height = 2, 16
    width_ratio = 0.1
    scale = 150

    deciles_width = scale * (1 - width_ratio) * width
    inequality_width = scale * width_ratio * width

    income_label = "GDP ($ PPP)"

    slider = alt.binding_range(min=income.Year.min(), max=income.Year.max(), step=1)
    select_year = alt.selection_single(
        name="Year", fields=["Year"], bind=slider, init={"Year": income.Year.min()}
    )
    deciles_heatmap = (
        alt.Chart(income)
        .mark_rect()
        .encode(
            alt.X(
                "Decile",
                type="ordinal",
                axis=alt.Axis(title="Income decile", orient="top", labelAngle=0),
                scale=alt.Scale(padding=0),
            ),
            alt.Y(
                "Country",
                type="nominal",
                sort=alt.Sort(op="median", field="Income", order="descending"),
                axis=alt.Axis(title=None),
                scale=alt.Scale(padding=0),
            ),
            alt.Color(
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
        .properties(width=deciles_width, height=scale * height)
    )
    inequality_heatmap = (
        alt.Chart(income)
        .mark_rect()
        .encode(
            alt.Y(
                "Country",
                type="nominal",
                sort=alt.Sort(op="median", field="Income", order="descending"),
                axis=alt.Axis(title=None, labels=False),
                scale=alt.Scale(padding=0),
            ),
            alt.Color(
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
        .properties(title="Inequality", width=inequality_width, height=scale * height)
    )
    chart = (deciles_heatmap | inequality_heatmap).resolve_scale(color="independent")
    chart = (
        chart.add_selection(select_year)
        .transform_filter(select_year)
        .configure_view(strokeWidth=0)
        .configure_axis(grid=False)
    )
    chart = common.configure_altair_fonts(chart, font_config)
    return common.altair_chart_to_html(chart)


def main():
    elements = common.header_elements(__file__)
    data = common.read_data(
        fn="read_csv",
        url=DATA_URL,
        header=2,
    )
    html = plot_income(data)
    elements.append(html)
    print(common.render(__file__, elements=elements))
    return data


if __name__ == "__main__":
    data = main()
