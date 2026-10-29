import csv
from loguru import logger

from .curve import Curve

def load(file_name, key_mapping: dict = None):
    with open(file_name, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        data = Curve()

        header = True
        keys = []
        for row in reader:
            if key_mapping:
                for k, v in key_mapping.items():
                    try:
                        data.append({k: float(row[v])})
                    except ValueError:
                        logger.warning(f"Could not convert value '{row[v]}' to float for key '{k}'. Skipping row.")
                        break
                    except IndexError:
                        logger.warning(f"Index {v} is out of range for row: {row}. Skipping row.")
                        break
            else:
                if header:
                    header = False
                    for col in row:
                        keys.append(col)
                else:
                    if len(row) != len(keys):
                        logger.warning(f"Row length {len(row)} does not match header length {len(keys)}. Skipping row: {row}")
                        continue

                    for i in range(len(row)):
                        try:
                            data.append({keys[i]: float(row[i])})
                        except ValueError:
                            logger.warning(f"Could not convert value '{row[i]}' to float for key '{keys[i]}'.")

    return data

def save(file_name, key_mapping: dict):
    data = [[]]

    for k, v in key_mapping.items():
        data[0].append(k)
        size = len(v)

    for i in range(size):
        block = []
        for k, v in key_mapping.items():
            block.append(v[i])
        data.append(block)

    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data) # Use writerows for multiple rows