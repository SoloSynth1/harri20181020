import os
import re
import threading

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
                factors[current_set][direction] = int(factor) if factor.isnumeric() else 1
        f.close()
    return factors

def touch(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_files(path, extension):
    files = {}
    for file in os.listdir(path):
        if file.lower().endswith(extension.lower()):
            files[os.path.join(path,file)] = os.path.splitext(file)[0].split("_")[1]
    return files

def process(file, direction, factors):
    filename = os.path.splitext(file)
    with open(file, 'r') as f:
        factor_files = {}
        touch(output_path)
        for factor in factors:
            factor_files[factor] = open(filename[0].replace(data_path, output_path)+'_'+factor+filename[1],'w')
        for line in f.readlines():
            row_items = line.split(',')
            if len(row_items) == 5 and row_items[0].isnumeric():
                average = sum([float(x) for x in row_items[1:4]])/3
                for factor in factors:
                    row_items[4] = average * factors[factor][direction]
                    row_items[4] = ' {:.8e}\n'.format(row_items[4])
                    factor_files[factor].write(','.join(row_items))
            else:
                for factor in factors:
                    factor_files[factor].write(line)

if __name__ == "__main__":
    factors = get_factors()
    files = get_files(data_path, ".csv")
    for file, direction in files.items():
        threading.Thread(target=process, args=(file, direction, factors)).start()
