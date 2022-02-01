import sys
from math import pi

import pandas as pd
from bokeh.embed import components
import bokeh.palettes
from bokeh.models import (
    ColumnDataSource,
    BasicTicker,
    ColorBar,
    LinearColorMapper,
    PrintfTickFormatter,
)
from bokeh.plotting import figure

import common


def plot_inequality(data):
    data = data[["Country", "Inequality"]].copy().dropna().sort_values("Inequality")
    data.Inequality = data.Inequality.round(1).apply("{:.1f}".format)
    data.Country = data.Country.astype(str)
    plot = figure(
        width=1000,
        height=2000,
        toolbar_location=None,
        y_range=data.Country,
        tooltips=[("Inequality", "@Inequality"), ("Country", "@Country")],
    )
    plot.hbar(
        y="Country",
        right="Inequality",
        source=ColumnDataSource(data),
        height=2 / 3,
    )
    plot.ygrid.grid_line_color = None
    plot.outline_line_color = None
    return plot


def plot_income(data):
    data = data.melt(
        id_vars=["Country", "Year"],
        value_vars=[f"Decile {i} Income" for i in range(1, 11)],
        value_name="Income",
        var_name="Decile",
    )
    data.Decile = data.Decile.str.split(expand=True)[1].astype(int)
    data = data.set_index(["Country", "Year"])
    data = data.xs(1985, level="Year")
    data = data.pivot(columns="Decile", values="Income")

    countries = data.index.to_list()
    income_deciles = data.columns.astype(str).to_list()

    common.eprint(data)
    data = pd.DataFrame(data.stack(), columns=["Income"]).reset_index()

    colors = bokeh.palettes.YlGn[9][::-1]
    mapper = LinearColorMapper(
        palette=colors, low=data.Income.min(), high=data.Income.max()
    )

    TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

    common.eprint(countries, income_deciles)

    p = figure(
        title="income",
        y_range=countries,
        x_range=income_deciles,
        x_axis_location="above",
        height=3000,
        width=1200,
        tools=TOOLS,
        toolbar_location="below",
        tooltips=[("Country", "@Country"), ("Income", "@Income (@Decile. decile)")],
    )

    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = "24px"

    p.rect(
        y="Country",
        x="Decile",
        width=1,
        height=1,
        source=data,
        fill_color={"field": "Income", "transform": mapper},
        line_color=None,
    )

    color_bar = ColorBar(
        color_mapper=mapper,
        major_label_text_font_size="24px",
        ticker=BasicTicker(desired_num_ticks=len(colors)),
        formatter=PrintfTickFormatter(format="%d"),
        label_standoff=6,
        border_line_color=None,
    )
    p.add_layout(color_bar, "right")
    return p


def main(name):
    scripts = []
    divs = []
    divs.extend(
        [
            "<h1>Inequality as rich-to-poor ratio by GDP ($ PPP)</h1>",
            f"<b>{common.now()}</b>",
        ]
    )
    data = common.read_csv("GCIPrawdata.csv", header=2)
    data["Inequality"] = data["Decile 10 Income"] / data["Decile 1 Income"]

    # for year in (1980, 1990, 2014):
    #     plot = plot_inequality(data[data.Year == year])
    #     s, d = components(plot)
    #     scripts.append(s)
    #     divs.extend([f"<h2>{year}</h2>", d])

    plot = plot_income(data)
    s, d = components(plot)
    scripts.append(s)
    divs.append(d)
    print(common.render(name, scripts, divs))
    return data


if __name__ == "__main__":
    data = main(sys.argv[1])
