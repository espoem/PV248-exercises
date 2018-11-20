import csv
import json
import os
import sys
from collections import defaultdict

import numpy


def main():
    args = sys.argv
    try:
        mode = args[2].lower()
    except:
        print("Wrong number of parameters")
        exit(1)

    here = os.path.dirname(__file__)
    csv_file = os.path.join(here, args[1])

    header_parsed = False
    header = None
    key = None
    data_aux = {}
    with open(csv_file) as f:
        reader = csv.reader(f)
        for row in reader:
            if not header_parsed:
                header = row
                header_parsed = True
                continue
            for idx in range(1, len(row)):
                key_split = header[idx].strip().split("/")
                if mode == "dates":
                    key = key_split[0]
                elif mode == "exercises":
                    key = key_split[1]
                else:
                    key = header[idx]

                if not key in data_aux:
                    data_aux[key] = defaultdict(lambda: 0)
                data_aux[key][row[0]] += float(row[idx])

    data_res = defaultdict(dict)
    for key, value in data_aux.items():
        np_val_arr = numpy.array(list(value.values()))
        data_res[key]["mean"] = round(numpy.mean(np_val_arr), 4)
        data_res[key]["median"] = numpy.median(np_val_arr)
        data_res[key]["passed"] = len(np_val_arr[np_val_arr > 0])
        quantiles = numpy.quantile(np_val_arr, [0.25, 0.75], interpolation="midpoint")
        data_res[key]["first"] = quantiles[0]
        data_res[key]["last"] = quantiles[1]

    print(json.dumps(data_res, indent=2))


if __name__ == "__main__":
    main()
