# Contains image analysis code used to find laser spot and target spot
# todo : implement machine learning with stochastic gradient descent
import cv2
import time
import os
import numpy as np
from multiprocessing.pool import ThreadPool
from PIL import Image

from PyQt5 import QtCore, QtWidgets, QtGui

if 'arm' in os.uname().machine.lower():
    machine = 'pi'
    from picamera import PiCamera
    from picamera import PiCameraCircularIO
    from picamera import PiVideoFrameType
else:
    machine = 'standard'

class SmartImage(object):

    class Signal(QtCore.QObject):
        updateImage = QtCore.pyqtSignal()
        imageCaptured = QtCore.pyqtSignal()
        centroidCalculated = QtCore.pyqtSignal()

    def __init__(self):
        self.widget = QtWidgets.QLabel()
        self.signal = self.Signal()
        self.setup_signals()
        self.capturing = False
        self.image_cv = None
        self.image_qt = None
        self.apply_filter = False
        self.calculate_centroid = False
        self.show_mask = False
        self.filter_mode = 'rgb'
        self.filter_color = 'red'

    def setup_signals(self):
        self.signal.updateImage.connect(self.update_image)
        self.signal.imageCaptured.connect(self.process_image)

    def filter(self, image, filter_mode=None, filter_color=None):
        if filter_mode is None:
            filter_mode = self.filter_mode
        if filter_color is None:
            filter_color = self.filter_color

        if filter_mode == 'rgb':
            filter = image
            if filter_color == 'red':
                lower_color = np.array([240, 240, 240]) # works best with thorlabs FGL715 colored filter
                upper_color = np.array([255, 255, 255])
            elif filter_color == 'green':
                lower_color = np.array([240, 240, 240])
                upper_color = np.array([255, 255, 255])
            else:  # color == 'blue':
                lower_color = np.array([240, 240, 240])
                upper_color = np.array([255, 255, 255])

        elif filter_mode == 'hsv':
            # gimp HSV = (0-360, 0-100, 0-100)
            # opencv2 HSV = (0-180, 0-255, 0-255)
            filter = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            if filter_color == 'red':
                lower_color = np.array([165, 50, 50])
                upper_color = np.array([185, 255, 255])
            elif filter_color == 'green':
                lower_color = np.array([50, 50, 50])
                upper_color = np.array([80, 255, 255])
            else:  # color == 'blue':
                lower_color = np.array([110, 50, 50])
                upper_color = np.array([130, 255, 255])

        # Threshold the HSV image to get only blue colors, HSV performs better than RGB
        mask = cv2.inRange(filter, lower_color, upper_color)

        # Bitwise-AND mask and original image
        filtered_image = cv2.bitwise_and(image, image, mask=mask)

        # Apply Gaussian adaptive thresholding
        # filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)
        # filtered_image = cv2.medianBlur(filtered_image, 11)
        # filtered_image = cv2.adaptiveThreshold(filtered_image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #                                                cv2.THRESH_BINARY,11,2)
        return filtered_image, mask

    def centroid(self, image):

        if image.shape.__len__() == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        M = cv2.moments(image)

        if M["m00"] > 0 :
            self.centroid_x = float(M["m10"] / M["m00"])
            self.centroid_y = float(M["m01"] / M["m00"])
            self.signal.centroidCalculated.emit()
            return self.centroid_x, self.centroid_y

    def convert_to_qimage(self,image):
        if image.shape.__len__() > 2:
            height, width, byteValue = image.shape
            byteValue = byteValue * width
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
            image_qt = QtGui.QImage(image, width, height, byteValue, QtGui.QImage.Format_RGB888)
        else:
            height, width = image.shape
            byteValue = width
            image_qt = QtGui.QImage(image, width, height, byteValue, QtGui.QImage.Format_Grayscale8)
        return image_qt


    def update_image(self,image = None):
        if image is not None:
            image = QtGui.QPixmap(self.convert_to_qimage(image))
            self.widget.setPixmap(image)
            self.widget.show()

    def process_image(self):
        image = self.image
        mask = None
        filtered_image = None
        if self.apply_filter:
            filtered_image, mask = self.filter(image)

        if self.show_mask:
            if filtered_image is not None:
                image += filtered_image

        if self.calculate_centroid:
            if mask is not None:
                self.centroid(mask)
            else:
                self.centroid(image)
            center = int(self.centroid_x), int(self.centroid_y)
            image = cv2.circle(image, center, 5, [0,255,0])

        self.update_image(image)

    def start_capture(self):
        pool = ThreadPool()
        self.capturing = True

        if machine == 'pi':
            self.camera = PiCamera()
            self.stream = PiCameraCircularIO(self.camera, seconds=10)
            self.camera.capture(self.stream, use_video_port=True)
            self.camera.wait_recording(1)

            def continuous_capture(signal):
                while self.capturing:
                    fps = 10
                    time.sleep(1./fps)
                    self.image = Image.open(self.stream)
                    signal.emit()

            args = (self.signal.imageCaptured)

        else:

            self.videoCapture = cv2.VideoCapture(0)

            def continuous_capture(signal,videoCapture):
                while self.capturing:
                    fps = 10
                    time.sleep(1./fps)
                    rval, image_cv = videoCapture.read()
                    self.image = cv2.flip(image_cv, 1)
                    signal.emit()

            args = (self.signal.imageCaptured, self.videoCapture)

        pool.apply_async(continuous_capture, args)






