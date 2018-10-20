import os
import re

data_path = "data"
output_path = "."
factor_path = "input_factors.ini"

def get_factors():
    factors = {}
    with open(factor_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if '[' in line:
                current_set = re.sub(r'[\[|\]|\n]', '', line)
                factors[current_set] = {}
            elif '=' in line:
                direction, factor = [_.strip() for _ in line.split('=')]
                if factor.isnumeric():
                    factor = int(factor)
                else:
                    factor = 1
                factors[current_set][direction] = factor
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
    with open(''.join(filename), 'r') as f:
        factor_files = {}
        factors_name = list(factors.keys())
        touch(output_path)
        for factor in factors_name:
            factor_files[factor] = open(filename[0].replace(data_path, output_path)+'_'+factor+filename[1],'w+')
        lines = f.readlines()
        for line in lines:
            row_items = line.split(',')
            if len(row_items) == 5 and row_items[0].isnumeric():
                average = sum([float(x) for x in row_items[1:4]])/3
                for factor in factors_name:
                    row_items[4] = average * factors[factor][direction]
                    row_items[4] = ' {:.7e}\n'.format(row_items[4])
                    factor_files[factor].write(','.join(row_items))
            else:
                for factor in factors_name:
                    factor_files[factor].write(line)

        f.close()

if __name__ == "__main__":
    factors = get_factors()
    files = get_files(data_path, ".csv")
    for file, direction in files.items():
        process(file, direction, factors)
