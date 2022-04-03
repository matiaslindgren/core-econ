import datetime
import functools
import io
import json
import pathlib
import sys

import altair as alt
import bs4
import jinja2
import joblib
import pandas as pd
import requests
import yaml

memory = joblib.Memory(pathlib.Path(".").joinpath("cache"), verbose=0)


def module_name(file):
    return pathlib.Path(file).stem


def module_metadata(file):
    meta = dict.fromkeys(
        [
            "title",
            "desc",
            "src",
            "url",
            "url_name",
            "chapter",
            "chapter_url",
        ]
    )
    path = pathlib.Path("metadata").joinpath(module_name(file)).with_suffix(".yaml")
    if path.exists():
        meta.update(yaml.safe_load(path.read_text()))
    return meta


def today():
    return datetime.datetime.now().strftime("%d. %B %Y")


def render(module, chart=None, **extra_context):
    rootdir = pathlib.Path(".").parent
    template_dirs = [
        rootdir.joinpath("lib"),
        rootdir.joinpath("src"),
    ]
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dirs),
        undefined=jinja2.StrictUndefined,
        cache_size=0,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.select_template([f"{module_name(module)}.j2", "base.j2"])
    context = {
        "module_name": module_name(module),
        "metadata": module_metadata(module),
        "created_at": today(),
        "has_chart": False,
        "custom_tooltip": False,
    }
    if chart:
        context["vega_spec"], context["vega_opt"] = altair_chart_to_json(chart)
        context["has_chart"] = True
    html = template.render(**(context | extra_context))
    tree = bs4.BeautifulSoup(html, features="html.parser")
    return tree.prettify()


@memory.cache
def read_data(fn, url=None, filename=None, **kwargs):
    if url:
        eprint(f"downloading {url}")
        return getattr(pd, fn)(url, **kwargs)
    if filename:
        csv_path = pathlib.Path(".").parent.joinpath("data", filename)
        return getattr(pd, fn)(csv_path, **kwargs)


eprint = functools.partial(print, file=sys.stderr)


def altair_chart_to_json(chart, **options):
    spec = chart.to_json()
    default_options = {"renderer": "canvas", "actions": False}
    return spec, json.dumps(default_options | options)


def configure_altair_fonts(chart, **config):
    default_config = {
        "titleFontSize": 16,
        "labelFontSize": 14,
        "titleFont": "Georgia",
        "labelFont": "Georgia",
    }
    config = default_config | config
    title_config = {}
    if "titleFontSize" in config:
        title_config["fontSize"] = config["titleFontSize"]
    if "titleFont" in config:
        title_config["font"] = config["titleFont"]
    return (
        chart.configure_axis(**config)
        .configure_legend(**config)
        .configure_header(**config)
        .configure_title(**title_config)
    )


def altair_selector(
    *fields,
    type="single",
    on="mouseover",
    clear="mouseout",
    nearest=True,
    empty="none",
    **kwargs,
):
    return alt.selection(
        fields=fields,
        type=type,
        on=on,
        clear=clear,
        nearest=nearest,
        empty=empty,
        **kwargs,
    )


def altair_range_input(*, field, init, name=None, min=1, max=100, step=1):
    return alt.selection_single(
        fields=[field],
        bind=alt.binding_range(
            min=min,
            max=max,
            step=step,
            name=f"{name or field}:",
        ),
        init={field: init},
    )
