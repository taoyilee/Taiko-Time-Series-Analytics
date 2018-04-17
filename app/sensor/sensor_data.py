import configparser as cp
from app.sensor.sensor_db_model import SensorModel
import matplotlib.pyplot as plt
import scipy.integrate as integrate
from scipy import interpolate
import pandas as pd
from sklearn.decomposition import PCA
import numpy as np
from PIL import Image
import io
from app.notes.music_notes import plot_notes
import cv2
import os
from app.dbutils import MySQLTaiko


class SensorData:
    verbosity = 0

    def __init__(self, config: cp.ConfigParser, database_handle: MySQLTaiko, sensor_db_model: SensorModel, song_id):
        self.database_handle = database_handle
        self.song_id = song_id
        self.config = config
        self.sensor_db_model = sensor_db_model
        self.verbosity = config["DEFAULT"].getint("verbosity")

    def plot_curve_only_axis(self, hand="left", axis_name="imu_ax", ax_num=None, title=None, filename=None):
        print(f"** Plotting sensor data for {hand} hand on axis {axis_name}")
        data = self.sensor_db_model.get_sensor_data_axis(hand=hand, axis_name=axis_name)
        total_steps = 200
        step_size = max(data.index) / total_steps
        print(f"Using step_size of {step_size}")
        steps = np.arange(0, max(data.index), step_size)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

        plt.figure(num=ax_num)
        data.plot()
        plt.axvspan(17.5, 19, color='red', alpha=0.5)
        plt.axis("off")
        buf = io.BytesIO()
        plt.savefig(buf)  # , transparent=True)
        im = Image.open(buf)  # type: Image.Image
        size = np.shape(im)[1], np.shape(im)[0]
        out = cv2.VideoWriter(os.path.join("video_output.avi"), fourcc, 15, size, 1)

        for i, step_i in enumerate(steps):
            plt.xlim([step_i, step_i + 10 * step_size])
            buf = io.BytesIO()
            plt.savefig(buf)  # , transparent=True)
            im = Image.open(buf)  # type: Image.Image
            frame = cv2.resize(np.array(im)[:, :, 0:3], size)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
            plt.savefig(os.path.join(f"image_{i}.png"), transparent=True)

        out.release()
        cv2.destroyAllWindows()

        im.save(f"{filename}_{axis_name}_im.png")
        plt.close()

    def plot_data_axis(self, hand="left", axis_name="imu_ax", ax_num=None):
        print(f"** Plotting sensor data for {hand} hand on axis {axis_name}")
        data = self.sensor_db_model.get_sensor_data_axis(hand=hand, axis_name=axis_name)
        plt.figure(num=ax_num)
        data.plot(legend=True)
        plt.xlim([0, max(data.index)])

    def plot_speed(self, arm_length=1, ax_num=0, title=None, filename=None, show_ideal=True, offset=0):
        data = self.speed(arm_length=arm_length)
        plt.figure(num=ax_num, figsize=(14, 8))
        data.plot()
        y_range = 300
        if show_ideal:
            legend_names = plot_notes(self.config, self.database_handle, self.song_id, plt, offset, 2 * y_range,
                                      -y_range)
        plt.legend(["signal"] + legend_names)
        plt.xticks(np.arange(0, 120, 4))
        plt.xlim([0, max(data.index)])
        plt.title(f"{title} - Speed", family="IPAPGothic")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Sensor data (PCA)")
        plt.ylim([-y_range, y_range])
        plt.grid()
        if filename is not None:
            output_file = f"{filename}_speed.png"
            print(f"Saving figure to {output_file}")
            plt.savefig(output_file)

        # save video
        total_steps = 200
        step_size = max(data.index) / total_steps
        print(f"Using step_size of {step_size}")
        steps = np.arange(0, max(data.index), step_size)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')

        buf = io.BytesIO()
        plt.savefig(buf)  # , transparent=True)
        im = Image.open(buf)  # type: Image.Image
        size = np.shape(im)[1], np.shape(im)[0]
        out = cv2.VideoWriter(os.path.join("images", "speed_video_output.avi"), fourcc, 15, size, 1)

        for i, step_i in enumerate(steps):
            plt.xlim([step_i, step_i + 10 * step_size])
            buf = io.BytesIO()
            plt.savefig(buf)  # , transparent=True)
            im = Image.open(buf)  # type: Image.Image
            frame = cv2.resize(np.array(im)[:, :, 0:3], size)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out.write(frame)
            # plt.savefig(os.path.join(f"image_{i}.png"), transparent=True)

        out.release()
        cv2.destroyAllWindows()

        plt.close()
        return data

    def speed(self, arm_length=1):
        data_ax_left = self.sensor_db_model.get_sensor_data_axis(hand="left", axis_name="imu_ax")
        time_index_left = data_ax_left.index
        data_ay_left = self.sensor_db_model.get_sensor_data_axis(hand="left", axis_name="imu_ay")
        data_az_left = self.sensor_db_model.get_sensor_data_axis(hand="left", axis_name="imu_az")
        data_gx_left = self.sensor_db_model.get_sensor_data_axis(hand="left", axis_name="imu_gx")
        data_gy_left = self.sensor_db_model.get_sensor_data_axis(hand="left", axis_name="imu_gy")
        data_gz_left = self.sensor_db_model.get_sensor_data_axis(hand="left", axis_name="imu_gz")

        data_ax_right = self.sensor_db_model.get_sensor_data_axis(hand="right", axis_name="imu_ax")
        time_index_right = data_ax_right.index
        data_ay_right = self.sensor_db_model.get_sensor_data_axis(hand="right", axis_name="imu_ay")
        data_az_right = self.sensor_db_model.get_sensor_data_axis(hand="right", axis_name="imu_az")
        data_gx_right = self.sensor_db_model.get_sensor_data_axis(hand="right", axis_name="imu_gx")
        data_gy_right = self.sensor_db_model.get_sensor_data_axis(hand="right", axis_name="imu_gy")
        data_gz_right = self.sensor_db_model.get_sensor_data_axis(hand="right", axis_name="imu_gz")

        data_ax_left_analog = interpolate.interp1d(time_index_left, data_ax_left.values)
        data_ay_left_analog = interpolate.interp1d(time_index_left, data_ay_left.values)
        data_az_left_analog = interpolate.interp1d(time_index_left, data_az_left.values)
        data_gx_left_analog = interpolate.interp1d(time_index_left, data_gx_left.values)
        data_gy_left_analog = interpolate.interp1d(time_index_left, data_gy_left.values)
        data_gz_left_analog = interpolate.interp1d(time_index_left, data_gz_left.values)

        data_ax_right_analog = interpolate.interp1d(time_index_right, data_ax_right.values)
        data_ay_right_analog = interpolate.interp1d(time_index_right, data_ay_right.values)
        data_az_right_analog = interpolate.interp1d(time_index_right, data_az_right.values)
        data_gx_right_analog = interpolate.interp1d(time_index_right, data_gx_right.values)
        data_gy_right_analog = interpolate.interp1d(time_index_right, data_gy_right.values)
        data_gz_right_analog = interpolate.interp1d(time_index_right, data_gz_right.values)

        time_index_new = np.arange(max(time_index_left.min(), time_index_right.min()),
                                   min(time_index_left.max(), time_index_right.max()), 0.01)

        data = np.stack([data_ax_left_analog(time_index_new),
                         data_ay_left_analog(time_index_new),
                         data_az_left_analog(time_index_new),
                         arm_length * data_gx_left_analog(time_index_new),
                         arm_length * data_gy_left_analog(time_index_new),
                         arm_length * data_gz_left_analog(time_index_new),
                         data_ax_right_analog(time_index_new),
                         data_ay_right_analog(time_index_new),
                         data_az_right_analog(time_index_new),
                         arm_length * data_gx_right_analog(time_index_new),
                         arm_length * data_gy_right_analog(time_index_new),
                         arm_length * data_gz_right_analog(time_index_new)], axis=1)

        pca = PCA(n_components=1)
        pca_data = pca.fit_transform(data).squeeze()
        return pd.Series(pca_data, index=time_index_new)

    def plot_data(self, hand="left", axis_name="imu_ax", ax_num=0, title=None, filename=None):
        hand = ["left", "right"] if hand == "all" else [hand]
        plt.figure(num=ax_num, figsize=(8, 6))
        for h in hand:
            self.plot_data_axis(hand=h, axis_name=axis_name, ax_num=ax_num)
        if filename is not None:
            plt.title(f"{title} - {axis_name}", family="IPAPGothic")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Sensor data")
            # plt.ylim([-2.5, 2.5])
            plt.grid()
            plt.savefig(f"{filename}_{axis_name}.png")
            plt.close()
