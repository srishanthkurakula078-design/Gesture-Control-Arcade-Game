import cv2

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from Week3.hand_detector import HandDetector
from Week4 import gestures

detector = HandDetector()

cap = cv2.VideoCapture(0)

while True:

    success, frame = cap.read()

    if not success:
        break

    frame, lmList = detector.findHands(frame)

    gesture = "NONE"

    if len(lmList) >= 21:
        gesture = gestures.classify(lmList)

    cv2.putText(
        frame,
        gesture,
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Week 4 - Gesture Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
