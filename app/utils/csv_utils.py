import csv
from typing import Tuple, List, Dict, Optional

def analyze_csv_stream(path: str, delimiter=";") -> Tuple[int, int]:
    """Return number of rows and columns in a CSV file."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        header = next(reader, [])
        columns = len(header)
        rows = sum(1 for _ in reader)
    return rows, columns


def read_csv_page(path: str, delimiter=";", page: int = 1, page_size: int = 100) -> List[Dict]:
    """
    Reads a page of CSV rows as list of dicts (header -> value).

    :param path: Path to CSV file
    :param delimiter: CSV delimiter
    :param page: 1-based page number
    :param page_size: number of rows per page
    :return: list of rows as dicts
    """
    start = (page - 1) * page_size
    end = start + page_size
    data = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for i, row in enumerate(reader):
            if i < start:
                continue
            if i >= end:
                break
            data.append(row)
    return data

def read_csv_as_dicts(path: str, delimiter=";") -> List[Dict]:
    """Return CSV content as a list of dicts (header -> value)."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        return [row for row in reader]