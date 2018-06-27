from Gui import main
from PyQt5 import QtWidgets
from Processor import ImageAnalyzer


class AutoAlign(object):

    def __init__(self):
        self.image = ImageAnalyzer.SmartImage()
        self.setup_image()
        self.create_ui()
        self.connect_ui()

    def create_ui(self):
        self.mainWindow = QtWidgets.QMainWindow()
        self.ui = main.Ui_MainWindow()
        self.ui.setupUi(self.mainWindow)
        self.ui.imageContainerLayout.addWidget(self.image.widget)
        self.mainWindow.show()

    def connect_ui(self):
        self.ui.apply_filter_checkBox.toggled.connect(self.apply_filter)
        self.ui.get_centroid_checkBox.toggled.connect(self.get_centroid)
        self.ui.show_mask_checkBox.toggled.connect(self.show_mask)
        self.image.signal.centroidCalculated.connect(self.update_centroid)
        self.ui.filter_mode_comboBox.currentIndexChanged.connect(self.connect_filter_mode)
        self.connect_filter_mode()


    def apply_filter(self):
        self.image.apply_filter = self.ui.apply_filter_checkBox.isChecked()

    def connect_filter_mode(self):
        color, mode = self.ui.filter_mode_comboBox.currentText().split()
        self.image.filter_mode = mode
        self.image.filter_color = color

    def get_centroid(self):
        self.image.calculate_centroid = self.ui.get_centroid_checkBox.isChecked()

    def show_mask(self):
        self.image.show_mask = self.ui.show_mask_checkBox.isChecked()

    def update_centroid(self):
        xlabel = 'x : {}'.format(self.image.centroid_x)
        ylabel = 'y : {}'.format(self.image.centroid_y)
        self.ui.centroid_x_label.setText(xlabel)
        self.ui.centroid_y_label.setText(ylabel)

    def setup_image(self):
        # self.image.signal.updateImage.connect(self.update_image)
        self.image.start_capture()

    def update_image(self):
        self.image.widget.setImage(self.image.image)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    qapp = AutoAlign()
    app.exec_()
        