import altair as alt
import numpy as np
import pandas as pd

import common


def plot():
    y = [0, 20, 33, 42, 50, 57, 63, 69, 74, 78, 81, 84, 86, 88, 89, 90]
    y = np.array(y + 9 * [y[-1]])
    x = np.arange(len(y))
    ap = np.concatenate(([0], y[1:] / x[1:]))
    mp = np.diff(y, prepend=[0])
    data = pd.concat(
        [
            pd.DataFrame({"x": x, "y": y, "grade": "final"}),
            pd.DataFrame({"x": x, "y": ap, "grade": "average"}),
            pd.DataFrame({"x": x, "y": mp, "grade": "marginal"}),
        ]
    )

    grade_lines = (
        alt.Chart(data)
        .mark_line()
        .encode(
            x=alt.X(
                "x:Q",
                title="Hours of study per day",
            ),
            y=alt.Y(
                "y:Q",
                title="Grade",
                scale=alt.Scale(domainMin=0, domainMax=95),
            ),
            color="grade:N",
        )
    )

    x_selector = common.altair_selector("x")
    tooltip_points = (
        alt.Chart(data.pivot(index="x", columns="grade", values="y").reset_index())
        .mark_point()
        .add_selection(x_selector)
        .encode(
            x="x:Q",
            y="final:Q",
            opacity=alt.value(0),
            tooltip=[
                alt.Tooltip("x:Q", title=grade_lines.encoding.x.title),
                alt.Tooltip("final:Q", title="Final grade", format=".1f"),
                alt.Tooltip("average:Q", title="Average product", format=".1f"),
                alt.Tooltip("marginal:Q", title="Marginal product", format=".1f"),
            ],
        )
    )
    xy = pd.DataFrame({"x": x, "y": y})
    vertical_rules = (
        alt.Chart(xy)
        .mark_rule(color="gray", strokeDash=[4, 2])
        .encode(
            y="y:Q",
            x="x:Q",
            x2=alt.value(0),
            opacity=alt.condition(x_selector, alt.value(1), alt.value(0)),
        )
    )
    horizontal_rules = (
        alt.Chart(xy)
        .mark_rule(color="gray", strokeDash=[4, 2])
        .encode(
            x="x:Q",
            y="y:Q",
            opacity=alt.condition(x_selector, alt.value(1), alt.value(0)),
        )
    )

    chart = grade_lines + tooltip_points + vertical_rules + horizontal_rules
    chart = chart.properties(width=600, height=400)
    chart = common.configure_altair_fonts(chart)

    return chart, data


def main():
    chart, data = plot()
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
