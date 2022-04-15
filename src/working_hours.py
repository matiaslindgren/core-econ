import sys
import math

import altair as alt
import pandas as pd

import common


def plot(hours, wages, begin_year=1992):
    assert (hours.pop("Unit") == "Hours").all()
    assert (wages.pop("Unit") == "US Dollar").all()
    assert (wages.pop("Reference Period") == 2020).all()

    columns = {"Country": "country", "Time": "year"}
    hours = hours.rename(columns=columns | {"Value": "hours"})
    wages = wages.rename(columns=columns | {"Value": "wages"})

    hours = hours[hours.year >= begin_year]
    hours = hours[hours.pop("Employment status") == "Total employment"]
    countries = [
        "Finland",
        "Sweden",
        "Denmark",
        "Norway",
        "Iceland",
        "Germany",
        "France",
        "United Kingdom",
        "United States",
        "Japan",
    ]
    hours = hours[hours.country.isin(countries)]

    data = wages.merge(hours, how="inner", on=["country", "year"])
    data["wage_per_hour"] = data.wages / data.hours
    data.year = pd.to_datetime(data.year, format="%Y")
    data = pd.melt(
        data,
        id_vars=["country", "year"],
        value_vars=["wages", "hours", "wage_per_hour"],
        var_name="datatype",
    )
    assert not data.isna().any().any()

    def make_chart(datatype, axis_title):
        chart_data = data[data.datatype == datatype]
        line_base = alt.Chart(chart_data)
        line = line_base.mark_line().encode(
            x=alt.X(
                "year",
                title="Year",
                type="temporal",
                timeUnit="year",
                axis=alt.Axis(
                    grid=True,
                    labelAngle=0,
                    format="%Y",
                    formatType="time",
                ),
            ),
            y=alt.Y(
                "value",
                type="quantitative",
                axis=alt.Axis(grid=True, title=axis_title),
                scale=alt.Scale(domainMin=0.9 * chart_data.value.min()),
            ),
            color=alt.Color(
                "country",
                type="nominal",
                legend=None,
                sort=countries,
            ),
        )
        year_selector = common.altair_selector("year")
        year_rule = (
            line_base.mark_rule(color="gray")
            .encode(x=line.encoding.x)
            .transform_filter(year_selector)
        )
        tooltip_points = (
            alt.Chart(
                chart_data.pivot(
                    index=["year", "datatype"],
                    columns="country",
                    values="value",
                ).reset_index()
            )
            .mark_point()
            .encode(
                x=line.encoding.x,
                opacity=alt.value(0),
                tooltip=[
                    alt.Tooltip("datatype"),
                    alt.Tooltip(
                        field="year",
                        title="title",
                        format="%Y",
                        formatType="time",
                    ),
                    *countries,
                ],
            )
            .add_selection(year_selector)
        )
        chart = alt.layer(
            line,
            year_rule,
            tooltip_points,
        )
        chart = chart.properties(width="container", height=400)
        return chart

    chart = alt.vconcat(
        make_chart("hours", "Average worked hours"),
        make_chart("wages", "Average annual wages (2020 USD PPP)"),
        make_chart("wage_per_hour", "Average hourly wages"),
        usermeta={
            "customTooltip": {
                "formatter": {
                    "hours": {"name": "hour", "digits": 4},
                    "wages": {"name": "USD", "digits": 4},
                    "wage_per_hour": {"name": "USD", "digits": 3},
                }
            }
        },
    )
    chart = common.configure_altair_fonts(chart)

    return chart, data


def main():
    hours = common.read_data(
        fn="read_csv",
        filename="ANHRS_15042022120521493.csv",
        usecols=["Country", "Time", "Value", "Unit", "Employment status"],
    )
    wages = common.read_data(
        fn="read_csv",
        filename="AV_AN_WAGE_15042022122047196.csv",
        usecols=["Country", "Time", "Value", "Unit", "Reference Period"],
    )
    chart, data = plot(hours, wages)
    print(common.render(__file__, chart=chart))
    return data


if __name__ == "__main__":
    data = main()
