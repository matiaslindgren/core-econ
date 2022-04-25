import random

import altair as alt
import numpy as np
import pandas as pd

import common


def draw_pareto(shape, n):
    v = np.random.pareto(shape, n)
    v = (100 / v.sum()) * v
    v = v.round(1)
    return v


def plot(persons=20):
    init_income = draw_pareto(3, persons)
    input_fieldnames = [(f"person_{p}", init_income[p - 1]) for p in range(1, persons + 1)]
    input_fieldnames.sort(key=lambda x: x[1])
    inputs = {
        field: common.altair_range_input(
            name=field,
            field=field,
            min=0,
            max=100,
            step=0.1,
            init=init,
        )
        for field, init in input_fieldnames
    }
    data = pd.DataFrame([{k: init for k, init in [("person_0", 0), *input_fieldnames]}])

    base = alt.Chart(data)
    for input in inputs.values():
        base = base.add_selection(input)

    cumulative_income_line = (
        base.transform_calculate(
            **{field: 1.0 * input[field] for field, input in inputs.items()},
        )
        .transform_fold(
            [k for k, _ in input_fieldnames],
            as_=["group", "income"],
        )
        .transform_window(
            sort=[{"field": "income"}],
            cumulative_income="sum(income)",
            order="row_number(income)",
            ignorePeers=True,
        )
        .transform_joinaggregate(total_income="sum(income)")
        .transform_calculate(
            income_share=alt.datum.cumulative_income / alt.datum.total_income,
            order_p=alt.datum.order / 20,
        )
        .mark_line()
        .encode(
            x=alt.X(
                "order_p:Q",
                title="Cumulative share of population, ordered by income",
                axis=alt.Axis(format="%"),
            ),
            y=alt.Y(
                "income_share:Q",
                title="Cumulative share of income",
                axis=alt.Axis(format="%"),
                scale=alt.Scale(domainMin=0, domainMax=1),
            ),
        )
    )

    perfect_equality_line = (
        alt.Chart(pd.DataFrame({"x": [0, 1], "y": [0, 1]}))
        .mark_line(color="gray")
        .encode(
            x="x:Q",
            y="y:Q",
        )
    )

    chart = cumulative_income_line + perfect_equality_line
    chart = chart.properties(width=600, height=600, title="Distribution of wealth ownership")
    chart = common.configure_altair_fonts(chart)

    return chart, data


def main():
    chart, data = plot()
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
