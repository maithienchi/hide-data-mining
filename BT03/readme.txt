import constants
from huffman import Huffman 
import jpeg_decoder

import struct 
import numpy as np
from scipy import fftpack
from PIL import Image
from bitarray import bitarray
import matplotlib.pyplot as plt


def dct2(pixels):
    '''
    Hàm biến đổi từ ma trận điểm ảnh sang ma trận hệ số DCT (2 ma trận có cùng shape).
    '''
    return fftpack.dct(fftpack.dct(pixels, axis=0, norm='ortho'), axis=1, norm='ortho')

def idct2(dct_coefs):
    '''
    Hàm biến đổi từ ma trận hệ số DCT sang ma trận điểm ảnh (2 ma trận có cùng shape).
    '''
    return fftpack.idct(fftpack.idct(dct_coefs, axis=0 , norm='ortho'), axis=1, norm='ortho')


def get_header(img_height, img_width, quant_table):
    '''
    Hàm tính chuỗi byte ứng với header của ảnh JPEG.
    (Code được điều chỉnh từ nguồn: https://github.com/reinhrst/pygreypeg.)
    '''
    buf = bytearray()

    def writebyte(val):
        buf.extend(struct.pack(">B", val))

    def writeshort(val):
        buf.extend(struct.pack(">H", val))

    # SOI
    writeshort(0xFFD8)  # SOI marker

    # APP0
    writeshort(0xFFE0)  # APP0 marker
    writeshort(0x0010)  # segment length
    writebyte(0x4A)     # 'J'
    writebyte(0x46)     # 'F'
    writebyte(0x49)     # 'I'
    writebyte(0x46)     # 'F'
    writebyte(0x00)     # '\0'
    writeshort(0x0101)  # v1.1
    writebyte(0x00)     # no density unit
    writeshort(0x0001)  # X density = 1
    writeshort(0x0001)  # Y density = 1
    writebyte(0x00)     # thumbnail width = 0
    writebyte(0x00)     # thumbnail height = 0

    # DQT
    quant_table = quant_table.reshape(-1)
    writeshort(0xFFDB)  # DQT marker
    writeshort(0x0043)  # segment length
    writebyte(0x00)     # table 0, 8-bit precision (0)
    for index in constants.zz:
        writebyte(quant_table[index])

    # SOF0
    writeshort(0xFFC0)  # SOF0 marker
    writeshort(0x000B)  # segment length
    writebyte(0x08)     # 8-bit precision
    writeshort(img_height)
    writeshort(img_width)
    writebyte(0x01)     # 1 component only (grayscale)
    writebyte(0x01)     # component ID = 1
    writebyte(0x11)     # no subsampling
    writebyte(0x00)     # quantization table 0

    # DHT
    writeshort(0xFFC4)                     # DHT marker
    writeshort(19 + constants.dc_nb_vals)  # segment length
    writebyte(0x00)                        # table 0 (DC), type 0 (0 = Y, 1 = UV)
    for node in constants.dc_nodes[1:]:
        writebyte(node)
    for val in constants.dc_vals:
        writebyte(val)

    writeshort(0xFFC4)                     # DHT marker
    writeshort(19 + constants.ac_nb_vals)
    writebyte(0x10)                        # table 1 (AC), type 0 (0 = Y, 1 = UV)
    for node in constants.ac_nodes[1:]:
        writebyte(node)
    for val in constants.ac_vals:
        writebyte(val)

    # SOS
    writeshort(0xFFDA)  # SOS marker
    writeshort(8)       # segment length
    writebyte(0x01)     # nb. components
    writebyte(0x01)     # Y component ID
    writebyte(0x00)     # Y HT = 0
    # segment end
    writebyte(0x00)
    writebyte(0x3F)
    writebyte(0x00)

    return buf

