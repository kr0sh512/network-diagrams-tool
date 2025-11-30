from parse import parse_csv_to_structure
import sys
from structures import Host, Wire


def check_correct(data):
    assert isinstance(data, dict)

    for key, value in data.items():
        assert isinstance(key, str)
        assert isinstance(value, dict)

        # for subkey, subvalue in value.items():
        #     assert isinstance(subkey, str)
        #     assert isinstance(subvalue, str)


if __name__ == "__main__":
    data = parse_csv_to_structure(sys.argv[1])
    if check_correct(data):
        print("yay!")
    print(data)
