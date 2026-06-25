import cv2
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


class HandDetector:

    def __init__(self):
        options = HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path="Week3/hand_landmarker.task"
            ),
            running_mode=VisionRunningMode.IMAGE,
            num_hands=1
        )

        self.landmarker = HandLandmarker.create_from_options(options)

    def findHands(self, image):

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = self.landmarker.detect(mp_image)

        landmarkList = []

        if result.hand_landmarks:

            h, w, _ = image.shape

            for hand in result.hand_landmarks:

                for id, lm in enumerate(hand):

                    x = int(lm.x * w)
                    y = int(lm.y * h)

                    landmarkList.append([id, x, y])

                    cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

        return image, landmarkList 
        