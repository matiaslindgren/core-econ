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
    data = data[1700 <= data.Date.dt.year]
    countries = """
        Afghanistan
        Argentina
        Australia
        Brazil
        China
        Congo
        Denmark
        Egypt
        Finland
        France
        Germany
        Greece
        India
        Indonesia
        Italy
        Japan
        Kenya
        Kuwait
        Mexico
        Mozambique
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
    nearest_line_selector = alt.selection(
        fields=["Country"],
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
    lines = (
        base.mark_point()
        .encode(
            size=alt.condition(
                ~nearest_line_selector,
                alt.value(2),
                alt.value(6),
            ),
        )
        .transform_filter(country_selector)
        .add_selection(country_selector)
        .add_selection(nearest_line_selector)
    )
    chart = lines.properties(
        width=scale * width,
        height=scale * height,
    )
    chart = common.configure_altair_fonts(chart)
    return common.altair_chart_to_html(chart)


def main():
    elements = common.header_elements(__file__)
    data = common.read_data(
        fn="read_csv",
        filename="historys-hockey-stick-gross-domestic-product-per-capita-using-the-ratio-scale-1990.csv",
    )
    html = plot_growth(data)
    elements.append(html)
    print(common.render(__file__, elements=elements))
    return data


if __name__ == "__main__":
    data = main()
