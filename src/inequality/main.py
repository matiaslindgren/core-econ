import sys

import pandas as pd
from bokeh.embed import components
from bokeh.models import ColumnDataSource
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

    for year in (1980, 1990, 2014):
        plot = plot_inequality(data[data.Year == year])
        s, d = components(plot)
        scripts.append(s)
        divs.extend([f"<h2>{year}</h2>", d])

    print(common.render(name, scripts, divs))


if __name__ == "__main__":
    main(sys.argv[1])
