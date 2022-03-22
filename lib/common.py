import datetime
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
    context = dict(
        module_name=module_name(module),
        metadata=module_metadata(module),
        created_at=today(),
    )
    if chart:
        context["vega_spec"], context["vega_opt"] = altair_chart_to_json(chart)
    html = template.render(has_chart=bool(chart), **dict(context, **extra_context))
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


def eprint(*a, file=sys.stderr, **kw):
    print(*a, file=file, **kw)


def altair_chart_to_json(chart, renderer="canvas", actions=False, **opt):
    spec = chart.to_json()
    opt = dict(renderer=renderer, actions=actions, **opt)
    opt = json.dumps(opt)
    return spec, opt


def configure_altair_fonts(chart, **config):
    config = dict(
        titleFontSize=16,
        labelFontSize=14,
        titleFont="Georgia",
        labelFont="Georgia",
        **config,
    )
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


def altair_selector(*fields, **kwargs):
    return alt.selection(
        fields=fields,
        **dict(
            type="single",
            on="mouseover",
            clear="mouseout",
            nearest=True,
            empty="none",
            **kwargs,
        ),
    )
