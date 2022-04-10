import altair as alt
import numpy as np
import pandas as pd

import common


def plot():
    hours = pd.DataFrame({"hours": np.linspace(0, 24, 200)})
    dh = hours.hours.diff()[1]
    linetypes = ["Final grade", "Average product", "Marginal product"]
    data = hours.merge(pd.DataFrame({"type": linetypes}), how="cross")

    A_input = common.altair_range_input(
        name="A",
        field="A",
        min=1,
        max=40,
        init=24,
    )
    alpha_input = common.altair_range_input(
        name="α",
        field="alpha",
        min=0.01,
        max=0.99,
        step=0.01,
        init=0.6,
    )
    max_grade_input = common.altair_range_input(
        name="Max grade",
        field="max_grade",
        min=0,
        max=100,
        init=90,
    )

    def f(h):
        h = alt.expr.max(0, h)
        y = A_input.A * h ** alpha_input.alpha
        return alt.expr.min(max_grade_input.max_grade, y)

    prod_func = f(alt.datum.hours)
    avg_prod = prod_func / alt.expr.max(1, alt.datum.hours)
    marginal_prod = (prod_func - f(alt.datum.hours - dh)) / dh

    lines = (
        alt.Chart(data)
        .mark_line(clip=True)
        .add_selection(A_input)
        .add_selection(alpha_input)
        .add_selection(max_grade_input)
        .transform_calculate(
            y=(alt.datum.type == "Final grade") * prod_func
            + (alt.datum.type == "Average product") * avg_prod
            + (alt.datum.type == "Marginal product") * marginal_prod,
        )
        .encode(
            x=alt.X(
                "hours:Q",
                title="Hours of study per day",
            ),
            y=alt.Y(
                "y:Q",
                title="Grade",
                scale=alt.Scale(domainMax=95),
            ),
            color=alt.Color(
                "type:N",
                title="Grade",
                sort=linetypes,
                legend=alt.Legend(title=None),
            ),
        )
    )
    hours_selector = common.altair_selector("hours")
    tooltip_points = (
        alt.Chart(data)
        .mark_point()
        .add_selection(hours_selector)
        .transform_calculate(calculate=prod_func, as_="Final grade")
        .transform_calculate(calculate=avg_prod, as_="Average product")
        .transform_calculate(calculate=marginal_prod, as_="Marginal product")
        .encode(
            x=lines.encoding.x,
            tooltip=[
                alt.Tooltip(f"{field}:Q", title=field.capitalize(), format=".1f")
                for field in ["hours", *linetypes]
            ],
            opacity=alt.value(0),
        )
    )
    hours_rule = (
        alt.Chart(data)
        .mark_rule(color="gray")
        .transform_filter(hours_selector)
        .encode(x=lines.encoding.x)
    )

    chart = lines + tooltip_points + hours_rule
    chart = chart.properties(
        width=600,
        height=400,
        title="Production function: input study hours, output final grade",
    )
    chart = common.configure_altair_fonts(chart)

    return chart, data


def main():
    chart, data = plot()
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
