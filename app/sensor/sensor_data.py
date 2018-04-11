import configparser as cp
from app.sensor.sensor_db_model import SensorModel
import matplotlib.pyplot as plt


class SensorData:
    verbosity = 0

    imu_ax = None
    imu_ay = None
    imu_az = None
    imu_gx = None
    imu_gy = None
    imu_gz = None
    time = None

    def __init__(self, config: cp.ConfigParser, sensor_db_model: SensorModel):
        self.config = config
        self.sensor_db_model = sensor_db_model
        self.verbosity = config["DEFAULT"].getint("verbosity")

    def plot_data_axis(self, hand="left", axis_name="imu_ax", ax_num=None):
        print(f"** Plotting sensor data for {hand} hand on axis {axis_name}")
        time_series = self.sensor_db_model.get_sensor_data_axis(hand=hand, axis_name=axis_name)  # type: pd.Series
        plt.figure(num=ax_num)
        time_series.plot(legend=True)
        plt.xlim([0, max(time_series.index)])

    def plot_data(self, hand="left", axis_name="imu_ax", ax_num=0, title=None, filename=None):
        hand = ["left", "right"] if hand == "all" else [hand]
        plt.figure(num=ax_num, figsize=(14, 6))
        for h in hand:
            self.plot_data_axis(hand=h, axis_name=axis_name, ax_num=ax_num)
        if filename is not None:
            plt.title(f"{title} - {axis_name}", family="IPAPGothic")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Sensor data")
            plt.ylim([-2.5, 2.5])
            plt.grid()
            plt.savefig(f"{filename}_{axis_name}.png")
            plt.close()
