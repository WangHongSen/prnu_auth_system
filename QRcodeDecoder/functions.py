import cv2
import numpy
import os
import sys
from reedsolo import ReedSolomonError
from PIL import Image
from pyzbar.pyzbar import decode
from .qr_detector import extract_matrix, QrDetectorError
from .qr_decoder import extract_bit_array, extract_string, error_correction, \
    get_version_size, get_format_info_data, QrDecoderError

def decoder(img_path):

    image = cv2.imread(img_path,-1)
    if type(image[0][0]).__name__ == 'uint8':
        return str(decode(Image.open(img_path))[0][0], encoding='utf-8')
    image = cv2.blur(image,(5,5))    #进行滤波去掉噪声
    if image is False:
        print('could not open picture')
    else:
        try:
            bit_matrix, image_list = extract_matrix(image, 400)
            mask_index, ecc_level = get_format_info_data(bit_matrix)
            version, size = get_version_size(bit_matrix)
            raw_bit_array, (mask_matrix, dataarea_indicator, bit_matrix_unmasked) = \
                extract_bit_array(bit_matrix, mask_index, True)

            bit_array = error_correction(raw_bit_array, version, ecc_level)
            string = extract_string(bit_array, version) 
        except QrDetectorError as e:
            print('Error while detecting occurred: {}'.format(e), file = sys.stderr)
            #for image, name in e.image_list:
                #cv2.imshow(name, image)
        except ReedSolomonError as e:
            print('Error while applying error correction occurred: {}'.format(e), file = sys.stderr)
        except QrDecoderError as e:
            print('Error while decoding occurred: {}'.format(e), file = sys.stderr)
        else:
            return string 
        return None
if __name__ == "__main__":

    img_path = 'test3.jpg'
    print(decoder(img_path))
    
