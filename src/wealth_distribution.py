from types import SimpleNamespace
import random

import altair as alt
import numpy as np
import pandas as pd

import common


np_rng = np.random.default_rng(3)


def draw_from_pareto(shape, n):
    v = np_rng.pareto(shape, n)
    v /= v.sum()
    v = np.minimum(100, 100 * shape * v)
    return v.round(1)


def plot(population_size=20):
    # Create range input for each person and draw initial income from the Pareto distribution
    inputs = [
        SimpleNamespace(key=f"person_{p}", income=income)
        for p, income in enumerate(draw_from_pareto(3, population_size), start=1)
    ]
    for inp in sorted(inputs, key=lambda inp: inp.income):
        inp.alt_input = common.altair_range_input(
            name=inp.key,
            field=inp.key,
            min=0,
            max=100,
            step=0.1,
            init=inp.income,
        )

    # Base data, one income value for each person from each range input
    base = alt.Chart(pd.DataFrame([{inp.key: inp.income for inp in inputs}]))
    for inp in inputs:
        base = base.add_selection(inp.alt_input)
    # Insert range input values as data fields in wide form
    input_vars = {inp.key: 1.0 * inp.alt_input[inp.key] for inp in inputs}
    base = base.transform_calculate(**input_vars)
    # Fold into long form
    base = base.transform_fold(list(input_vars), as_=["group", "income"])

    cumulative_income_line = (
        base
        # Compute cumulative income and population shares
        .transform_window(
            sort=[{"field": "income"}],
            cumulative_income="sum(income)",
            row_number="row_number(income)",
            ignorePeers=True,
        )
        .transform_joinaggregate(
            total_income="sum(income)",
        )
        .transform_calculate(
            income_share=alt.datum.cumulative_income / alt.datum.total_income,
            population_share=(alt.datum.row_number - 1) / (population_size - 1),
        )
        # Compute Gini coefficient
        .transform_calculate(
            mean_abs_diff_self=sum(
                alt.expr.abs(alt.datum.income - alt.datum[other_income])
                for other_income in input_vars
            )
            / population_size,
        )
        .transform_joinaggregate(
            mean_abs_diff="mean(mean_abs_diff_self)",
            mean_income="mean(income)",
        )
        .transform_calculate(
            gini=alt.datum.mean_abs_diff / (2 * alt.datum.mean_income),
        )
        # .mark_point(size=50, tooltip={"content": "data"})
        # .encode(x="group:O", y="income:Q")
        .mark_area(line=True)
        .encode(
            x=alt.X(
                "population_share:Q",
                title="Cumulative share of population, ordered by income",
                axis=alt.Axis(format="%"),
                scale=alt.Scale(domainMin=0, domainMax=1),
            ),
            y=alt.Y(
                "income_share:Q",
                title="Cumulative share of income",
                axis=alt.Axis(format="%"),
                scale=alt.Scale(domainMin=0, domainMax=1),
            ),
            color=alt.Color(
                "gini:Q",
                scale=alt.Scale(scheme="reds", domainMin=0, domainMax=0.5),
            ),
            tooltip=[alt.Tooltip("gini:Q", title="Gini")],
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

    return chart


def main():
    print(common.render(__file__, chart=plot(), include_katex=True))


if __name__ == "__main__":
    main()
