import cv2
import numpy as np

# Đọc ảnh từ tệp
image = cv2.imread('image251.jpeg')

# Chuyển đổi không gian màu sang HSV
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Đặt phạm vi màu đỏ
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])

# Tạo mask để chọn màu đỏ trong phạm vi
mask = cv2.inRange(hsv_image, lower_red, upper_red)

# Sử dụng mask để phân đoạn màu đỏ trong ảnh gốc
segmented_image = cv2.bitwise_and(image, image, mask=mask)

# Hiển thị ảnh gốc và ảnh phân đoạn màu đỏ
cv2.imshow('Original Image', image)
cv2.imshow('Segmented Image (Red)', segmented_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
