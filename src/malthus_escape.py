import sys
import math

import altair as alt
import pandas as pd

alt.data_transformers.disable_max_rows()

import common


def plot(data):
    data = data.drop(columns=["Entity", "Code"])
    data = data.sort_values("Year")

    nearest_point_selector = common.altair_selector("Year")
    line = (
        alt.Chart(data)
        .mark_trail()
        .encode(
            x=alt.X(
                "Year",
                type="ordinal",
                axis=alt.Axis(values=list(data.Year[::2])),
            ),
            y=alt.Y(
                "Real wage index (1860 = 100)",
                type="quantitative",
                scale=alt.Scale(domainMin=40, domainMax=120),
            ),
            size=alt.Size(
                "Population (millions)",
                type="quantitative",
                scale=alt.Scale(domainMin=1, domainMax=20),
            ),
        )
    )
    year_points = (
        alt.Chart(data)
        .mark_point()
        .add_selection(nearest_point_selector)
        .encode(
            x=line.encoding.x,
            opacity=alt.value(0),
            tooltip=[
                "Year:O",
                alt.Tooltip(
                    line.encoding.y.shorthand,
                    title="Real wage index",
                    format=".1f",
                ),
                alt.Tooltip(
                    line.encoding.size.shorthand,
                    format=".1f",
                ),
            ],
        )
    )
    year_rule = (
        alt.Chart(data[["Year"]])
        .mark_rule(color="gray")
        .transform_filter(nearest_point_selector)
        .encode(x=line.encoding.x)
    )

    chart = line + year_points + year_rule
    chart = chart.properties(width="container", height=500)
    chart = common.configure_altair_fonts(chart)

    return chart, data


def main():
    data = common.read_data("escaping-the-malthusian-trap.csv")
    chart, data = plot(data)
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
