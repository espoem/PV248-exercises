import os
import re
import sys
from collections import defaultdict

import numpy
from numpy import linalg

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except:
        exit(1)

    here = os.path.dirname(__file__)
    vars_parse = re.compile(r"([+-]? ?(\d*)(\w))")
    mtx_dict = {}
    vars_names = set()
    eq_count = 0
    for idx, line in enumerate(open(os.path.join(here, filename), "r").readlines()):
        parts = line.split("=")
        left = parts[0]
        right = float(parts[1].strip())
        mtx_dict[idx] = {"left": defaultdict(lambda: 0), "right": right}
        for v in vars_parse.findall(left):
            # mtx[idx].setdefault({})
            sgn = -1 if v[0].startswith("-") else 1
            mtx_dict[idx]["left"][v[2]] = sgn * float(v[1]) if v[1] else sgn
            vars_names.add(v[2])
        eq_count += 1

    mtx = []
    mtx_augmented = []
    vars_names_sorted = sorted(list(vars_names))
    for k, line in mtx_dict.items():
        mtx_row = [line["left"][var_name] for var_name in vars_names_sorted]
        mtx.append(mtx_row)
        mtx_augmented.append([v for v in mtx_row] + [line["right"]])

    matrix = numpy.array(mtx)
    matrix_augmented = numpy.array(mtx_augmented)
    r1 = linalg.matrix_rank(matrix)
    r2 = linalg.matrix_rank(matrix_augmented)
    vars_count = len(vars_names)

    if r1 < r2:
        print("no solution")
        exit(0)

    if vars_count > r1 and vars_count > r2:
        print("solution space dimension: {}".format(vars_count - r1))
        exit(0)

    solutions = linalg.solve(matrix, matrix_augmented.T[-1])
    msgs = []
    for idx, s in enumerate(solutions):
        msgs.append("{} = {}".format(vars_names_sorted[idx], s))
    print("solution: " + ", ".join(msgs))
