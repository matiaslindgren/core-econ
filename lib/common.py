import datetime
import io
import json
import pathlib
import sys
import textwrap

import bs4
import jinja2
import joblib
import pandas as pd
import requests

memory = joblib.Memory(pathlib.Path(".").joinpath("cache"), verbose=0)


def module_name(file):
    return pathlib.Path(file).stem


def header_elements(file):
    return [
        "<a href='index.html'>go back</a>",
        f"<h1>{module_name(file).capitalize()}</h1>",
        f"<b>{today()}</b>",
        "<br>",
    ]


def today():
    return datetime.datetime.now().strftime("%d. %B %Y")


def render(module, elements=(), scripts=(), **context):
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
    template = env.get_template(f"{module_name(module)}.j2")
    html = template.render(scripts=scripts, elements=elements, **context)
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


def altair_chart_to_html(chart, renderer="canvas", actions=False, **opt):
    spec = chart.to_json()
    opt = dict(renderer=renderer, actions=actions, **opt)
    opt = json.dumps(opt)
    html = f"""
        <script type="application/json" id="vega-data-spec">
          {spec}
        </script>
        <script type="application/json" id="vega-data-options">
          {opt}
        </script>
    """
    return textwrap.dedent(html)


def configure_altair_fonts(chart, config):
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
