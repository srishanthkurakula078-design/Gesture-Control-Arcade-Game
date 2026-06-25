import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="Assets/hand_landmarker.task"),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2
)

with HandLandmarker.create_from_options(options) as landmarker:

    image = mp.Image.create_from_file("Week2/hand.jpeg")

    result = landmarker.detect(image)

    print("Number of hands detected:", len(result.hand_landmarks))

    for i, hand in enumerate(result.hand_landmarks):
        print(f"\nHand {i+1}")

        for j, landmark in enumerate(hand):
            print(
                f"Landmark {j}: "
                f"x={landmark.x:.3f}, "
                f"y={landmark.y:.3f}, "
                f"z={landmark.z:.3f}"
            )

    image_bgr = cv2.imread("Week2/hand.jpeg")

    cv2.imshow("Input Image", image_bgr)

    cv2.waitKey(0)

cv2.destroyAllWindows()
