import os
import re
import random
import shutil

class FrameMap:
    def __init__(self, USDA_file_name, render_top_directory):
        self.file_lines = self.read_file(USDA_file_name)
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
                    #extract xyz coordinates into list
                    coordinates_list = values_list[12:15]
                    data[camera_names[-1]]['frame_coords'][int(frame)] = coordinates_list
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
                print(f'The number of frames in the export file and the number of frames in {camera_name} render directory don\'t match')
        
    def write_data(self, output_file):
        with open(output_file, 'w') as file:
            file.write(str(self.data))

    def print_data(self):
        print(self.data)

class RandomTour:
    def __init__(self, animation_data, frame_target_length):
        self.animation_data = animation_data
        self.frame_target_length = frame_target_length
        self.tour_frame_count = 0
        
        self.all_cameras = list(self.animation_data.keys())
        self.current_camera = random.choice(self.all_cameras)
        self.tour_cameras_order = [self.current_camera]
        self.camera_just_switched = False
        self.current_camera_frame_idx = 0
        self.direction = random.choice([1, -1])
        self.update_camera_path_info()

        self.frames_list = self.get_tour_frames_list()

    def update_camera_path_info(self):
        self.camera_frames_path_dict = self.animation_data[self.current_camera]['frame_files']
        self.camera_frames_max = len(self.camera_frames_path_dict.keys()) - 1

    def get_tour_frames_list(self):
        tour_frames_paths_list = []
        continue_tour = True
        
        while continue_tour:
            # append new frame to list
            new_frame = self.camera_frames_path_dict[self.current_camera_frame_idx]
            tour_frames_paths_list.append(new_frame)

            ## check to see if it is time to stop the tour
            # check if the video length target has been met
            if self.tour_frame_count > self.frame_target_length: 
                # but only stop at the beginning or end of a track
                if self.current_camera_frame_idx == 0 or \
                    self.current_camera_frame_idx == self.camera_frames_max:
                    continue_tour = False
                    break

            ### setup for next loop
            # set next frame
            self.set_next_frame()
            # update camera path dict and frames max
            self.update_camera_path_info()

            #update tour frame count
            self.tour_frame_count += 1
        
        return tour_frames_paths_list

    def set_next_frame(self):  
        intersection = self.get_intersection()
        next_frame_idx = self.current_camera_frame_idx + self.direction # calculate next frame
        if intersection is None or self.camera_just_switched:
            #reset direction if camera just switched onto an end node and is going back towards the intersection
            if next_frame_idx < 0 or next_frame_idx > self.camera_frames_max:
                if self.camera_just_switched:
                    self.direction *= -1
            else: #next frame is within range
                self.current_camera_frame_idx = next_frame_idx # set next frame
            self.camera_just_switched = False
        else:
            self.current_camera = intersection['connected_camera']
            self.tour_cameras_order.append(self.current_camera)
            self.current_camera_frame_idx = intersection['connected_frame']
            self.camera_just_switched = True
            self.direction = random.choice([-1, 1])

    def get_intersection(self):
        camera_intersections_dict = \
            self.animation_data[self.current_camera]['intersections']
        for intersection_key, intersection_info in camera_intersections_dict.items():
            if intersection_info['frame'] == self.current_camera_frame_idx:
                return intersection_info

        return None

    def build_tour_frame_dir(self, main_dir):
        suffix_str = ''.join(random.choices(
            'EQVFXYZ25680', k=4
        ))
        self.tour_name = f'tour_{suffix_str}'
        self.tour_frames_dir = os.path.normpath(f'{main_dir}/{self.tour_name}_frames')
        os.mkdir(self.tour_frames_dir)
        for frame_idx, frame_render_file in enumerate(self.frames_list):
            frame_file_name = f'{frame_idx}.png'
            destination = os.path.join(self.tour_frames_dir, frame_file_name)
            shutil.copy(frame_render_file, destination)

    def make_video(self, video_dir, framerate=30):
        vid_maker = VideoMaker(
            self.tour_frames_dir, video_dir, self.tour_name, framerate)
        print(f'Tour video saved at: {vid_maker.video_file}')


class VideoMaker:
    def __init__(self, frames_dir, video_dir, video_name, framerate, inputs_fmt="d"):
        self.frames_dir = os.path.normpath(frames_dir)
        self.video_dir = os.path.normpath(video_dir)
        self.video_name = video_name
        self.video_file = os.path.join(self.video_dir, f'{self.video_name}.mp4')
        self.framerate = framerate
        self.inputs_fmt = inputs_fmt
        self.make_video()
    
    def make_video(self):
        framerate_cmd = f'-framerate {self.framerate}'
        codec_cmd = '-vcodec libx264rgb'
        inputs_cmd = f'-i {self.frames_dir}/%{self.inputs_fmt}.png'
        dest_cmd = self.video_file

        ffmpeg_command = f'ffmpeg {framerate_cmd} {inputs_cmd} \
            {codec_cmd} {dest_cmd}'
        os.system(ffmpeg_command)


def get_example_data():
    export_file_dir_name = os.path.dirname(__file__)
    export_file_name = os.path.join(
        export_file_dir_name, 'example_data', 'endless_tour_test.usda')
    render_top_dir = 'D:/blender_renders/tour_test_render_frames'
    data_parser = FrameMap(export_file_name, render_top_dir)
    animation_data = data_parser.data

    return animation_data

def make_random_tour(camera_animation_data):
    random_tour = RandomTour(camera_animation_data, 12600)
    random_tour.build_tour_frame_dir('D:/blender_renders')
    random_tour.make_video('D:/blender_renders/animations')

def run():
    camera_animation_data = get_example_data()
    make_random_tour(camera_animation_data)
    print('done')

if __name__ == '__main__':
    run()
