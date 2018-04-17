from app.video import CaptureModel
from app.sensor.sensor_data import SensorData
import os


class Performance:
    frame_model = None

    def __init__(self, performance_id, database_handle, config):
        self.performance_id = performance_id
        self.database_handle = database_handle
        self.config = config
        self.database_handle.set_database(self.config["DATA"].get("database_name"))
        cursor = self.database_handle.cursor()
        query = ("SELECT * FROM taiko_performances INNER JOIN `taiko_songs` "
                 "ON `taiko_performances`.`song`=`taiko_songs`.`id` "
                 f"WHERE taiko_performances.`id`={self.performance_id} LIMIT 1")
        cursor.execute(query)
        (_, self.name, self.song_id, self.nth, self.year, self.month, self.date, self.hour, self.minute, self.second, _,
         self.song, self.diffi) = cursor.next()
        self.frame_model = CaptureModel(self.config, self.database_handle,
                                        (self.year, self.month, self.date, self.hour, self.minute, self.second))
        cursor.close()

    def write_frames(self):
        frames = self.frame_model.frames()
        frames.write(self.config["DEFAULT"].get("image_directory"))

    def write_video(self):
        sensor_data = SensorData(self.config, self.database_handle, self.frame_model.sensor_data(), self.song_id)
        file_name = os.path.join(self.config["DEFAULT"].get("image_directory"),
                                 f"{self.name}_{self.song_id}_{self.diffi}_{self.nth}_curve")
        title = f"Test Subject#{self.name} {self.song}({self.song_id})@{self.diffi} Performance #{self.nth}"

        speed_data = sensor_data.plot_speed(title=title, filename=file_name, offset=11.8)
        # sensor_data.plot_data(hand="all", axis_name="imu_ax", title=title, filename=file_name)
        # sensor_data.plot_curve_only_axis(hand="left", axis_name="imu_ax", title=title, filename=file_name)
        # sensor_data.plot_data(hand="all", axis_name="imu_ay", title=title, filename=file_name)
        # sensor_data.plot_data(hand="all", axis_name="imu_az", title=title, filename=file_name)
        # sensor_data.speed(hand="left")
        # frames = frame_model.frames()
        # video_dir = os.path.join(config["DEFAULT"].get("image_directory"), f"video_{name}")
        # os.makedirs(video_dir, exist_ok=True)
        # frames.write_video(video_dir)
