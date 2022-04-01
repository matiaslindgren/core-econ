import sys
import math

import altair as alt
import pandas as pd

alt.data_transformers.disable_max_rows()

import common


def plot(data):
    data = data.rename(
        columns={
            "GDP per capita (1990 $)": "GDP",
            "Entity": "Country",
        }
    )
    data = data.drop(columns=["Code"])
    data["Date"] = pd.to_datetime(data.pop("Year"), format="%Y", errors="coerce")

    countries = sorted(data.Country.unique())
    gdp_range = [64000 / (2 ** i) for i in range(10)][::-1]
    gdp_title = "GDP (1990 US$)"
    chart_size = 800

    nearest_point_selector = common.altair_selector("Date")
    encoding_year = alt.X(
        "Date",
        title="Year",
        type="temporal",
        timeUnit="year",
        axis=alt.Axis(
            grid=True,
            labelAngle=0,
            format="%Y",
            formatType="time",
        ),
    )
    encoding_gdp = alt.Y(
        "GDP",
        type="quantitative",
        axis=alt.Axis(grid=True, title=gdp_title, values=gdp_range),
        scale=alt.Scale(type="log", base=2),
    )
    line = (
        alt.Chart(data)
        .mark_line()
        .encode(
            encoding_year,
            encoding_gdp,
            alt.Color(
                "Country",
                type="nominal",
                scale=alt.Scale(scheme="set2"),
                legend=None,
            ),
        )
    )
    line_points = (
        alt.Chart(data)
        .mark_point()
        .encode(
            encoding_year,
            encoding_gdp,
            size=alt.value(chart_size // 30),
            opacity=alt.condition(
                ~nearest_point_selector,
                alt.value(0),
                alt.value(1),
            ),
        )
    )
    year_points = (
        alt.Chart(
            data.pivot(index="Date", columns="Country", values="GDP").reset_index()
        )
        .mark_point()
        .encode(
            encoding_year,
            opacity=alt.value(0),
            tooltip=[
                alt.Tooltip(
                    field="Date",
                    title="title",
                    format="%Y",
                    formatType="time",
                ),
                *[country_gdp for country_gdp in countries],
            ],
        )
        .add_selection(nearest_point_selector)
    )
    year_rule = (
        alt.Chart(data)
        .mark_rule(color="gray")
        .encode(x="Date:T")
        .transform_filter(nearest_point_selector)
    )
    chart = line_points + line + year_points + year_rule
    chart = chart.properties(width="container", height=chart_size)
    chart = common.configure_altair_fonts(chart)
    return chart, data


def main():
    data = common.read_data(
        fn="read_csv",
        filename="the-two-germanies-planning-and-capitalism.csv",
    )
    chart, data = plot(data)
    print(common.render(__file__, chart=chart, custom_tooltip=True))
    return data


if __name__ == "__main__":
    data = main()
