#!/usr/bin/env python

import zlib
import pprint
import time

import pyzbar.pyzbar as pyzbar
import base45
import cbor2
import cv2 # opencv, a library for computer vision

class Scanner:
    """Coordinates barcode scanning and inventory management"""
    def __init__(self):
        self._camerasetup()
        self.has_frame = False
        self.image = None
        self.frame = None

    def _camerasetup(self):
        # camera is the object we’ll use to interact; 0 means use the default camera
        camera = cv2.VideoCapture(0)

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        time.sleep(2)

        self.camera = camera

    def _endcamera(self):
        self.camera.release()
        cv2.destroyAllWindows()

    def _takepix(self):
        self.has_frame, self.frame = self.camera.read()
        if not self.has_frame:
            return
        self.image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

    def _scan(self):
        barcodes = pyzbar.decode(self.image)

        for barcode in barcodes:
            barcode_value = barcode.data.decode("utf-8")

            if barcode.type == "QRCODE":
                return barcode_value

        return None

    def run(self):
        """Sets up the camera and scans until exit"""
        barcode = None
        while self.camera.isOpened() and barcode is None:
            self._takepix()
            if not self.has_frame:
                continue
            barcode = self._scan()
            cv2.imshow('frame', self.frame)
            cv2.waitKey(1)
        self._endcamera()
        return barcode

############# Main #############################################

scanner = Scanner()
cert = scanner.run()
print(f"QRCode content: {cert}")

b45data = cert.replace("HC1:", "")
print()
print(f"Base 45 string: {b45data}")

zlibdata = base45.b45decode(b45data)
print()
print(f"Result of base 45 decode: {zlibdata}")

cbordata = zlib.decompress(zlibdata)
print()
print(f"Result of zlib decompression: {cbordata}")

decoded = cbor2.loads(cbordata)
print()
print(f"Result of CBOR decoding: {decoded}")

print()
print(" -- Payload")
payload = cbor2.loads(decoded.value[2])
print(f"1: issuer of cert: {payload[1]}")
print(f"6: cert issue date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload[6]))}")
print(f"4: cert expiry date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payload[4]))}")
print(f"-260: payload of cert: {pprint.pformat(payload[-260])}")
