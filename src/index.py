import sys

import common


def main(modules):
    print(common.render(__file__, modules=modules))


if __name__ == "__main__":
    main(sys.argv[1:])
