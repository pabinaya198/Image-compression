from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider


class Slider(QWidget):
    def __init__(self, parent=None):
        super(Slider, self).__init__(parent=parent)
        self.horiLayout = QHBoxLayout(self)

        self.label = QLabel()
        self.horiLayout.addWidget(self.label)

        self.slider = QSlider()
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.setOrientation(Qt.Horizontal)
        self.horiLayout.addWidget(self.slider)

        self.setLayout(self.horiLayout)
