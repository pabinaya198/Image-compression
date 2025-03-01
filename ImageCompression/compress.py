import os.path

import numpy as np
from PIL import Image
from scipy.fft import dct, idct


def blockify(image, block_size):
    height, width = image.shape
    return image.reshape(
        height // block_size, block_size, width // block_size, block_size
    ).swapaxes(1, 2).reshape(-1, block_size, block_size)


def un_blockify(blocks, image_shape):
    return blocks.swapaxes(1, 2).reshape(*image_shape)


def build_quantization_matrix(quality=50):
    quality = max(1, min(quality, 100))
    if quality < 50:
        scale = 50 / quality
    else:
        scale = 2 - quality / 50
    quantization_matrix = np.array([
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68, 109, 103, 77],
        [24, 35, 55, 64, 81, 104, 113, 92],
        [49, 64, 78, 87, 103, 121, 120, 101],
        [72, 92, 95, 98, 112, 100, 103, 99]
    ], dtype=float)
    quantization_matrix = np.round(quantization_matrix * scale)
    quantization_matrix[quantization_matrix < 1] = 1
    quantization_matrix[quantization_matrix > 255] = 255
    return quantization_matrix


def compress_image(image, block_size=8, quality=50):
    blocks = blockify(image, block_size)
    dct_blocks = np.zeros_like(blocks, dtype=float)
    for i in range(blocks.shape[0]):
        dct_blocks[i] = dct(dct(blocks[i], axis=0, norm='ortho'), axis=1, norm='ortho')
    quantization_matrix = build_quantization_matrix(quality)
    quantized_blocks = np.round(dct_blocks / quantization_matrix)
    de_quantized_blocks = quantized_blocks * quantization_matrix
    compressed_blocks = np.zeros_like(de_quantized_blocks, dtype=float)
    for i in range(de_quantized_blocks.shape[0]):
        compressed_blocks[i] = idct(idct(
            de_quantized_blocks[i], axis=0, norm='ortho'), axis=1, norm='ortho'
        )
    compressed_image = un_blockify(compressed_blocks, image.shape)
    return compressed_image.astype(np.uint8)


def compress(path, quality=200, optimize=True, progressive=True):
    im_name = os.path.splitext(os.path.basename(path))[0]
    compressed_dir = 'CompressedImages'
    os.makedirs(compressed_dir, exist_ok=True)
    sp = os.path.join(compressed_dir, im_name + '.jpg')
    img = Image.open(path)
    # compress_image(np.array(img.convert('L')))
    img.save(sp, 'JPEG', quality=quality, optimize=optimize, progressive=progressive)
    return sp


if __name__ == '__main__':
    compress('Images/5.3.02.bmp')
