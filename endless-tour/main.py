import os
import re

class FrameMap:
    def __init__(self, file_name, render_top_directory):
        self.file_lines = self.read_file(file_name)
        self.data = self.parse_data(self.file_lines)
        self.add_intersections()
        self.add_frame_paths(render_top_directory)

    def read_file(self, file_name):
        with open(file_name, 'r') as file:
            lines = file.readlines()

        for idx in range(len(lines)):
            lines[idx] = lines[idx].strip()

        return lines

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
                                intersection_dict = {'frame': frame_1, 'connected_camera': cam_2, 'connected_frame': frame_2}
                                #intersections[cam_1][intersection_idx] = intersection_dict
                                self.data[cam_1]['intersections'][intersection_idx] = intersection_dict
                                intersection_idx += 1
                                
                                print(f'match found: camera {cam_1} frame {frame_1} and camera {cam_2} frame {frame_2}')

    def add_frame_paths(self, render_top_directory):
        render_top_directory = os.path.normpath(render_top_directory)
        for camera_render_folder in os.listdir(render_top_directory):
            frame_file_list = os.listdir(f'{render_top_directory}/{camera_render_folder}')
            camera_name = camera_render_folder
            self.data[camera_name]['frame_files'] = {}
            frame_count = len(self.data[camera_name]['frame_coords'].keys())
            if len(frame_file_list) == frame_count:
                for frame_idx in range(frame_count):
                    frame_path = os.path.join(
                        render_top_directory, camera_render_folder, 
                        frame_file_list[frame_idx])
                    self.data[camera_name]['frame_files'][frame_idx] = frame_path
            else:
                print('The number of frames in the export file and the number of frames in the camera render directory don\'t match')
                return -1
        
    def write_data(self, output_file):
        with open(output_file, 'w') as file:
            file.write(str(self.data))

    def print_data(self):
        print(self.data)


def get_example_data():
    export_file_dir_name = os.path.dirname(__file__)
    export_file_name = os.path.join(
        export_file_dir_name, 'example_data', 'endless_tour_test.usda')
    render_top_dir = 'D:/blender_renders/tour_test_render_frames'
    data_parser = FrameMap(export_file_name, render_top_dir)
    animation_data = data_parser.data

    return animation_data

def run():
    camera_animation_data = get_example_data()
    print('done')

if __name__ == '__main__':
    run()
