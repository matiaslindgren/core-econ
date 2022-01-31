import datetime

import jinja2
import bs4

bokeh_version = "2.4.0"


def now_str():
    return datetime.datetime.now().strftime("%d. %B %Y")


def render(template, scripts, divs, template_dirs):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dirs + ["common"]),
        undefined=jinja2.StrictUndefined,
        cache_size=0,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template)
    html = template.render(bokeh_version=bokeh_version, scripts=scripts, divs=divs)
    tree = bs4.BeautifulSoup(html, features="html.parser")
    return tree.prettify()
