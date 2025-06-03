import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load image (supports PNG or JPG)
bgr_image = cv2.imread('two.jpg', cv2.IMREAD_UNCHANGED)

# Handle PNG alpha channel (if present)
if bgr_image.shape[2] == 4:
    bgr_image = bgr_image[:, :, :3]

# Convert BGR to RGB
rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

# Convert RGB to HSV
hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)

# Define red color range in HSV
lower_red1 = np.array([0, 100, 100])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 100, 100])
upper_red2 = np.array([179, 255, 255])

# Create mask for red regions
mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
mask = cv2.bitwise_or(mask1, mask2)

# HSV thresholded result (only red parts preserved)
hsv_filtered = cv2.bitwise_and(hsv_image, hsv_image, mask=mask)
rgb_filtered = cv2.cvtColor(hsv_filtered, cv2.COLOR_HSV2RGB)

# Grayscale from HSV-filtered version
gray_from_filtered = cv2.cvtColor(rgb_filtered, cv2.COLOR_RGB2GRAY)
gray_filtered_rgb = cv2.cvtColor(gray_from_filtered, cv2.COLOR_GRAY2RGB)

# Grayscale from original RGB
gray_from_original = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
gray_original_rgb = cv2.cvtColor(gray_from_original, cv2.COLOR_GRAY2RGB)

# Color pop: color where mask==1, grayscale elsewhere
color_pop = gray_original_rgb.copy()
color_pop[mask > 0] = rgb_image[mask > 0]

# Plot everything
plt.figure(figsize=(18, 8))

plt.subplot(2, 3, 1)
plt.title("Original RGB")
plt.imshow(rgb_image)
plt.axis("off")

plt.subplot(2, 3, 2)
plt.title("HSV Filtered (Red)")
plt.imshow(rgb_filtered)
plt.axis("off")

plt.subplot(2, 3, 4)
plt.title("Gray from Original")
plt.imshow(gray_original_rgb)
plt.axis("off")

plt.subplot(2, 3, 5)
plt.title("Color Pop (Red Only)")
plt.imshow(color_pop)
plt.axis("off")

plt.tight_layout()
plt.show()
