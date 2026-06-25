import cv2
import numpy as np

canvas = np.zeros((500, 500, 3), dtype=np.uint8)

cv2.line(canvas, (20, 20), (480, 20), (255, 0, 0), 3)

cv2.rectangle(canvas, (50, 60), (200, 200), (0, 255, 0), 3)

cv2.circle(canvas, (350, 130), 60, (0, 0, 255), -1)

cv2.putText(
    canvas,
    "OpenCV Practice",
    (110, 320),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (255, 255, 255),
    2,
)

cv2.imshow("Drawing Shapes", canvas)

cv2.waitKey(0)
cv2.destroyAllWindows()

