import sys
import math

import altair as alt
import pandas as pd

alt.data_transformers.disable_max_rows()

import common


def plot_growth(data):
    data = data.rename(
        columns={
            "Real GDP per capita in 2011 US$": "GDP",
            "Entity": "Country",
        }
    )
    del data["Code"]
    data["Date"] = pd.to_datetime(data.pop("Year"), format="%Y", errors="coerce")
    data = data[1680 <= data.Date.dt.year]
    countries = """
        Afghanistan
        Argentina
        Australia
        Brazil
        China
        Congo
        Finland
        France
        Germany
        Greece
        India
        Indonesia
        Italy
        Japan
        Kenya
        Mexico
        Netherlands
        Niger
        Norway
        Russian Federation
        South Africa
        Spain
        Sweden
        Switzerland
        Turkey
        United Kingdom
        United States
    """
    countries = sorted(filter(None, set(c.strip() for c in countries.splitlines())))
    data = data[data.Country.isin(countries)]

    gdp_range = [64000 / (2 ** i) for i in range(10)][::-1]
    gdp_title = "GDP (US$)"

    width, height = 14, 8
    scale = 100

    country_selector = alt.selection_multi(
        fields=["Country"],
        bind="legend",
    )
    nearest_point_selector = alt.selection(
        fields=["Date", "Country"],
        type="single",
        on="mouseover",
        nearest=True,
    )
    base = alt.Chart(data).encode(
        alt.X(
            "Date",
            type="temporal",
            timeUnit="year",
            axis=alt.Axis(grid=True, labelAngle=0),
        ),
        alt.Y(
            "GDP",
            type="quantitative",
            axis=alt.Axis(grid=True, title=gdp_title, values=gdp_range),
            scale=alt.Scale(type="log", base=2),
        ),
        alt.Color(
            "Country",
            type="nominal",
            legend=alt.Legend(values=countries, symbolLimit=len(countries)),
        ),
        tooltip=[
            "Country",
            alt.Tooltip(field="Date", type="temporal", timeUnit="year"),
            alt.Tooltip(field="GDP", title=gdp_title, format=","),
        ],
    )
    points = (
        base.mark_point()
        .encode(
            size=alt.condition(
                ~nearest_point_selector,
                alt.value(4),
                alt.value(50),
            ),
        )
        .transform_filter(country_selector)
        .add_selection(country_selector)
        .add_selection(nearest_point_selector)
    )
    chart = points.properties(
        width=scale * width,
        height=scale * height,
    )
    chart = common.configure_altair_fonts(chart)
    return chart, data


def main():
    data = common.read_data(
        fn="read_csv",
        filename="historys-hockey-stick-gross-domestic-product-per-capita-using-the-ratio-scale-1990.csv",
    )
    chart, data = plot_growth(data)
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
