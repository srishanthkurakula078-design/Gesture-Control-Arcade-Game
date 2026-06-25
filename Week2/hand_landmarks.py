import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="Assets/hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2
)

image = mp.Image.create_from_file("Week2/hand.jpeg")

with HandLandmarker.create_from_options(options) as landmarker:

    result = landmarker.detect(image)

    image_bgr = cv2.imread("Week2/hand.jpeg")
    print(image_bgr.shape)


    height, width = image_bgr.shape[:2]

    for hand in result.hand_landmarks:

        for landmark in hand:

            x = int(landmark.x * width)
            y = int(landmark.y * height)

            cv2.circle(image_bgr, (x, y), 5, (0, 255, 0), -1)

display = cv2.resize(image_bgr, (600, 800))

cv2.imshow("Hand Landmarks", display)

cv2.waitKey(0)
cv2.destroyAllWindows()

