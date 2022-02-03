import sys
import textwrap
from math import pi

import pandas as pd
import altair as alt
from bokeh.embed import components
from bokeh.models import (
    ColumnDataSource,
    BasicTicker,
    ColorBar,
    LinearColorMapper,
    PrintfTickFormatter,
)
from bokeh.plotting import figure
from matplotlib import cm
from matplotlib.colors import rgb2hex

import common


def plot_income(data, year):
    low, high = data["Mean Income"].min(), data["Mean Income"].max()
    country_ord = {
        c: i for i, c in enumerate(data.sort_values("Mean Income").Country.unique())
    }
    data = data.melt(
        id_vars=["Country", "Year"],
        value_vars=[f"Decile {i} Income" for i in range(1, 11)],
        value_name="Income",
        var_name="Decile",
    )
    data.Decile = data.Decile.str.split(expand=True)[1].astype(int)
    data = data.set_index(["Country", "Year"])
    data = data.xs(year, level="Year")
    data = data.pivot(columns="Decile", values="Income")
    countries = sorted(data.index, key=country_ord.get)
    income_deciles = data.columns.astype(str).to_list()
    data = pd.DataFrame(data.stack(), columns=["Income"]).reset_index()

    cmap = cm.get_cmap("YlGn", len(income_deciles))
    colors = [rgb2hex(cmap(i)) for i in range(cmap.N)]
    mapper = LinearColorMapper(palette=colors, low=low, high=high)

    scale = 2
    font_px = 16
    rect_px = 20

    p = figure(
        title="income",
        x_range=income_deciles,
        y_range=countries,
        x_axis_location="above",
        height=len(countries) * rect_px,
        width=len(income_deciles) * rect_px,
        tools="hover",
        toolbar_location=None,
        tooltips=[("Country", "@Country"), ("Income", "@Income (@Decile. decile)")],
    )

    common.eprint(countries, income_deciles, p.width, p.height)
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.major_label_text_font_size = f"{font_px}px"
    p.axis.major_label_standoff = 0

    p.rect(
        x="Decile",
        y="Country",
        width=rect_px,
        height=rect_px,
        source=data,
        width_units="screen",
        height_units="screen",
        fill_color={"field": "Income", "transform": mapper},
        line_color=None,
    )

    # color_bar = ColorBar(
    #     color_mapper=mapper,
    #     major_label_text_font_size=f"{font_px}px",
    #     ticker=BasicTicker(desired_num_ticks=len(colors)),
    #     formatter=PrintfTickFormatter(format="{:,d}$"),
    #     label_standoff=6,
    #     border_line_color=None,
    # )
    # p.add_layout(color_bar, "above")

    return p


def plot_income_altair(data, year):
    data = data.melt(
        id_vars=["Country", "Year"],
        value_vars=[f"Decile {i} Income" for i in range(1, 11)],
        value_name="Income",
        var_name="Decile",
    )
    data.Decile = data.Decile.str.split(expand=True)[1].astype(int)
    data = data.set_index(["Country", "Year"])
    data = data.xs(year, level="Year")
    data = data.reset_index()
    plot = (
        alt.Chart(data)
        .mark_rect()
        .encode(x="Decile:O", y="Country:N", color="Income:Q")
        .properties(width=600)
    )
    html = f"""
        <div id="vis"></div>
        <script type="text/javascript">
          var spec = {plot.to_json()};
          var opt = {{"renderer": "canvas", "actions": false}};
          vegaEmbed("#vis", spec, opt);
        </script>
    """
    return textwrap.dedent(html)


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

    html = plot_income_altair(data, 1990)
    # plot = plot_income(data, 1990)
    # s, d = components(plot)
    # scripts.append(s)
    divs.append(html)
    print(common.render(name, scripts, divs))
    return data


if __name__ == "__main__":
    data = main(sys.argv[1])
