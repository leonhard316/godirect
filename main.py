# サーモで計測とRGBで録画を行い、bitalinoで計測を行うプログラム
# データ取得部分をマルチスレッドにする
import numpy
import cv2
import threading
import time
from bitalino import BITalino
from flirpy.camera.boson import Boson
import os

def workerForBItalino(device, N_SAMPLE, data, _times, _signals, output_dir=' '):
    """指定秒間のBItalinoデータを保存"""
    data = device.read(N_SAMPLE)
    device.close()
    for i in range(len(data)):
        _times.append(dt * i)
        _signals.append(data[i][-1])
    with open(txt_file, 'a') as f:
        f.write("Sampling Rate={}\n".format(SAMPLING_RATE))
        f.write("fRR={}\n".format(calculate_fRR(_times, _signals, output_dir, n_padding)))
        # f.write("tRR={}\n".format(calculate_tRR(_times, _signals, output_dir, n_padding)))

    f.close()
    print("Number of signals", len(_signals))
    print("elapsed_time", _times[len(_times) - 1])
    print("initial_time", _times[0])
    WriteSignal2CSV(_times, _signals, output_dir)
    WriteSignal2Graph(_times, _signals, output_dir)

# Boson-----------------------------------------------------------------------------
def workerForBoson(camera1, running_time, txt_file, u16_frames, _times, output_dir):

    initial_time = time.clock()
    elapsed_time = time.clock()
    while True:
        ret, u16_frame = camera1.read()
        if elapsed_time - initial_time > running_time:
            print("Thermal_time : ", elapsed_time - initial_time)
            break
        elif elapsed_time - initial_time < running_time:
            u16_frames.append(u16_frame)
            _times.append(elapsed_time - initial_time)
            elapsed_time = time.clock()
    print(u16_frame.dtype)
    fps = len(u16_frames) / running_time
    print("Thermal_elapsedtime", elapsed_time)
    print("Thermal_itialtime", initial_time)
    print("Number of frame : ", len(u16_frames))
    print("estimated fps : ", fps)
    with open(txt_file, 'a') as f:
        f.write("estimated Thermal_fps={}\n".format(fps))
    f.close()
    SaveThermoTIFF(u16_frames, output_dir)
    SaveThermoMP4(u16_frames, output_dir, fps)

# RGB
def workerForRGB(camera2, running_time, txt_file, RGB_frames, _times, output_dir):
    initial_time = time.clock()
    elapsed_time = time.clock()
    while True:
        ret, RGB_frame = camera2.read()
        RGB_frame = cv2.cvtColor(RGB_frame, cv2.COLOR_BGR2RGB)
        if elapsed_time - initial_time > running_time:
            print("RGB_time : ", elapsed_time - initial_time)
            break
        elif elapsed_time - initial_time < running_time:
            RGB_frames.append(RGB_frame)
            _times.append(elapsed_time - initial_time)
            elapsed_time = time.clock()
    print(RGB_frame.dtype)
    fps = len(RGB_frames) / running_time
    print("RGB_elapsedtime", elapsed_time)
    print("RGB_initialtime", initial_time)
    print("Number of frame : ", len(RGB_frames))
    print("estimated fps : ", )
    with open(txt_file, 'a') as f:
        f.write("estimated RGB_fps={}\n".format(fps))
    f.close()
    SaveTIFF(RGB_frames, output_dir)
    SaveMP4(RGB_frames, output_dir, fps)

if __name__ == '__main__':

    # 保存先を作成-------------------------------------------------
    while True:
        OUTPUT_DIR = input("保存するフォルダ名を入力してください：")
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            txt_file = os.path.join(OUTPUT_DIR, "info.txt")
            break
        else:
            folder = input("exist directory! Ignore?(y/n):")
            if folder == "y":
                txt_file = os.path.join(OUTPUT_DIR, "info.txt")
                break

    # 計測時間の設定-----------------------------------------------
    running_time = int(input("Put recording time:"))
    # 取得サンプル数
    N_SAMPLE = int(SAMPLING_RATE * running_time)

    # bitalinoを接続する-------------------------------------------
    device = BITalino(MAC_ADDRESS)
    device.battery(BATTERY_THRESHOLD)
    device.start(SAMPLING_RATE, ACQUIRED_CHANNEL)
    data = []
    _signals = []
    _times = []

    # bosonを接続する----------------------------------------------
    # 16bitで動画を保存するための設定
    camera1 = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    camera1.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y', '1', '6', ''))
    camera1.set(cv2.CAP_PROP_CONVERT_RGB, False)
    u16_frames = []
    u16_times = []

    # RGBカメラを接続する-------------------------------------------
    RGB_port = int(input("RGB port number(0 ~ 4):"))
    camera2 = cv2.VideoCapture(int(RGB_port))
    ret, RGB_frame = camera2.read()
    # frameを表示
    cv2.imshow('camera capture', RGB_frame)
    RGB_frames = []
    RGB_times = []

    # p1 = threading.Thread(target=workerForBItalino, args=(device, N_SAMPLE, data, _times, _signals, OUTPUT_DIR))
    p2 = threading.Thread(target=workerForBoson, args=(camera1, running_time, txt_file, u16_frames, u16_times, OUTPUT_DIR))
    p3 = threading.Thread(target=workerForRGB, args=(camera2, running_time, txt_file, RGB_frames, RGB_times, OUTPUT_DIR))

    # 計測開始
    print("start")
    # p1.start()
    p2.start()
    p3.start()

    # p1.join()
    p2.join()
    p3.join()
    print("end")