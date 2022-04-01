import sys
import math

import altair as alt
import pandas as pd

alt.data_transformers.disable_max_rows()

import common


def plot(data):
    data = data.rename(
        columns={"Deviation from 1951-1990 average temperature": "Deviation"}
    )
    data = data[["Year", "Deviation"]]

    nearest_point_selector = common.altair_selector("Year")
    line = (
        alt.Chart(data)
        .mark_point()
        .encode(
            size=alt.condition(
                ~nearest_point_selector,
                alt.value(6),
                alt.value(100),
            ),
            x=alt.X(
                "Year",
                type="ordinal",
                axis=alt.Axis(
                    grid=False,
                    labelAngle=0,
                    values=list(data.Year[::50]),
                ),
            ),
            y=alt.Y(
                "Deviation",
                type="quantitative",
                axis=alt.Axis(
                    grid=True,
                    title="Deviation from 1951-1990 mean temperature (°C)",
                ),
            ),
            color=alt.Color(
                "Deviation",
                type="quantitative",
                scale=alt.Scale(
                    domainMin=-0.5,
                    domainMid=0,
                    domainMax=0.5,
                    range=["#6babd0", "lightgray", "#bf363a"],
                ),
                legend=None,
            ),
        )
    )
    year_points = (
        alt.Chart(data)
        .mark_point()
        .encode(
            x="Year:O",
            opacity=alt.value(0),
            tooltip=[
                "Year",
                alt.Tooltip(
                    field="Deviation",
                    title="Deviation (°C)",
                    format=".2f",
                ),
            ],
        )
        .add_selection(nearest_point_selector)
    )
    zero_rule = (
        alt.Chart(pd.DataFrame([{"Deviation": 0.0}]))
        .mark_rule(color="gray")
        .encode(
            y="Deviation:Q",
            size=alt.SizeValue(1),
        )
    )
    year_rule = (
        alt.Chart(data)
        .mark_rule(color="gray")
        .encode(x="Year:O")
        .transform_filter(nearest_point_selector)
    )
    chart = line + year_points + year_rule + zero_rule
    chart = chart.properties(width="container", height=400)
    chart = common.configure_altair_fonts(chart)
    return chart, data


def main():
    data = common.read_data(
        fn="read_csv",
        filename="northern-hemisphere-temperatures-over-the-long-run-deviation-from-1951-1990-mean-temperature-c.csv",
    )
    chart, data = plot(data)
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
