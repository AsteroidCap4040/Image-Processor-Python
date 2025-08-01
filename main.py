import os
from PIL import Image

def image_resize_dimension(image, dimensions):
    """Resize image by height while preserving aspect ratio."""
    original_size = image.size
    if original_size[0] == original_size[1]:
        new_size = (dimensions, dimensions)
    else:
        ratio = original_size[0] / original_size[1]
        height = dimensions
        width = int(dimensions * ratio)
        new_size = (width, height)

    resized_image = image.resize(new_size)
    print(f"Original Size: {original_size[0]} x {original_size[1]}")
    print(f"New Size: {resized_image.size[0]} x {resized_image.size[1]}")
    
    return resized_image

def image_resize_filesize(image, output_path, target_kb, step=5, min_quality=10):
    """Resize image by reducing quality to achieve target file size in KB."""
    quality = 95

    while quality >= min_quality:
        image.save(output_path, quality=quality, optimize=True)
        size_kb = os.path.getsize(output_path) / 1024
        if size_kb <= target_kb:
            return True
        quality -= step

    return False



# === USER INTERFACE START ===
image_path = "sample2.jpg"
download_path = r"C:\Users\pvdev\Downloads"
output_path = os.path.join(download_path, "final_resized.jpg")

# Load image
img = Image.open(image_path)

# Ask user what they want to do
mode = input("Resize by 'dimension', 'filesize', or 'both'? ").strip().lower()

if mode == "dimension":
    new_height = int(input("Enter desired image height: "))
    resized = image_resize_dimension(img, new_height)
    resized.save(output_path)
    print("Image resized by dimension and saved successfully!")

elif mode == "filesize":
    target_kb = int(input("Enter target file size in KB: "))
    success = image_resize_filesize(img, output_path, target_kb)
    if success:
        print("Image resized by file size and saved successfully!")
    else:
        print("Failed to reach target file size.")

elif mode == "both":
    new_height = int(input("Enter desired image height: "))
    target_kb = int(input("Enter target file size in KB: "))
    resized = image_resize_dimension(img, new_height)
    success = image_resize_filesize(resized, output_path, target_kb)
    if success:
        print("Image resized by dimension + file size and saved successfully!")
    else:
        print("Resized image saved but couldn't reach desired file size.")

else:
    print("Invalid option. Please choose 'dimension', 'filesize', or 'both'.")
