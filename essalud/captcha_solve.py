# -*- coding: utf-8 -*-

import cv2
import numpy as np

class captchaSolve:

    def __init__(self, img, model):
        self.model = model
        self.img = img

    def processingNewImage(self):
        img2gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        #Threshold image
        ret, img_thresh = cv2.threshold(img2gray, 170, 255, cv2.THRESH_BINARY)

        #Crop image after thresholding
        crop0 = img_thresh[:,:24]
        crop1 = img_thresh[:,24:40]
        crop2 = img_thresh[:,40:56]
        crop3 = img_thresh[:,56:76]
        crop4 = img_thresh[:,76:]

        return [crop0, crop1, crop2, crop3, crop4]

    def testingModel(self):
        cropList = self.processingNewImage()

        captchaValue = list()

        for img in cropList:

            x_np = np.zeros((40, 44))

            if img.shape[1]!=44:

                x_np[:, :img.shape[1]] = img
                x_np[:, img.shape[1]:] = [1]

            else:
                x_np = img

            np_value = x_np.flatten()
            np_value = np_value.reshape(1, -1)

            value = self.model.predict(np_value)[0]

            captchaValue.append(value)

        return ''.join(captchaValue)
