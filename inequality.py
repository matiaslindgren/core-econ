import pandas as pd

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.embed import components

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


if __name__ == "__main__":
    scripts = []
    divs = []

    now = common.now_str()
    divs.extend(
        [
            "<h1>Inequality as rich-to-poor ratio by GDP ($ PPP)</h1>",
            f"<b>{now}</b>",
        ]
    )

    data = pd.read_csv("data/GCIPrawdata.csv", header=2)
    data["Inequality"] = data["Decile 10 Income"] / data["Decile 1 Income"]

    for year in (1980, 1990, 2014):
        plot = plot_inequality(data[data.Year == year])
        s, d = components(plot)
        scripts.append(s)
        divs.append(f"<h2>{year}</h2>")
        divs.append(d)

    with open("out.html", "w") as f:
        print(common.render("inequality.j2", scripts, divs, ["."]), file=f)
