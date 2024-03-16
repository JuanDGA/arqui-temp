import cv2
import numpy as np
from pyzbar import pyzbar


def detect_face(image_data):
    opencv_image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # Perform face detection
    gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    return len(faces) == 1


def detect_barcode_or_qr(image_data):
    opencv_image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

    # Perform barcode and QR code detection
    barcodes = pyzbar.decode(opencv_image)

    print(barcodes)

    return len(barcodes) > 0
