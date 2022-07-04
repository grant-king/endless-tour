from main import VideoMaker

def run():
    frames_dir = 'D:/blender_renders/warehouse_render_frames'
    video_dir = 'D:/blender_renders/animations'
    video_name = 'warehouse_1'
    framerate = 30
    inputs_fmt = '04d'

    VideoMaker(
        frames_dir, video_dir, video_name, framerate, inputs_fmt=inputs_fmt)

if __name__ == '__main__':
    run()