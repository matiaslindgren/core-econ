import altair as alt
import pandas as pd

import common


def plot(persons=20):
    init = 100 // persons
    input_fieldnames = [f"person_{i}" for i in range(1, persons + 1)]
    inputs = {
        field: common.altair_range_input(name=field, field=field, min=0, max=100, init=init)
        for field in input_fieldnames
    }
    data = pd.DataFrame([{k: init for k in input_fieldnames}])

    lines = alt.Chart(data)
    for i in inputs.values():
        lines = lines.add_selection(i)
    lines = (
        lines.transform_calculate(**{field: i[field] for field, i in inputs.items()})
        .transform_fold(input_fieldnames, as_=["group", "income"])
        .mark_bar()
        .encode(
            x=alt.X(
                "group:N",
                title="people",
            ),
            y=alt.Y(
                "income:Q",
                title="income",
                scale=alt.Scale(domainMax=100),
            ),
        )
    )
    chart = lines.properties(
        width=600,
        height=400,
        title="wealth dist",
    )
    chart = common.configure_altair_fonts(chart)

    return chart, data


def main():
    chart, data = plot()
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