def embed(msg_file, cover_img_file, quant_table, stego_img_file):
    
    # I. Đọc cover img file
    
    cover_img = Image.open(cover_img_file)
    cover_pixels = np.array(cover_img, dtype=np.int)
    height = cover_pixels.shape[0]
    width = cover_pixels.shape[1]
    
    # II. Đọc msg file, chuyển msg thành msg bits, kiểm xem có đủ chỗ nhúng không, thêm 100... vào msg bits
    
    with open(msg_file, 'r') as f:
        msg = f.read()
        
    msg_bits = bitarray()
    msg_bits.fromstring(msg)
   
    capacity = int(cover_pixels.size/64)*26
    if len(msg_bits) + 1 > capacity:
        return False
    
    msg_bits.extend('1' + '0' * (capacity - len(msg_bits) - 1))
    
    # III. Nén jpeg, trong quá trình nén thực hiện nhúng msg bits
    jpeg_bytes = bytearray()
    jpeg_bytes.extend(get_header(height, width, quant_table))
    huf = Huffman()
    
    # Lần lượt duyệt các khối ảnh 8x8 (theo thứ tự từ trái qua phải, từ trên xuống dưới)
    # Với mỗi khối:
    # (1) Trừ 128 rồi tính các hệ số DCT
    # (2) Tính các hệ số quantized DCT
    # (3) Nhúng msg bits vào các hệ số quantized DCT
    # (4) Nén các hệ số quantized DCT bằng thuật toán nén Huffman
    #     Để nén dùng câu lệnh `huf.encode_block(quant_dct_coefs, length)`
    #     Trong đó: 
    #     - `quant_dct_coefs` là mảng 1 chiều các hệ số quantized DCT 
    #       (có được bằng cách duyệt mảng 2 chiều theo thứ tự dích dắc:
    #       đầu tiên, kéo mảng 2 chiều thành mảng một chiều, 
    #       rồi duyệt mảng một chiều này theo mảng chỉ số `constants.zz` đã được định nghĩa sẵn cho bạn)
    #     - `length` là số lượng phần tử của mảng `quant_dct_coefs` tính
    #       từ phần tử đầu cho đến phần tử khác 0 cuối cùng 
    #       (lưu ý: có thể xảy ra trường hợp tất cả phần tử đều bằng 0)
    
    b = 0
    for r in range(0, cover_pixels.shape[0], 8):
        for c in range(0, cover_pixels.shape[1], 8):
            block = cover_pixels[r:(r+8),c:(c+8)]
            dct = dct2(block-128)
            quant_dct = np.round(dct / quant_table).astype(np.int)

            for i in range(8):
                for j in range(8):
                    if i+j > 3 and i+j < 8:
                        quant_dct[i,j] = (quant_dct[i,j]>>1<<1) + msg_bits[b]
                        b += 1

            quant_dct_coefs = quant_dct.flatten()[constants.zz]
            length = np.max(np.nonzero(quant_dct_coefs))+1
            huf.encode_block(quant_dct_coefs, length)
    
    jpeg_bytes.extend(huf.end_and_get_buffer())
    jpeg_bytes.extend(struct.pack(">H", 0xFFD9))  # EOI marker
    
    # IV. Ghi kết quả nén jpeg xuống file
    with open(stego_img_file, 'wb') as f:
        f.write(jpeg_bytes)
    
    return True


def extract(stego_img_file, extr_msg_file):
    
    # Trong quá trình giải nén stego img file, lấy các hệ số quantized dct và bảng quatization
    quant_dct_coefs, quant_table = jpeg_decoder.get_quant_dct_coefs_and_quant_table(stego_img_file)
    #print(quant_dct_coefs.shape, quant_table.shape)
    
    
    extr_msg_bits = bitarray()
    quant_dct = np.array(quant_dct_coefs).reshape(int(quant_dct_coefs.shape[0]/8),8)
    
    for r in range(0, quant_dct.shape[0], 8):
        for c in range(0, quant_dct.shape[1], 8):
            block = quant_dct[r:(r+8),c:(c+8)]
            for i in range(8):
                for j in range(8):
                    if i+j > 3 and i+j < 8:
                        extr_msg_bits.extend((np.binary_repr(block[i,j] & (2**1-1), 1)))
    
    extr_msg_bits = extr_msg_bits[:extr_msg_bits.to01().rfind('1')]
    extr_msg = extr_msg_bits.tostring()
    
    with open(extr_msg_file, 'w') as f:
        f.write(extr_msg)