import cv2
import numpy as np

def cartoonify_image(image_path):
    # Load the image
    img = cv2.imread("C:\\Users\\IFtech\\Desktop\\image.jpg")
    if img is None:
        print("Error: Unable to load image.")
        return
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply median blur to reduce noise
    gray_blur = cv2.medianBlur(gray, 7)
    
    # Detect edges using adaptive thresholding
    edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
    
    # Apply bilateral filter to smooth colors while preserving edges
    color = cv2.bilateralFilter(img, d=9, sigmaColor=250, sigmaSpace=250)
    
    # Convert to cartoon by combining edges with color image
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    # Display results
    cv2.imshow("Original", img)
    cv2.imshow("Cartoon", cartoon)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
# Example usage
cartoonify_image('image.jpg')
