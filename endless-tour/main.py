import os
import re

class USDAParser:
    def __init__(self, file_name):
        self.file_lines = self.read_file(file_name)
        self.data = self.parse_data(self.file_lines)

    def read_file(self, file_name):
        with open(file_name, 'r') as file:
            lines = file.readlines()

        for idx in range(len(lines)):
            lines[idx] = lines[idx].strip()

        return lines

    def skip_line(self, line):
        skip_start_characters = ['#', '(']
        skip = False
        for char in skip_start_characters:
            if line.startswith(char):
                skip = True
        
        return skip

    def parse_data(self, lines):
        camera_names = []
        data = {}

        for idx in range(len(lines)):
            line = lines[idx]
            if len(line) > 0:
                if line.split()[0][:-1].isnumeric():
                    frame = line.split()[0][:-1]
                    animation_text = line[line.index(':')+2 : -2]
                    values_list = re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", animation_text)
                    #extract all coordinates into list
                    coordinates_list = values_list[12:15]
                    data[camera_names[-1]][frame] = coordinates_list
                elif line.startswith('def Xform'):
                    camera_names.append(line[line.index('"')+1 : line.rindex('"')])
                    data[camera_names[-1]] = {}
                else:
                    continue
            
        return data
                
    def write_data(self, output_file):
        with open(output_file, 'w') as file:
            file.write(str(self.data))

    def print_data(self):
        print(self.data)


def run():
    dir_name = os.path.dirname(__file__)
    file_name = os.path.join(dir_name, 'example_data', 'endless_tour_test.usda')
    data_parser = USDAParser(file_name)
    animation_data = data_parser.data

if __name__ == '__main__':
    run()
