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
    if path.exists() and (content := path.read_text()):
        meta.update(yaml.safe_load(content))
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
        "updated_at": today(),
        "chart": None,
        "include_katex": False,
    }
    if chart:
        context["chart"] = altair_chart_to_json(chart)
    return template.render(**(context | extra_context))


memory = joblib.Memory(pathlib.Path(".").joinpath("cache"), verbose=1)


@memory.cache
def download_data(url, **kwargs):
    eprint(f"downloading url {url}")
    return pd.read_csv(url, **kwargs)


def read_data(filename, **kwargs):
    csv_path = pathlib.Path(".").parent.joinpath("data", filename)
    return pd.read_csv(csv_path, **kwargs)


eprint = functools.partial(print, file=sys.stderr)


def altair_chart_to_json(chart, renderer="canvas", actions=False, **options):
    options = {"renderer": renderer, "actions": actions} | options
    return {"spec": chart.to_json(), "options": json.dumps(options)}


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


def altair_replace(obj, **values):
    obj = obj.copy()
    for k, v in values.items():
        obj[k] = v
    return obj


def reindex_multiple_columns(data, *index_columns, **reindex_kw):
    index_values = (data[col].dropna().unique() for col in index_columns)
    index = pd.MultiIndex.from_product(index_values, names=index_columns)
    return data.set_index(index.names).reindex(index, **reindex_kw)


def tooltip_from_encoding(e, title):
    t = alt.Tooltip(
        field=e.field,
        type=e.type,
        title=e.axis.title or title,
    )
    if hasattr(e, "timeUnit"):
        t.timeUnit = e.timeUnit
    return t
