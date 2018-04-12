from app.video.timestamped_frame import TimestampedFrame
import cv2
import os
import numpy as np


class TimestampedFrameSeries:
    frames = []

    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height

    def append(self, frame: TimestampedFrame):
        if not isinstance(frame, TimestampedFrame):
            raise TypeError(f"TimestampedFrameSeries only accepts TimestampedFrame, received {type(frame)}")
        frame.index = len(self.frames)
        self.frames.append(frame)

    def write(self, image_dir):
        for f in self.frames:
            f.write(image_dir)

    def write_video(self, video_dir):
        time_stamps = self.get_timestamps()
        fps = np.mean(1 / (np.array(time_stamps[1:]) - np.array(time_stamps[0:-1])))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        frame_0 = np.array(self.frames[0].frame)
        size = np.shape(frame_0)[1], np.shape(frame_0)[0]
        out = cv2.VideoWriter(os.path.join(video_dir, "output.avi"), fourcc, fps, size, 1)

        for f in self.frames:
            frame = cv2.resize(np.array(f.frame), size)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)

        out.release()
        cv2.destroyAllWindows()

    def get_timestamps(self):
        return [f.timestamp for f in self.frames]

    def insert_time_series(self, time_series):
        pass
