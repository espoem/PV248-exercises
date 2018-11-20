import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

import numpy

ROUND_DIGITS = 6


def cumulate(data_list):
    res = []
    sum_ = 0
    for item in data_list:
        sum_ += item
        res.append(sum_)
    return res


def average_student_data(data):
    data_res = {}
    for k, v in data.items():
        points = numpy.array(list(v.values()))
        data_res[k] = numpy.mean(points)
    return data_res


def regression(dataset):
    start_date = datetime.strptime("2018-09-17", "%Y-%m-%d").date()
    data_sorted = sorted(dataset.items())
    # print(data_sorted)
    elapsed_times = [
        (datetime.strptime(i[0], "%Y-%m-%d").date() - start_date).days
        for i in data_sorted
    ]
    # print(elapsed_times)
    cumulated_points = cumulate([x[1] for x in data_sorted])
    # print(cumulated_points)
    # x = numpy.vstack([elapsed_times, numpy.ones(len(elapsed_times))]).T
    x = numpy.vstack([elapsed_times]).T
    y = numpy.array(cumulated_points)
    # print(x)
    slope, *_ = numpy.linalg.lstsq(x, y, rcond=None)
    slope = slope[0]
    if slope != 0:
        date16 = start_date + timedelta(days=16 / slope)
        date20 = start_date + timedelta(days=20 / slope)
    else:
        date16 = None
        date20 = None
    return slope, date16, date20


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
    points_per_exercise = {}
    points_per_date = {}
    with open(csv_file) as f:
        reader = csv.reader(f)
        for row in reader:
            if not header_parsed:
                header = row
                header_parsed = True
                continue
            for idx in range(1, len(row)):
                key_split = header[idx].strip().split("/")
                key_exercise = key_split[1]
                key_date = key_split[0]

                if not key_exercise in points_per_exercise:
                    points_per_exercise[key_exercise] = defaultdict(lambda: 0)
                points_per_exercise[key_exercise][row[0]] += float(row[idx])

                if not key_date in points_per_date:
                    points_per_date[key_date] = defaultdict(lambda: 0)
                points_per_date[key_date][row[0]] += float(row[idx])
    # print(points_per_exercise)

    if mode == "average":
        data_student_exercise = average_student_data(points_per_exercise)
        data_student_date = average_student_data(points_per_date)
    else:
        student_id = mode
        data_student_exercise = {}
        for k, v in points_per_exercise.items():
            data_student_exercise[k] = v[student_id]
        data_student_date = {}
        for k, v in points_per_date.items():
            data_student_date[k] = v[student_id]

    # print(data_student_exercise)
    # print(data_student_date)
    data_res = {}
    points = numpy.array(list(data_student_exercise.values()))
    data_res["mean"] = numpy.mean(points)
    data_res["median"] = numpy.median(points)
    data_res["passed"] = len(points[points > 0])
    data_res["total"] = numpy.sum(points)

    slope, date16, date20 = regression(data_student_date)
    data_res["slope"] = slope
    if slope != 0:
        data_res["date 16"] = date16.isoformat()
        data_res["date 20"] = date20.isoformat()

    print(json.dumps(data_res, indent=2))


if __name__ == "__main__":
    main()
