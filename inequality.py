import pandas as pd
import numpy as np
import mistune


data = pd.read_csv("data/GCIPrawdata.csv", header=2)
data["Inequality"] = data["Decile 10 Income"] / data["Decile 1 Income"]

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.embed import components


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


def render(scripts, divs):
    return "\n".join(
        [
            "<html>",
            "<head>",
            '<meta charset="utf-8">',
            "\n".join(scripts),
            "</head>",
            "<body>",
            "\n".join(divs),
            "</body>",
            "</html>",
        ]
    )


if __name__ == "__main__":
    scripts = [
        '<script src="https://cdn.bokeh.org/bokeh/release/bokeh-2.4.0.min.js" crossorigin="anonymous"></script>',
        '<script src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.4.0.min.js" crossorigin="anonymous"></script>',
        '<script src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.4.0.min.js" crossorigin="anonymous"></script>',
        '<script src="https://cdn.bokeh.org/bokeh/release/bokeh-gl-2.4.0.min.js" crossorigin="anonymous"></script>',
        '<script src="https://cdn.bokeh.org/bokeh/release/bokeh-mathjax-2.4.0.min.js" crossorigin="anonymous"></script>',
    ]
    divs = []

    for year in (1980, 1990, 2014):
        plot = plot_inequality(data[data.Year == year])
        s, d = components(plot)
        scripts.append(s)
        divs.append(d)

    with open("out.html", "w") as f:
        print(render(scripts, divs), file=f)
