# データを保存する
import csv
import numpy as np
import os
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import time
from signal_processing import *
from flirpy.camera.boson import Boson


# bitalinoの保存形式----------------------------------------------------------------------------
from keisoku.signal_processing import ApplyMovingAverageFilter


def WriteSignal2CSV(_times, _signals, _output_dir):
    signal_data = []
    output_path = os.path.join(_output_dir, "signal.csv")
    with open(output_path, 'w', newline="") as f:
        writer = csv.writer(f)
        for i in range(len(_times)):
            writer.writerow([_times[i], _signals[i]])


def WriteSignal2Graph(_times, _signals, _output_dir):
    output_path = os.path.join(_output_dir, "signal.png")
    plt.figure(figsize=(8, 6), dpi=200)
    plt.xticks(fontsize=15)
    plt.xlabel(r"$Running_time[s]$", style='italic', ha='center', fontsize=25,
               fontname="Times New Roman")
    plt.ylabel(r"$Signal$", style='italic',
               ha='center', fontsize=25, fontname="Times New Roman")
    filtered_signals = ApplyMovingAverageFilter(_signals, 5)
    plt.figure()
    plt.plot(_times[3:-3], filtered_signals[3:-3])
    plt.savefig(output_path)


# bosonの保存形式--------------------------------------------------------------------------------
def Convert16to8bit(images_u16):
    maxV, minV = np.amax(images_u16), np.amin(images_u16)
    # maxV, minV = (60000, 50000)
    # print(maxV, minV)
    alpha = 255.0 / (maxV - minV)
    images_u8 = np.add(images_u16, -minV)
    images_u8 = images_u8 * alpha
    images_u8 = images_u8.astype(np.uint8)
    return images_u8

def SaveThermoTIFF(_u16_frames, output_path):
    save_path = os.path.join(output_path, "thermal_video.tiff")
    stack = []
    for u16_frame in _u16_frames:
        stack.append(Image.fromarray(u16_frame))
    stack[0].save(save_path, compression="tiff_deflate", save_all=True, append_images=stack[1:])

def SaveTIFF(RGB_frames, output_path):
    save_path = os.path.join(output_path, "video.tiff")
    stack = []
    for RGB_frame in RGB_frames:
        stack.append(Image.fromarray(RGB_frame))
    stack[0].save(save_path, compression="tiff_deflate", save_all=True, append_images=stack[1:])


def SaveThermoMP4(_u16_frames, output_path, _frame_rate):
    output_path = os.path.join(output_path, "thermal_video.mp4")
    size = (_u16_frames[0].shape[1], _u16_frames[0].shape[0])

    fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    writer = cv2.VideoWriter(output_path, fmt, _frame_rate, size)  # ライター作成
    for u16_frame in _u16_frames:
        u16_frame = np.stack([u16_frame, u16_frame, u16_frame], axis=-1)
        u8_frame = Convert16to8bit(u16_frame)
        writer.write(u16_frame)  # 画像を1フレーム分として書き込み

    writer.release()  # ファイルを閉じる

def SaveMP4(RGB_frames, output_path, _frame_rate):
    output_path = os.path.join(output_path, "video.mp4")
    size = (RGB_frames[0].shape[1], RGB_frames[0].shape[0])

    fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    writer = cv2.VideoWriter(output_path, fmt, _frame_rate, size)  # ライター作成
    for RGB_frame in RGB_frames:
        RGB_frame = np.stack([RGB_frame, RGB_frame, RGB_frame], axis=-1)
        writer.write(RGB_frame)  # 画像を1フレーム分として書き込み

    writer.release()  # ファイルを閉じる
