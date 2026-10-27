import csv

def load_single_table(file_name, row_start, vx, vy):
    xlist = []
    ylist = []

    with open(file_name, mode = 'r', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        i = 0
        for row in spamreader:
            if i >= row_start:
                xlist.append(float(row[vx]))
                ylist.append(float(row[vy]))
            else:
                i += 1
    
    return xlist, ylist

def load_multi_table(file_name, row_start, vx, vy_list):
    xlist, ylist = load_single_table(file_name, row_start, vx, vy_list.pop(0))
    yield xlist
    yield ylist
    
    for vy in vy_list:
        xlist, ylist = load_single_table(file_name, row_start, vx, vy)
        yield ylist

class csv_data:
    def __init__(self):
        self.data = []
    
    def load(self, *args):
        input_list = []
        if len(self.data) == 0:
            for telemetry_list in args:
                for telemetry in telemetry_list:
                    for key in telemetry.keys():
                        input_list.append(key)
            self.data.append(input_list)
        input_list = []
        for telemetry_list in args:
            for telemetry in telemetry_list:
                for item in telemetry.values():
                    input_list.append(item)
        self.data.append(input_list)

    def save(self, file_name):
        with open(file_name + '.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.data) # Use writerows for multiple rows