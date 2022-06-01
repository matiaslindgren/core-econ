import sys
from types import SimpleNamespace

import altair as alt
import pandas as pd

alt.data_transformers.disable_max_rows()

import common


translate = SimpleNamespace(
    location={
        "FIN": "Finland",
        "SWE": "Sweden",
        "NOR": "Norway",
    },
    indicator={
        "REALGDPFORECAST": "Real gross domestic product growth rate (%)",
        "HHDI": "Household disposable income US$ per capita yearly change (%)",
        "HUR": "Unemployment rate (% of labour force)",
        "CPI": "Inflation growth rate (%)",
        "LTINT": "Long-term interest rate (%)",
        "STINT": "Short-term interest rate (%)",
    },
)


def read_csv(name, measure, subject="TOT"):
    data = common.read_data(f"oecd_{name}.csv")
    data = data.loc[
        (
            data.LOCATION.isin(translate.location)
            & (data.FREQUENCY == "A")
            & (data.SUBJECT == subject)
            & (data.MEASURE == measure)
        ),
        ["LOCATION", "INDICATOR", "TIME", "Value"],
    ]
    data["country"] = data.pop("LOCATION").map(translate.location.get)
    data["date"] = pd.to_datetime(data.pop("TIME"), format="%Y", errors="coerce")
    data["indicator"] = data.pop("INDICATOR")
    data["value"] = data.pop("Value")
    if measure.startswith("PC_") or measure == "AGRWTH":
        data.value = data.value / 100
    if name == "disposable_income":
        data.value = data.value.pct_change()
    return data


def get_data():
    data = pd.concat(
        [
            read_csv("gdp", measure="AGRWTH"),
            read_csv("disposable_income", measure="USD_CAP", subject="GROSSADJ"),
            read_csv("unemployment", measure="PC_LF"),
            read_csv("cpi", measure="AGRWTH"),
            read_csv("long_term_interest_rates", measure="PC_PA"),
            read_csv("short_term_interest_rates", measure="PC_PA"),
        ],
        axis="rows",
    )
    earliest_common_date = data.groupby(["country", "indicator"]).date.min().max()
    data = data[(data.date >= earliest_common_date) & (data.date.dt.year <= 2021)]
    data = data.pivot(index=["country", "date"], columns="indicator", values="value")
    data = data.reset_index()
    return data


def plot(data):
    nearest_date_selector = common.altair_selector("date")
    chart_base = alt.Chart(data).encode(
        x=alt.X(
            field="date",
            type="temporal",
            timeUnit="year",
            axis=alt.Axis(title=None, grid=True),
        ),
    )
    countries = list(translate.location.values())

    def plot_lines(indicator, title, format=".1%"):
        lines = chart_base.mark_line().encode(
            y=alt.Y(
                field=indicator,
                type="quantitative",
                axis=alt.Axis(title=None, format=format),
            ),
            color=alt.Color(
                field="country",
                type="nominal",
                sort=countries,
                legend=alt.Legend(title="Country"),
            ),
        )
        tooltip_rule = (
            chart_base.transform_pivot(
                "country",
                value=indicator,
                groupby=["date"],
            )
            .transform_calculate(Indicator=repr(title))
            .mark_rule(color="gray")
            .encode(
                opacity=alt.condition(
                    nearest_date_selector,
                    alt.value(1),
                    alt.value(0),
                ),
                tooltip=[
                    alt.Tooltip("Indicator", type="nominal"),
                    common.tooltip_from_encoding(chart_base.encoding.x, title="Year"),
                    *[alt.Tooltip(c, type="quantitative", format=format) for c in countries],
                ],
            )
            .add_selection(nearest_date_selector)
        )
        chart = lines + tooltip_rule
        chart = chart.properties(
            title=title,
            width="container",
            height=200,
        )
        return chart

    chart = alt.vconcat(
        *[plot_lines(indicator, title) for indicator, title in translate.indicator.items()],
    )
    chart = common.configure_altair_fonts(chart)
    return chart


def main():
    data = get_data()
    chart = plot(data)
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
