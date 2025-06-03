import cv2
import numpy as np
import matplotlib.pyplot as plt

def create_hue_mask(hsv_img, h_min, h_max, s_min=100, s_max=255, v_min=50, v_max=255):
    lower1 = np.array([0, s_min, v_min])
    upper1 = np.array([0, s_max, v_max])
    lower2 = np.array([0, s_min, v_min])
    upper2 = np.array([0, s_max, v_max])
    
    if h_min <= h_max:
        lower1[0] = h_min
        upper1[0] = h_max
        return cv2.inRange(hsv_img, lower1, upper1)
    else:
        # Wrap-around case
        lower1[0], upper1[0] = h_min, 179
        lower2[0], upper2[0] = 0, h_max
        mask1 = cv2.inRange(hsv_img, lower1, upper1)
        mask2 = cv2.inRange(hsv_img, lower2, upper2)
        return cv2.bitwise_or(mask1, mask2)

# Load image
bgr_image = cv2.imread('two.jpg', cv2.IMREAD_UNCHANGED)

# Handle PNG alpha channel
if bgr_image.shape[2] == 4:
    bgr_image = bgr_image[:, :, :3]

# Convert to RGB and HSV
rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)

# Custom HUE range (wraps from 160 to 20)
hue_min = 35
hue_max = 85

# Create the dynamic mask
mask = create_hue_mask(hsv_image, hue_min, hue_max)

# HSV thresholded result
hsv_filtered = cv2.bitwise_and(hsv_image, hsv_image, mask=mask)
rgb_filtered = cv2.cvtColor(hsv_filtered, cv2.COLOR_HSV2RGB)

# Grayscale from filtered
gray_from_filtered = cv2.cvtColor(rgb_filtered, cv2.COLOR_RGB2GRAY)
gray_filtered_rgb = cv2.cvtColor(gray_from_filtered, cv2.COLOR_GRAY2RGB)

# Grayscale from original
gray_from_original = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
gray_original_rgb = cv2.cvtColor(gray_from_original, cv2.COLOR_GRAY2RGB)

# Color pop: color where mask==1, grayscale elsewhere
color_pop = gray_original_rgb.copy()
color_pop[mask > 0] = rgb_image[mask > 0]

# Plot results
plt.figure(figsize=(18, 8))

plt.subplot(2, 3, 1)
plt.title("Original RGB")
plt.imshow(rgb_image)
plt.axis("off")

plt.subplot(2, 3, 2)
plt.title("HSV Filtered (Custom Hue)")
plt.imshow(rgb_filtered)
plt.axis("off")

plt.subplot(2, 3, 4)
plt.title("Gray from Original")
plt.imshow(gray_original_rgb)
plt.axis("off")

plt.subplot(2, 3, 5)
plt.title("Color Pop (Hue {}-{})".format(hue_min, hue_max))
plt.imshow(color_pop)
plt.axis("off")

plt.tight_layout()
plt.show()
