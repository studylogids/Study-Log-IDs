#!/usr/bin/env python3
import csv
from ctypes import ArgumentError
from functools import partial
from itertools import chain
import logging
from pathlib import Path
import sys
from typing import AnyStr, IO, Iterable, List, Set, Tuple

import pandas as pd

from package import scratch, subjects
from toolkit.logid import LogidExecutionError, gather
from toolkit.utilities.execution import bar, do
from toolkit.utilities.project import Project, split_project
from toolkit.utilities.query import isid

logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(levelname)s %(message)s')

def process(subjects: List[Project]):
    def process_subject(subject: Project):
        def process_split(split: Path):
            logging.info('starting %s', split)
            try:
                logtypes = list(gather(split, launcher="file"))
                logging.info("%s", split)
                return logtypes
            except LogidExecutionError as e:
                logging.exception("failed to extract logs from %s retrying by split", split)
                splits = list(filter(lambda s: s.is_dir() or s.suffix == '.java' and s.stem != 'package-info', split_project(split, maxdepth=4)))
                logtypes = list(chain.from_iterable(
                    map(partial(process_split), splits)
                ))
                return logtypes

        count = 0
        count_w_id = 0
        count_w_injection = 0
        for logtype in process_split(subject.path):
            count += 1
            if any(isid(variable) for variable in logtype.variables):
                count_w_id += 1
            for dominator in logtype.dominators:
                if any(isid(variable) for variable in dominator.variables):
                    count_w_injection += 1
        return count, count_w_id, count - count_w_id, count_w_injection

    results = []
    for subject, row in zip(subjects, do(process_subject, subjects)):
        results.append([subject.name, *row])
    return pd.DataFrame(
        results,
        columns=[
            "Subject",
            "Count",
            "Count w/ IDs",
            "Count w/o ID",
            "Count w/ Injections",
        ],
    )


def main():
    result = process(subjects())
    result.to_csv(scratch() / 'extract_logs.csv')


if __name__ == "__main__":
    main()
