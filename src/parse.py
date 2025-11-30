import csv


def parse_csv_to_structure(path):
    result = {}

    with open(path, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    headers = rows[0][1:]

    for row in rows[1:]:
        obj = row[0].strip()

        if not obj:
            continue

        result[obj] = {}
        for header, value in zip(headers, row[1:]):
            value = value.strip()

            if value:
                result[obj][header] = value

    return result


if __name__ == "__main__":
    data = parse_csv_to_structure("input.csv")
    print(data)
