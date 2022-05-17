# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 19:58:23 2020

@author: Yusuf Çiçek
"""

import sys
from PyQt6.QtWidgets import QWidget, QToolTip, QPushButton, QApplication
from PyQt6.QtGui import QFont
import numpy as np
import cv2 as cv


class AirCanvas:

    cap = cv.VideoCapture(0)
    ret, frame = cap.read()

    Points = []
    x, y, width, height = 0, 0, 640, 480
    track_window = (x, y, width, height)

    roi = frame[y : y + height, x : x + width]

    hsv_roi = cv.cvtColor(roi, cv.COLOR_BGR2HSV)

    # l_b = np.array([50, 100, 50])
    # u_b = np.array([65, 230, 150])

    # mask = cv.inRange(hsv_roi, l_b, u_b)

    # roi_hist = cv.calcHist([hsv_roi], [0], mask, [180], [0, 180])

    roi_hist = cv.calcHist([hsv_roi], [0], None, [180], [0, 180])

    cv.normalize(roi_hist, roi_hist, 0, 255, cv.NORM_MINMAX)

    term_crit = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)

    Lines = np.array([], np.int32)
    quit = 0

    @classmethod
    def AirCanvas_Start(cls):
        cls.quit = 0
        while cls.cap.isOpened():
            cls.ret, cls.frame = cls.cap.read()
            cls.frame = cv.flip(cls.frame, 1)

            if cls.ret == True:

                cls.hsv = cv.cvtColor(cls.frame, cv.COLOR_BGR2HSV)
                cls.dst = cv.calcBackProject([cls.hsv], [0], cls.roi_hist, [0, 180], 1)

                cls.ret, cls.track_window = cv.CamShift(
                    cls.dst, cls.track_window, cls.term_crit
                )

                cls.pts = cv.boxPoints(cls.ret)
                cls.pts = np.int0(cls.pts)

                cls.frame = cv.putText(
                    cls.frame,
                    "Quit for ESC",
                    (20, 40),
                    cv.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                    cv.LINE_AA,
                )

                cls.frame = cv.polylines(cls.frame, [cls.pts], True, (0, 0, 255), 3)

                cls.Lines = np.append(cls.Lines, cls.pts[0])

                for index, _ in enumerate(cls.Lines):
                    if index >= 3 and index % 2 != 0:
                        cv.line(
                            cls.frame,
                            (cls.Lines[index - 3], cls.Lines[index - 2]),
                            (cls.Lines[index - 1], cls.Lines[index]),
                            (0, 0, 0),
                            3,
                        )
                        if index == len(cls.Lines) - 2:
                            break

                cv.imshow("Air Canvas", cls.frame)
                cls.k = cv.waitKey(24) & 0xFF

                if cls.k == 27 or cls.quit == 1:
                    break

            else:
                break

        cv.destroyAllWindows()

    @classmethod
    def AirCanvas_Clear(cls):
        cls.Lines = np.array([], np.int32)

    @classmethod
    def AirCanvas_Stop(cls):
        cls.quit = 1
        cls.cap.release

    @classmethod
    def AirCanvas_FindPoints(cls):

        while cls.cap.isOpened():
            cls.ret, cls.frame = cls.cap.read()
            cls.frame = cv.flip(cls.frame, 1)

            cls.frame = cv.putText(
                cls.frame,
                "Please click your shape's two corners",
                (0, 40),
                cv.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
            cls.frame = cv.putText(
                cls.frame,
                "And press ESC for quit",
                (0, 80),
                cv.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
            cv.imshow("First Frame", cls.frame)
            cv.setMouseCallback("First Frame", cls.click_event)

            if cv.waitKey(24) == 27:
                break

        cv.destroyAllWindows()
        cls.x = cls.Points[0][0]
        cls.y = cls.Points[0][1]
        cls.width = cls.Points[1][0] - cls.x
        cls.height = cls.Points[1][1] - cls.y

    @classmethod
    def click_event(cls, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            strXY = str(x) + ", " + str(y)
            cv.putText(
                cls.frame, strXY, (x, y), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1
            )
            cv.imshow("First Frame", cls.frame)
            cls.Points.append((x, y))


class MyAppClass(QWidget, AirCanvas):
    def __init__(self):
        QWidget.__init__(self)
        AirCanvas.__init__(self)
        self.start_window()

    def start_window(self):
        QToolTip.setFont(QFont("verdana", 14))
        self.setToolTip("First you are supposed to find the corners of your shape")

        find_button = QPushButton("Find your shape corners", self)
        find_button.clicked.connect(self.AirCanvas_FindPoints)
        find_button.move(100, 50)

        start_button = QPushButton("Start the Air Canvas", self)
        start_button.clicked.connect(self.AirCanvas_Start)
        start_button.move(100, 100)

        clear_button = QPushButton("Clear the screen", self)
        clear_button.clicked.connect(self.AirCanvas_Clear)
        clear_button.move(100, 150)

        stop_button = QPushButton("Exit", self)
        stop_button.clicked.connect(self.stop_window)
        stop_button.move(100, 200)

        self.setGeometry(350, 300, 300, 300)
        self.setWindowTitle("Air Canvas App")
        self.show()

    def stop_window(self):
        self.AirCanvas_Stop()
        sys.exit()


if __name__ == "__main__":
    application = QApplication(sys.argv)
    window = MyAppClass()
    application.exit(application.exec())
