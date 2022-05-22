from types import SimpleNamespace

import altair as alt
import numpy as np
import pandas as pd

import common


def pluralize(name):
    # heuristic, definitely does not work with all nouns
    if name.endswith("y"):
        return name[:-1] + "ies"
    return name + "s"


def tooltip_from_encoding(e, format=None):
    return alt.Tooltip(
        field=e.field,
        type=e.type,
        title=e.title,
        format=format,
    )


def repr_latex(cost):
    x0, x1, x2 = [np.format_float_positional(x, min_digits=1) for x in cost.coef]
    return fr"\\text{{C}}(Q) := {x2} Q^2 + {x1} Q + {x0}"


def plot():
    firm_types = ["Smith", "Workshop", "Factory"]
    P = np.polynomial.Polynomial
    firm_costs = SimpleNamespace(
        Smith=P([2, 1, 0.5]),
        Workshop=P([30, 0.5, 0.01]),
        Factory=P([150, 0.001, 0.001]),
    )

    def get_cost(firm):
        return getattr(firm_costs, firm)

    quantity = np.linspace(0, 300, 301)
    data = pd.concat(
        (
            pd.DataFrame(
                {
                    "firm": firm,
                    "cost": get_cost(firm)(quantity),
                    "quantity": quantity,
                }
            )
            for firm in firm_types
        ),
        axis="rows",
    )

    cost_lines = (
        alt.Chart(data)
        .mark_line(clip=True)
        .encode(
            x=alt.X(
                "quantity:Q",
                title="Units produced",
            ),
            y=alt.Y(
                "cost:Q",
                title="Marginal cost",
                scale=alt.Scale(domainMin=0, domainMax=500),
            ),
            color=alt.Color(
                field="firm",
                type="nominal",
                title="Firm",
                sort=firm_types,
            ),
        )
    )
    quantity_selector = common.altair_selector("quantity")
    tooltip_points = (
        alt.Chart(data.pivot(index="quantity", columns="firm", values="cost").reset_index())
        .mark_point()
        .add_selection(quantity_selector)
        .encode(
            x=cost_lines.encoding.x,
            tooltip=[
                alt.Tooltip("quantity:Q", title="Units produced"),
                *[alt.Tooltip(f"{f}:Q", format=".1f") for f in firm_types],
            ],
            opacity=alt.value(0),
        )
    )
    quantity_rule = (
        alt.Chart(data)
        .mark_rule(color="gray")
        .transform_filter(quantity_selector)
        .encode(x=cost_lines.encoding.x)
    )
    chart_top = cost_lines + tooltip_points + quantity_rule

    inputs = SimpleNamespace(
        **{
            f: common.altair_range_input(
                name=pluralize(f),
                field=f"{f}_count",
                min=0,
                max=max,
                init=init,
            )
            for f, max, init in zip(firm_types, [100, 50, 10], [50, 10, 1])
        }
    )

    def get_input(firm):
        return getattr(getattr(inputs, firm), f"{firm}_count")

    def market_cost():
        counts = [get_input(f) for f in firm_types]
        costs = [get_cost(f) for f in firm_types]
        s0 = sum(count / cost.coef[0] for count, cost in zip(counts, costs))
        s1 = sum(count / cost.coef[1] for count, cost in zip(counts, costs))
        q = alt.datum.total_quantity
        min_cost = min(c.coef[0] for c in costs)
        return min_cost + (s0 / s1) * q + (2 / s1) * alt.expr.pow(q, 2)

    data_total = data.assign(total_quantity=data.quantity)
    market_supply_line = (
        alt.Chart(data_total)
        .mark_line(clip=True)
        .add_selection(inputs.Smith)
        .add_selection(inputs.Workshop)
        .add_selection(inputs.Factory)
        .transform_calculate(market_cost=market_cost())
        .encode(
            x=alt.X(
                field="total_quantity",
                type="quantitative",
                title="Units produced in total",
            ),
            y=alt.Y(
                field="market_cost",
                type="quantitative",
                title="Market marginal cost",
            ),
        )
    )
    total_quantity_selector = common.altair_selector("total_quantity")
    tooltip_points = (
        alt.Chart(data_total)
        .mark_point()
        .add_selection(total_quantity_selector)
        .transform_calculate(market_cost=market_cost())
        .encode(
            x=market_supply_line.encoding.x,
            tooltip=[
                tooltip_from_encoding(getattr(market_supply_line.encoding, x), ",.0f") for x in "xy"
            ],
            opacity=alt.value(0),
        )
    )
    total_quantity_rule = (
        alt.Chart(data_total)
        .mark_rule(color="gray")
        .transform_filter(total_quantity_selector)
        .encode(x=market_supply_line.encoding.x)
    )
    market_supply_line += tooltip_points + total_quantity_rule

    def firm_output(firm):
        cost = get_cost(firm)
        x0, x1 = cost.deriv().coef
        count = get_input(firm)
        p = alt.datum.price
        min_cost = cost.coef[0]
        return (p >= min_cost) * count * (p - x0) / x1

    total_output = sum(map(firm_output, firm_types))
    market_outputs = [(alt.datum.firm == f) * firm_output(f) for f in firm_types]
    market_shares = [
        output / alt.expr.max(1, total_output) for f, output in zip(firm_types, market_outputs)
    ]

    df_prices = pd.DataFrame({"price": np.linspace(0, 500)})
    df_firm_types = pd.DataFrame({"firm": firm_types})
    data_shares = df_prices.merge(df_firm_types, how="cross")
    market_output_area = (
        alt.Chart(data_shares)
        .mark_area()
        .transform_calculate(
            market_output=sum(market_outputs),
            market_share=sum(market_shares),
        )
        .encode(
            x=alt.X("price:Q", title="Price per unit"),
            y=alt.Y(
                "market_output:Q",
                title="Units produced",
                stack="zero",
            ),
            color=cost_lines.encoding.color,
            tooltip=[
                alt.Tooltip("price:Q", title="Price per unit", format=",.0f"),
                alt.Tooltip("market_output:Q", title="Units produced", format=",.0f"),
                alt.Tooltip("market_share:Q", title="Market share", format=".0%"),
                alt.Tooltip("firm:N", title="Firm"),
            ],
        )
    )

    chart = chart_top.properties(
        width=850,
        height=300,
        title="Cost per produced unit of goods by firm type",
    )
    market_supply_line = market_supply_line.properties(
        width=850,
        title="Total production cost",
    )
    market_output_area = market_output_area.properties(
        width=850,
        title="Market shares",
    )
    chart &= market_supply_line & market_output_area
    chart = common.configure_altair_fonts(chart)

    return chart, firm_costs, locals()


def main():
    chart, firm_costs, l = plot()
    html = common.render(
        __file__,
        chart=chart,
        include_katex=True,
        firm_costs={f: repr_latex(p) for f, p in firm_costs.__dict__.items()},
    )
    print(html)
    return l


if __name__ == "__main__":
    locals().update(main())
