import sys

import pandas as pd
import altair as alt

alt.data_transformers.disable_max_rows()

import common

DATA_URL = "https://raw.githubusercontent.com/jackblun/Globalinc/master/GCIPrawdata.csv"


def plot_income(data):
    data["Inequality"] = data["Decile 10 Income"] / data["Decile 1 Income"]
    data = data.melt(
        id_vars=["Country", "Year"],
        value_vars=[f"Decile {i} Income" for i in range(1, 11)],
        value_name="Income",
        var_name="Decile",
    )
    data.Decile = data.Decile.str.split(expand=True)[1].astype(int)
    data = data.reset_index()
    common.eprint(data.shape)

    width, height = 2, 16
    scale = 100

    slider = alt.binding_range(min=data.Year.min(), max=data.Year.max(), step=1)
    select_year = alt.selection_single(
        name="Year", fields=["Year"], bind=slider, init={"Year": data.Year.min()}
    )
    chart = (
        alt.Chart(data)
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
                    title="Income (USD)",
                    gradientLength=scale * width,
                    orient="top",
                    direction="horizontal",
                    titleAnchor="middle",
                ),
                scale=alt.Scale(
                    scheme="yellowgreen",
                    domainMin=data.Income.min(),
                    domainMax=data.Income.max(),
                ),
            ),
            tooltip=["Country", "Year", "Decile", "Income"],
        )
        .properties(width=scale * width, height=scale * height)
        .add_selection(select_year)
        .transform_filter(select_year)
        .configure_axis(grid=False)
        .configure_view(strokeWidth=0)
    )
    return common.altair_chart_to_html(chart)


def main(name):
    scripts = []
    divs = []
    divs.extend(
        [
            "<h1>Inequality as rich-to-poor ratio by GDP ($ PPP)</h1>",
            f"<b>{common.now()}</b>",
            "<br>",
        ]
    )
    data = common.read_csv(DATA_URL, header=2)
    html = plot_income(data)
    divs.append(html)
    print(common.render(name, scripts, divs))
    return data


if __name__ == "__main__":
    data = main(sys.argv[1])
