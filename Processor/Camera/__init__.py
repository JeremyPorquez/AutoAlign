import cv2
import numpy as np
import os
from PyQt5 import QtCore
from multiprocessing.pool import ThreadPool

if 'arm' in os.uname().machine.lower():
    machine = 'pi'
    from picamera import PiCamera
    from picamera import PiCameraCircularIO
    from picamera import PiVideoFrameType
else:
    machine = 'standard'

class cvCamera(object):
    def __init__(self, id=0):
        self.videoCapture = cv2.VideoCapture(id)
        self.capture()

    def capture(self):
        rval, image_cv = self.videoCapture.read()
        self.image = cv2.flip(image_cv, 1)

class RPiCamera(object):
    def __init__(self):
        self.camera = PiCamera()
        self.camera.awb_gains = 1  # between 0 and 8
        self.camera.awb_mode = 'off'
        self.camera.exposure_mode = 'off'
        self.camera.image_denoise = 'off'
        self.camera.iso = 100
        self.camera.shutter_speed = 1000
        self.image = np.zeros((480, 640, 3), dtype=np.uint8)

    def capture(self):
        self.camera.capture(self.image, format='bgr',
                            resize=(640, 480),
                            use_video_port=True)  # makes acquisition faster but lower quality

class Camera(object):
    class Signal(QtCore.QObject):
        imageCaptured = QtCore.pyqtSignal()

    def __init__(self):
        self.signal = self.Signal()
        if machine == 'pi':
            self.camera = RPiCamera()
        else:
            self.camera = cvCamera()


    def start_capture(self):
        pool = ThreadPool()
        self.capturing = True

        def continuous_capture(signal):
            while self.capturing:
                self.camera.capture()
                self.image = self.camera.image
                signal.emit()
            self.camera.close()

        args = (self.signal.imageCaptured,)

        pool.apply_async(continuous_capture, args)

    def stop_capture(self):
        self.capturing = False