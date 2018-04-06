from app.video.timestamped_frame import TimestampedFrame


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

    # TODO: Write video file
