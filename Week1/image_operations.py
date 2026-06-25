

import cv2

# Load the sample image
IMAGE_PATH = "Week1/test.jpg"

# Read image
image = cv2.imread(IMAGE_PATH)

# Check if image loaded successfully
if image is None:
    print(f"Error: Could not load '{IMAGE_PATH}'.")
    print("Place a file named 'test.jpg' in the Week1 folder.")
    exit()

# Original Image
cv2.imshow("Original Image", image)

# Resize image
resized = cv2.resize(image, (600, 400))
cv2.imshow("Resized Image", resized)

# Crop image (center region)
height, width = image.shape[:2]

start_x = width // 4
start_y = height // 4

end_x = start_x + width // 2
end_y = start_y + height // 2

cropped = image[start_y:end_y, start_x:end_x]

cv2.imshow("Cropped Image", cropped)

print(f"Original Size : {width} x {height}")
print(f"Resized Size  : 600 x 400")
print(f"Cropped Size  : {cropped.shape[1]} x {cropped.shape[0]}")

cv2.waitKey(0)
cv2.destroyAllWindows()
