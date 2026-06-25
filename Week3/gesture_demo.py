import cv2

from hand_detector import HandDetector
from gestures import fingersUp, detectGesture


detector = HandDetector()

cap = cv2.VideoCapture(0)

while True:

    success, frame = cap.read()

    if not success:
        break

    frame, lmList = detector.findHands(frame)

    if len(lmList) != 0:

        fingers = fingersUp(lmList)

        gesture = detectGesture(fingers)

        cv2.putText(
            frame,
            gesture,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

    cv2.imshow("Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows() 
