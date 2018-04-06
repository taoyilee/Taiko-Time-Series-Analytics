import os


class TimestampedFrame:
    index = 0

    def __init__(self, frame, timestamp):
        self.frame = frame
        self.timestamp = timestamp

    def write(self, image_dir):
        os.makedirs(image_dir, exist_ok=True)
        self.frame.save(os.path.join(image_dir, f"capture_{self.index:03d}.png"))
