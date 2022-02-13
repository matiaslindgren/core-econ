import sys

import common


def main(modules):
    modules = {m: common.module_metadata(m) for m in modules}
    print(common.render(__file__, modules=modules))


if __name__ == "__main__":
    main(sys.argv[1:])
