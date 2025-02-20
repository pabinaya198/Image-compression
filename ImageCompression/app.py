import os
import sys

from PyQt5.QtCore import QThreadPool, Qt
from PyQt5.QtGui import QFont, QImage, QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QGridLayout, QGroupBox, QPushButton, QLabel, \
    QFileDialog, QMessageBox, QProgressBar, QDialog, QCheckBox

from compress import compress
from slider import Slider
from utils import Worker, eval_single


class GUI(QWidget):
    def __init__(self):
        super(GUI, self).__init__()

        app.setFont(QFont('Roboto Mono'))
        self.setWindowTitle("Image Compression")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        self.screen_size = app.primaryScreen().size()
        self.awidth = (self.screen_size.width() // 100) * 60
        self.aheight = (self.screen_size.height() // 100) * 90
        self.setFixedWidth(self.awidth)
        self.setFixedHeight(self.aheight)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        self.gb_1 = QGroupBox("Input Data")

        self.gb_1.setFixedWidth((self.awidth // 100) * 99)
        self.gb_1.setFixedHeight((self.aheight // 100) * 15)
        self.grid_1 = QGridLayout()
        self.grid_1.setSpacing(10)
        self.gb_1.setLayout(self.grid_1)

        self.ci_pb = QPushButton("Choose Image")
        self.ci_pb.clicked.connect(self.choose_input)
        self.grid_1.addWidget(self.ci_pb, 0, 0)

        self.slider = Slider()
        self.slider.setFixedWidth((self.awidth // 100) * 40)
        self.slider.slider.setMinimum(0)
        self.slider.slider.setMaximum(100)
        self.slider.slider.valueChanged.connect(lambda: self.slider.label.setText(
            "Quality::{0}".format(self.slider.slider.value())
        ))
        self.slider.slider.setValue(80)
        self.grid_1.addWidget(self.slider, 0, 1)

        self.opt_btn = QCheckBox('Optimize')
        self.opt_btn.setChecked(True)
        self.grid_1.addWidget(self.opt_btn, 0, 2)

        self.prg_btn = QCheckBox('Progressive')
        self.prg_btn.setChecked(True)
        self.grid_1.addWidget(self.prg_btn, 0, 3)

        self.cmp_pb = QPushButton("Compress")
        self.cmp_pb.clicked.connect(self.compress_thread)
        self.grid_1.addWidget(self.cmp_pb, 0, 4)

        self.gb_2 = QGroupBox("Results")
        self.gb_2.setFixedWidth((self.awidth // 100) * 99)
        self.gb_2.setFixedHeight((self.aheight // 100) * 60)
        self.grid_2 = QGridLayout()
        self.gb_2.setLayout(self.grid_2)

        self.gb_3 = QGroupBox("Performance Metrics")
        self.gb_3.setFixedWidth((self.awidth // 100) * 99)
        self.gb_3.setFixedHeight((self.aheight // 100) * 20)
        self.grid_3 = QGridLayout()
        self.gb_3.setLayout(self.grid_3)

        self.pm_label = QLabel()
        self.grid_3.addWidget(self.pm_label, 0, 0, Qt.AlignCenter)

        self.main_layout.addWidget(self.gb_1)
        self.main_layout.addWidget(self.gb_2)
        self.main_layout.addWidget(self.gb_3)
        self.setLayout(self.main_layout)

        self.img_size = (
            (self.gb_2.height() // 100) * 90,
            (self.gb_2.width() // 100) * 45,
        )
        self.index = 0
        self.img_path = ''
        self.cimg_path = ''
        self.load_screen = Loading()
        self.thread_pool = QThreadPool()
        self.reset()
        self.show()

    def choose_input(self):
        self.reset()
        self.img_path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Choose Input Image",
            directory="Images/",
            options=QFileDialog.DontUseNativeDialog,
            filter="BMP Files (*.bmp);;PNG Files (*.PNG)",
        )
        if os.path.isfile(self.img_path):
            self.ci_pb.setEnabled(False)
            self.slider.setEnabled(True)
            self.opt_btn.setEnabled(True)
            self.prg_btn.setEnabled(True)
            self.cmp_pb.setEnabled(True)
            self.pm_label.setText('')
            self.clear_layout(self.grid_2)
            self.cimg_path = ''
            self.add_image(self.img_path, "Input Image")
        else:
            self.show_message_box(
                "InputImageError", QMessageBox.Critical, "Choose valid image?"
            )

    def compress_thread(self):
        worker = Worker(self.compress_runner)
        self.thread_pool.start(worker)
        worker.signals.finished.connect(self.compress_finisher)
        self.load_screen.setWindowModality(Qt.ApplicationModal)
        self.load_screen.show()

    def compress_runner(self):
        self.cimg_path = compress(self.img_path, quality=self.slider.slider.value(), optimize=self.opt_btn.isChecked(), progressive=self.prg_btn.isChecked())

    def compress_finisher(self):
        self.add_image(self.cimg_path, 'Compressed Image')
        self.load_screen.close()
        self.ci_pb.setEnabled(True)
        self.slider.setEnabled(False)
        self.opt_btn.setEnabled(False)
        self.prg_btn.setEnabled(False)
        self.cmp_pb.setEnabled(False)
        self.pm_label.setText(eval_single(self.img_path, self.cimg_path))

    def add_image(self, im_path, title):
        image_lb = QLabel()
        image_lb.setFixedHeight(self.img_size[0])
        image_lb.setFixedWidth(self.img_size[1])
        image_lb.setScaledContents(True)
        image_lb.setStyleSheet("padding-top: 30px;")
        qimg = QImage(im_path)
        pixmap = QPixmap.fromImage(qimg)
        image_lb.setPixmap(pixmap)
        self.grid_2.addWidget(image_lb, 0, self.index, Qt.AlignCenter)
        txt_lb = QLabel(title)
        self.grid_2.addWidget(txt_lb, 1, self.index, Qt.AlignCenter)
        self.index += 1

    @staticmethod
    def show_message_box(title, icon, msg):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        msg_box.setIcon(icon)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.setWindowModality(Qt.ApplicationModal)
        msg_box.exec_()

    @staticmethod
    def clear_layout(layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            if not item:
                continue
            w = item.widget()
            if w:
                w.deleteLater()

    def reset(self):
        self.ci_pb.setEnabled(True)
        self.slider.setEnabled(False)
        self.opt_btn.setEnabled(False)
        self.prg_btn.setEnabled(False)
        self.cmp_pb.setEnabled(False)
        self.pm_label.setText('')
        self.cimg_path = ''
        self.clear_layout(self.grid_2)


class Loading(QDialog):
    def __init__(self, parent=None):
        super(Loading, self).__init__(parent)
        self.screen_size = app.primaryScreen().size()
        self._width = int(self.screen_size.width() / 100) * 40
        self._height = int(self.screen_size.height() / 100) * 5
        self.setGeometry(0, 0, self._width, self._height)
        x = (self.screen_size.width() - self.width()) // 2
        y = (self.screen_size.height() - self.height()) // 2
        self.move(x, y)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.pb = QProgressBar(self)
        self.pb.setFixedWidth(self.width())
        self.pb.setFixedHeight(self.height())
        self.pb.setRange(0, 0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    app.setFont(QFont("Roboto Mono"))
    builder = GUI()
    sys.exit(app.exec_())
