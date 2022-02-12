import sys

import common


def main(modules):
    elements = [
        f"<h1>core-econ scribbles</h1>",
        f"<b>{common.today()}</b>",
        "<br>",
    ]
    print(common.render(__file__, elements=elements, modules=modules))


if __name__ == "__main__":
    main(sys.argv[1:])
