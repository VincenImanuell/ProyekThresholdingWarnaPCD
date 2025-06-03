import cv2
import numpy as np
import matplotlib.pyplot as plt

# === 1. Ask user for image file ===
file_name = input("Enter the image file name with extension (e.g., image.png): ")

image_path = f"{file_name}"
bgr_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

if bgr_image is None:
    raise FileNotFoundError(f"Image '{image_path}' not found!")

# === 2. Handle alpha channel (if PNG) ===
if bgr_image.shape[2] == 4:
    bgr_image = bgr_image[:, :, :3]

# === 3. Convert to RGB and HSV ===
rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)

# === 4. Define color presets (hue min, hue max) ===
color_ranges = {
    "red":   (160, 20),
    "green": (35, 85),
    "blue":  (100, 130),
    "yellow": (20, 35),
    "cyan":  (85, 100),
    "purple": (130, 155)
}

# === 5. Ask user for a color ===
print("\nAvailable colors:", ", ".join(color_ranges.keys()))
color_choice = input("Choose a color to filter: ").strip().lower()

if color_choice not in color_ranges:
    raise ValueError(f"Color '{color_choice}' is not in the available presets.")

hue_min, hue_max = color_ranges[color_choice]

# === 6. Dynamic mask creation with wrap-around support ===
def create_hue_mask(hsv_img, h_min, h_max, s_min=100, s_max=255, v_min=50, v_max=255):
    if h_min <= h_max:
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        return cv2.inRange(hsv_img, lower, upper)
    else:
        # Handle wrap-around
        lower1 = np.array([h_min, s_min, v_min])
        upper1 = np.array([179, s_max, v_max])
        lower2 = np.array([0, s_min, v_min])
        upper2 = np.array([h_max, s_max, v_max])
        mask1 = cv2.inRange(hsv_img, lower1, upper1)
        mask2 = cv2.inRange(hsv_img, lower2, upper2)
        return cv2.bitwise_or(mask1, mask2)

# === 7. Create mask and apply filter ===
mask = create_hue_mask(hsv_image, hue_min, hue_max)
hsv_filtered = cv2.bitwise_and(hsv_image, hsv_image, mask=mask)
rgb_filtered = cv2.cvtColor(hsv_filtered, cv2.COLOR_HSV2RGB)

# === 8. Create grayscale versions ===
gray_original = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
gray_rgb = cv2.cvtColor(gray_original, cv2.COLOR_GRAY2RGB)

# === 9. Create color pop version ===
color_pop = gray_rgb.copy()
color_pop[mask > 0] = rgb_image[mask > 0]

# === 10. Plot everything ===
plt.figure(figsize=(18, 8))

plt.subplot(2, 3, 1)
plt.title("Original RGB")
plt.imshow(rgb_image)
plt.axis("off")

plt.subplot(2, 3, 2)
plt.title(f"HSV Filtered ({color_choice})")
plt.imshow(rgb_filtered)
plt.axis("off")

plt.subplot(2, 3, 4)
plt.title("Grayscale from Original")
plt.imshow(gray_rgb)
plt.axis("off")

plt.subplot(2, 3, 5)
plt.title(f"Color Pop ({color_choice})")
plt.imshow(color_pop)
plt.axis("off")

plt.tight_layout()
plt.show()
