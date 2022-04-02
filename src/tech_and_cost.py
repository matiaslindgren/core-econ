from collections import namedtuple
import sys
import math

import altair as alt
import numpy as np
import pandas as pd

alt.data_transformers.disable_max_rows()

import common


def plot(data):
    wage_input = common.altair_range_input(
        name="Wages",
        field="wage",
        init=10,
        min=5,
        max=40,
    )
    coal_cost_input = common.altair_range_input(
        name="Coal cost",
        field="coal_cost",
        init=20,
        min=5,
        max=40,
    )
    tech_cost = (
        wage_input.wage * alt.datum.workers_required
        + coal_cost_input.coal_cost * alt.datum.coal_required
    )
    lines = (
        alt.Chart(data.merge(pd.DataFrame({"n": [0, 1]}), how="cross"))
        .mark_line(clip=True)
        .add_selection(wage_input)
        .add_selection(coal_cost_input)
        .transform_calculate(
            y_coal=alt.datum.n * tech_cost / coal_cost_input.coal_cost,
            x_workers=(1 - alt.datum.n) * tech_cost / wage_input.wage,
        )
        .encode(
            x=alt.X(
                "x_workers:Q",
                axis=alt.Axis(title="Number of workers"),
                scale=alt.Scale(domain=[0, 20]),
            ),
            y=alt.Y(
                "y_coal:Q",
                axis=alt.Axis(title="Tonnes of coal"),
                scale=alt.Scale(domain=[0, 20]),
            ),
            color=alt.Color("tech_name:N", legend=alt.Legend(title="Technology")),
        )
    )
    points = (
        alt.Chart(data)
        .mark_point()
        .transform_calculate(tech_cost=tech_cost)
        .encode(
            x="workers_required:Q",
            y="coal_required:Q",
            color=alt.Color("tech_name:N", legend=None),
            size=alt.value(60),
            tooltip=[
                alt.Tooltip("tech_name:N", title="Technology"),
                alt.Tooltip("workers_required:Q", title="Workers required"),
                alt.Tooltip("coal_required:Q", title="Tonnes of coal required"),
                alt.Tooltip("tech_cost:Q", title="Production cost"),
            ],
        )
    )
    labels = (
        alt.Chart(data)
        .mark_text(align="center", baseline="bottom", dy=-5)
        .encode(
            x="workers_required:Q",
            y="coal_required:Q",
            text="tech_name:N",
        )
    )
    chart = lines + points + labels
    chart = chart.properties(
        title="Total cost of producing 100 metres of cloth",
        width="container",
        height=600,
    )
    chart = common.configure_altair_fonts(chart)
    return chart, data


def main():
    data = common.read_data(
        fn="read_csv",
        filename="tech_and_cost.csv",
    )
    chart, data = plot(data)
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
