import datetime
import pathlib

import bs4
import jinja2
import pandas as pd

bokeh_version = "2.4.0"


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
    html = template.render(bokeh_version=bokeh_version, scripts=scripts, divs=divs)
    tree = bs4.BeautifulSoup(html, features="html.parser")
    return tree.prettify()


def read_csv(filename, **kwargs):
    csv_path = pathlib.Path(".").parent.joinpath("data", filename)
    return pd.read_csv(csv_path, **kwargs)
