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


def now():
    return datetime.datetime.now().strftime("%d. %B %Y")


def render(name, scripts, divs):
    rootdir = pathlib.Path(".").parent
    template_dirs = [
        rootdir.joinpath("lib"),
        rootdir.joinpath("src", name),
    ]
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dirs),
        undefined=jinja2.StrictUndefined,
        cache_size=0,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("main.j2")
    html = template.render(scripts=scripts, divs=divs)
    tree = bs4.BeautifulSoup(html, features="html.parser")
    return tree.prettify()


@memory.cache
def read_csv(url, **kwargs):
    if url.startswith("http"):
        eprint(f"downloading {url}")
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        assert (
            res.encoding == "utf-8"
        ), f"unexpected encoding {res.encoding} in response from GET to {url}"
        return pd.read_csv(io.StringIO(res.text), **kwargs)
    csv_path = pathlib.Path(".").parent.joinpath("data", filename)
    return pd.read_csv(csv_path, **kwargs)


def eprint(*a, file=sys.stderr, **kw):
    print(*a, file=file, **kw)


def altair_chart_to_html(chart, renderer="canvas", actions=False, **opt):
    spec = chart.to_json()
    opt = dict(renderer=renderer, actions=actions, **opt)
    opt = json.dumps(opt)
    html = f"""
        <div id="vis"></div>
        <script type="text/javascript">
          var spec = {spec};
          var opt = {opt};
          vegaEmbed("#vis", spec, opt).then(() => {{
              const bindings = document.querySelector("#vis.vega-embed form.vega-bindings");
              const canvas = document.querySelector("#vis.vega-embed canvas");
              canvas.parentNode.insertBefore(bindings, canvas);
          }});
        </script>
    """
    return textwrap.dedent(html)
