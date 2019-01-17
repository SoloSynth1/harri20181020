import os
import re
import threading
import numpy as np

data_path = "data"
output_path = "."
factor_path = "input_factors.ini"


def get_factors():
    factors = {}
    with open(factor_path, 'r') as f:
        for line in f.readlines():
            if '[' in line:
                current_set = re.sub(r'[\[|\]|\n]', '', line)
                factors[current_set] = {}
            elif '=' in line:
                direction, factor = [_.strip() for _ in line.split('=')]
                factors[current_set][direction] = percent_convert(factor)
        f.close()
    print(factors)
    return factors


def percent_convert(factor):
    if '%' in factor:
        return float(factor.replace('%', ''))/100
    else:
        return 1


def touch(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_files(path, extension):
    files = {}
    for file in os.listdir(path):
        if file.lower().endswith(extension.lower()):
            file_detail = [os.path.splitext(file)[0].split("_")[1], os.path.getsize(file)]
            print(file_detail)
            files[os.path.join(path, file)] = file_detail
    return files


def read(files):
    data = {}
    threads = []
    for file, direction in files.items():
        t = threading.Thread(target=get_surfaces, args=(data, direction, file))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()
    return data


def get_surfaces(data, direction, file):
    result = {}
    with open(file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "[Name]" in line:
                current_surface = lines[i+1].strip('\n')
                result[current_surface] = []
            else:
                row_items = line.split(',')
                if is_datarow(row_items):
                    result[current_surface].append(float(row_items[4].strip('\n')))
        for surface in result:
            result[surface] = np.array(result[surface])
    data[direction] = result

def is_datarow(row_items):
    return (len(row_items) == 5 and row_items[0].isnumeric())

def write(file, average):
    filename = os.path.splitext(file)
    with open(file, 'r') as f:
        files = {}
        touch(output_path)
        lines = f.readlines()
        for factor_set in average:
            files[factor_set] = open(filename[0].replace(data_path, output_path)+'_'+factor_set+filename[1],'w')
            threading.Thread(target=write_thread, args=(files[factor_set], lines, average[factor_set])).start()

def write_thread(opened_file, lines, factor_set):
    for i, line in enumerate(lines):
        row_items = line.split(',')
        if '[Name]' in line:
            current_surface = lines[i+1].strip('\n')
        if is_datarow(row_items):
            idx = int(row_items[0])
            row_items[4] = ' {:.8e}\n'.format(factor_set[current_surface][idx])
            opened_file.write(','.join(row_items))
        else:
            opened_file.write(line)
    opened_file.close()

def process(data, factors):
    average = {}
    surfaces = []
    for direction in data:
        surfaces += data[direction]
    surfaces = set(surfaces)
    for factor_set in factors:
        average[factor_set] = {}
        for surface in surfaces:
            average[factor_set][surface] = []
            for direction in data:
                if surface in data[direction]:
                    average[factor_set][surface].append(np.multiply(data[direction][surface],factors[factor_set][direction]))
    for factor_set in average:
        for surface in average[factor_set]:
            average[factor_set][surface] = np.average(np.array(average[factor_set][surface]), axis=0)
    return average

if __name__ == "__main__":
    factors = get_factors()
    files = get_files(data_path, ".csv")
    data = read(files)
    average = process(data, factors)
    for file in files:
        threading.Thread(target=write, args=(file, average)).start()
