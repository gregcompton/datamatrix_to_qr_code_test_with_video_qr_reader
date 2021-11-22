import cv2
from pyzbar import pyzbar
from pylibdmtx.pylibdmtx import decode
from PIL import Image
from time import time
import qrcode
import os


def read_barcodes(frame):
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        x, y, w, h = barcode.rect

        # 1
        barcode_info = barcode.data.decode('utf-8')
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 2
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcode_info, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)

        # 3
        with open("barcode_result.txt", mode='w') as file:
            file.write("Recognized Barcode:" + barcode_info)
    return frame

def read_datamatrix(image_file):
    print('Opening image file: ', image_file)
    image = Image.open(image_file)
    print('Starting datamatrix decode. Please wait...')
    result = decode(image)
    if result:
        decoded_data = result[0].data
        print('Decoded data: ', decoded_data)
    else:
        print('ERROR: The image file had no data')
        return False
    return decoded_data

def get_image():
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("PRESS SPACEBAR TO CAPTURE IMAGE")
    img_counter = 0

    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("PRESS SPACEBAR TO CAPTURE IMAGE", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "camera_images/opencv_frame_{}.png".format(int(time()))
            cv2.imwrite(img_name, frame)
            print("Image captured! {} written!".format(img_name))
            img_counter += 1
            break
    cam.release()
    cv2.destroyAllWindows()
    return img_name

def generate_qrcode(data, img_name):
    img = qrcode.make(data)
    img.save(img_name)
    return img

def main():

    # datamatrix to qr code from camera capture
    # todo: change to True to use this function
    if True:
        # ensure image folders exist
        folders = ['camera_images', 'qrcodes', 'failed_image_captures']
        for folder in folders:
            if not os.path.isdir(folder):
                os.mkdir(folder)

        # capture datamatrix image, decode the datamatrix
        camera_image_name = get_image()
        data = read_datamatrix(camera_image_name)

        # convert datamatrix data into str format, and rename the image files
        if not data:
            os.rename(camera_image_name, 'failed_image_captures/' + str(int(time())) + '.png')

        else:
            if type(data) == bytes:
                data = data.decode('utf-8')
            new_filename = 'camera_images/' + data + '-' + str(int(time())) + '.png'
            os.rename(camera_image_name, new_filename)

            # create the qr code
            qr_image_name = 'qrcodes/'+ data + '-QR.png'
            generate_qrcode(data, qr_image_name)

            # verify that qr code data matches datamatrix data
            img = cv2.imread(qr_image_name)
            det = cv2.QRCodeDetector()
            val, pts, st_code = det.detectAndDecode(img)

            print('qrcode: ', val)
            print('datamatrix: ', data)
            print("Does the data match: ", val == data)

        exit(1)


    # read qr code in video using pyzbar library
    # todo: change to True to use this function
    # https://towardsdatascience.com/building-a-barcode-qr-code-reader-using-python-360e22dfb6e5
    if True:
        # begin read qr code in video
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()

        while ret:
            ret, frame = camera.read()
            frame = read_barcodes(frame)
            cv2.imshow('Barcode/QR code reader', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        camera.release()
        cv2.destroyAllWindows()

        # end read qr code in video


if __name__ == '__main__':
    main()