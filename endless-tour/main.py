import os
import re

{
    'Camera_007': {
        '0': ['-4.5', ' 4.5', ' 1.7999999523162842'], 
        '1': ['-4.47857141494751', ' 4.5', ' 1.7999999523162842'], 
        '2': ['-4.4571428298950195', ' 4.5', ' 1.7999999523162842'], 
        '3': ['-4.435714244842529', ' 4.5', ' 1.7999999523162842'], 
        '4': ['-4.414285659790039', ' 4.5', ' 1.7999999523162842'], 
        '5': ['-4.392857074737549', ' 4.5', ' 1.7999999523162842']
    },
    'Camera_006': {
        '80': ['-4.5', ' 4.5', ' 1.7999999523162842'], 
        '81': ['-4.5', ' 3.664285659790039', ' 1.7999999523162842'], 
        '82': ['-4.5', ' 3.6857147216796875', ' 1.7999999523162842'], 
        '83': ['-4.5', ' 3.7071428298950195', ' 1.7999999523162842'], 
        '84': ['-4.5', ' 3.728571891784668', ' 1.7999999523162842'], 
        '85': ['-4.5', ' 3.75', ' 1.7999999523162842']
    }
}
    

class USDAParser:
    def __init__(self, file_name):
        self.file_lines = self.read_file(file_name)
        self.data = self.parse_data(self.file_lines)
        self.add_intersections()

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
                    data[camera_names[-1]]['frame_coords'][frame] = coordinates_list
                elif line.startswith('def Xform'):
                    camera_names.append(line[line.index('"')+1 : line.rindex('"')])
                    data[camera_names[-1]] = {}
                    data[camera_names[-1]]['frame_coords'] = {}
                else:
                    continue
            
        return data
                
    def add_intersections(self):
        intersections = {}
        for cam_1, cam_1_values in self.data.items():
            intersection_idx = 0
            #intersections[cam_1] = {}
            self.data[cam_1]['intersections'] = {}
            for cam_2, cam_2_values in self.data.items():
                if cam_1 != cam_2:
                    for frame_1, location_coords_list_1 in cam_1_values['frame_coords'].items():
                        for frame_2, location_coords_list_2 in cam_2_values['frame_coords'].items():
                            if location_coords_list_1 == location_coords_list_2:
                                intersection_dict = {'frame': frame_1, 'connected_camera': cam_2}
                                #intersections[cam_1][intersection_idx] = intersection_dict
                                self.data[cam_1]['intersections'][intersection_idx] = intersection_dict
                                intersection_idx += 1
                                
                                print(f'match found: camera {cam_1} frame {frame_1} and camera {cam_2} frame {frame_2}')

    def write_data(self, output_file):
        with open(output_file, 'w') as file:
            file.write(str(self.data))

    def print_data(self):
        print(self.data)

def get_example_data():
    dir_name = os.path.dirname(__file__)
    file_name = os.path.join(dir_name, 'example_data', 'endless_tour_test.usda')
    data_parser = USDAParser(file_name)
    animation_data = data_parser.data

    return animation_data


    


def run():
    camera_animation_data = get_example_data()
    print('done')

if __name__ == '__main__':
    run()
