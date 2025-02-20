import math
import os.path
import sys
import traceback

import numpy as np
import pandas as pd
import prettytable
from PIL import Image
from PyQt5.QtCore import (
    pyqtSlot,
    QObject,
    pyqtSignal,
    QRunnable,
)
from ssim import compute_ssim


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            print(e)
            traceback.print_exc()
            exc_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exc_type, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


def print_df_to_table(df, hline=prettytable.ALL):
    field_names = list(df.columns)
    p_table = prettytable.PrettyTable(field_names=field_names, hrules=hline)
    p_table.add_rows(df.values.tolist())
    return (
        "\n".join(
            [
                "{0}".format(p_)
                for p_ in p_table.get_string().splitlines(keepends=False)
            ]
        )
    )


def mse(im1, im2):
    return np.mean((im1 - im2) ** 2)


def psnr(mse_):
    if mse_ == 0:
        return float('inf')
    return 20 * math.log10(255.0 / math.sqrt(mse_))


def ssim(im1, im2):
    return compute_ssim(im1, im2)


def eval_single(p1, p2):
    print(p1, p2)
    im1 = Image.open(p1)
    im2 = Image.open(p2)
    mse_ = mse(np.array(im1).ravel(), np.array(im2).ravel())
    psnr_ = psnr(mse_)
    ssim_ = ssim(im1, im2)
    im1_size = os.path.getsize(p1)
    im2_size = os.path.getsize(p2)
    c_ratio = im1_size / im2_size
    metrics = [
        '{0:.2f}KB'.format(im1_size / 1024),
        '{0:.2f}KB'.format(im2_size / 1024),
        '{0:.2f}'.format(c_ratio),
        '{0:.2f}'.format(mse_),
        '{0:.2f}'.format(psnr_),
        '{0:.2f}'.format(ssim_),
    ]
    return print_df_to_table(pd.DataFrame(
        [metrics],
        columns=['Image Size', 'Compressed Image Size', 'Compression Ratio', 'MSE', 'PSNR', 'SSIM']
    ))
