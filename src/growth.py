import sys

import pandas as pd
import altair as alt

alt.data_transformers.disable_max_rows()

import common


def plot_growth(data):
    data = data.rename(
        columns={
            "Real GDP per capita in 2011 US$": "GDP",
            "Entity": "Country",
        }
    )
    data.Year = data.Year.astype(int)
    data = data[data.Year > 1800]

    countries = [
        "Afghanistan",
        "Finland",
        "Sweden",
        "United States",
        "Japan",
        "Germany",
    ]
    data = data[data.Country.isin(countries)]

    font_config = dict(
        titleFontSize=16,
        labelFontSize=14,
        titleFont="Georgia",
        labelFont="Georgia",
    )
    width, height = 10, 6
    scale = 100

    lines = (
        alt.Chart(data)
        .mark_line()
        .encode(
            alt.X("Year", type="ordinal"),
            alt.Y("GDP", type="quantitative"),
            alt.Color("Country", type="nominal"),
        )
        .properties(width=scale * width, height=scale * height)
    )
    chart = lines.configure_view(strokeWidth=0)
    chart = common.configure_altair_fonts(chart, font_config)
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
