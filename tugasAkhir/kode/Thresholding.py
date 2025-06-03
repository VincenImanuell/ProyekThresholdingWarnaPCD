import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load image
bgr_image = cv2.imread('hey.png')  # Replace with your image filename
rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

# Step 1: Convert RGB to HSV
hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)

# Step 2: Define HSV Thresholds (Example: Red)
# Note: Red wraps around 0° in hue, so we usually need two ranges
lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])

lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([179, 255, 255])

# Step 3: Create masks for red range and combine them
mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
mask = cv2.bitwise_or(mask1, mask2)

# Optional: visualize just the red parts in HSV
hsv_filtered = cv2.bitwise_and(hsv_image, hsv_image, mask=mask)

# Step 4: Convert HSV filtered image to RGB
rgb_filtered = cv2.cvtColor(hsv_filtered, cv2.COLOR_HSV2RGB)

# Step 5: Convert RGB to Grayscale
gray_image = cv2.cvtColor(rgb_filtered, cv2.COLOR_RGB2GRAY)

# Step 6: Convert Grayscale back to RGB
gray_to_rgb = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2RGB)

# Step 7: Display Results
plt.figure(figsize=(15, 5))

plt.subplot(1, 4, 1)
plt.title("Original RGB")
plt.imshow(rgb_image)
plt.axis("off")

plt.subplot(1, 4, 2)
plt.title("HSV Filtered")
plt.imshow(rgb_filtered)
plt.axis("off")

plt.subplot(1, 4, 3)
plt.title("Grayscale")
plt.imshow(gray_image, cmap='gray')
plt.axis("off")

plt.subplot(1, 4, 4)
plt.title("Gray to RGB")
plt.imshow(gray_to_rgb)
plt.axis("off")

plt.tight_layout()
plt.show()
