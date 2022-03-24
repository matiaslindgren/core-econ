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

    width = height = 8
    scale = 100

    nearest_point_selector = common.altair_selector("Date")
    line_x = alt.X(
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
    line_y = alt.Y(
        "GDP",
        type="quantitative",
        axis=alt.Axis(grid=True, title=gdp_title, values=gdp_range),
        scale=alt.Scale(type="log", base=2),
    )
    line_color = alt.Color(
        "Country",
        type="nominal",
        legend=alt.Legend(values=countries, symbolLimit=len(countries)),
    )
    line = (
        alt.Chart(data)
        .mark_line()
        .encode(
            line_x,
            line_y,
            line_color,
        )
    )
    line_points = (
        alt.Chart(data)
        .mark_point()
        .encode(
            line_x,
            line_y,
            line_color,
            size=alt.value(scale // 2),
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
            line_x,
            opacity=alt.value(0),
            tooltip=[
                alt.Tooltip(
                    field="Date",
                    title="Year",
                    format="%Y",
                    formatType="time",
                ),
                *[
                    alt.Tooltip(field=country_gdp, format=",.0d")
                    for country_gdp in countries
                ],
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
    chart = (line + line_points + year_points + year_rule).properties(
        width=scale * width,
        height=scale * height,
    )
    chart = common.configure_altair_fonts(chart)
    return chart, data


def main():
    data = common.read_data(
        fn="read_csv",
        filename="the-two-germanies-planning-and-capitalism.csv",
    )
    chart, data = plot(data)
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
