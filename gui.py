#Importing Libraries
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import os
import io

# ==================================================== Global Variables & Constants =======================================
directory_path = r"------!!!!!!-------"  # !!!!! Change it to your desired directory !!!!!!!!
loaded_image = None
resized_image = None
inverted_image = None
flipped_image = None
rotated_image = None
compressed_image = None

filetypes = [
    ("All image files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.tif;*.tiff;*.gif;*.ico;*.ppm;*.pgm;*.pbm;*.pnm"),
    ("PNG files", "*.png"),
    ("JPEG files", "*.jpg;*.jpeg"),
    ("WEBP files", "*.webp"),
    ("BMP files", "*.bmp"),
    ("TIFF files", "*.tiff;*.tif"),
    ("GIF files", "*.gif"),
    ("All files", "*.*")
]

#Font & Test Styles
FONT = ("Segoe UI", 10)
BTN_STYLE = {"width": 22, "height": 2, "font": FONT, "bg": "#2c3e50", "fg": "white", "activebackground": "#34495e"}
LABEL_STYLE = {"font": FONT, "bg": "#ecf0f1", "anchor": "w"}

# ================================== Functions ========================================================================
def update_original_size_label(custom_text=None):
    if custom_text:
        original_size_label.config(text=custom_text)
    elif loaded_image:
        size = loaded_image.size
        original_size_label.config(text=f"Original Size: {size[0]} x {size[1]}")
    else:
        original_size_label.config(text="No image loaded.")


def browse_images():
    global loaded_image
    
    #Initialdir -> Default file browse window
    file_input = filedialog.askopenfilename(initialdir=directory_path, title="Select a file", filetypes=filetypes) 
    if not file_input:
        return
    
    loaded_image = Image.open(file_input)
    display_image(loaded_image)
    update_original_size_label()

#Displaying images at the center panel
def display_image(image_to_display):
    resized_for_canvas = image_to_display.resize((400, 400))
    sample_image = ImageTk.PhotoImage(resized_for_canvas)
    canvas.sample_image = sample_image
    canvas.delete("all") #Empty old elements on the Canvas
    canvas.create_image(0, 0, image=sample_image, anchor="nw")

def show_resize_inputs():
    global original_size_label
    if not loaded_image:
        return

    # Clear previous widgets
    for widget in settings_frame.winfo_children():
        widget.destroy()

    # Re-create original size label
    original_size_label = tk.Label(settings_frame, text="")
    original_size_label.pack(pady=5)
    update_original_size_label()

    # Width entry
    tk.Label(settings_frame, text="Width:").pack()
    width_entry = tk.Entry(settings_frame)
    width_entry.pack()

    # Height entry
    tk.Label(settings_frame, text="Height:").pack()
    height_entry = tk.Entry(settings_frame)
    height_entry.pack()

    # Track which field is active
    active_field = {"field": None}

    def on_focus_in_width(event):
        active_field["field"] = "width"

    def on_focus_in_height(event):
        active_field["field"] = "height"

    def on_focus_out(event):
        active_field["field"] = None

    def update_dimensions(event):
        try:
            w_text = width_entry.get()
            h_text = height_entry.get()
            w, h = loaded_image.size
            aspect = w / h

            if active_field["field"] == "width" and w_text:
                new_w = int(w_text)
                height_entry.delete(0, tk.END)
                height_entry.insert(0, str(int(new_w / aspect)))
            elif active_field["field"] == "height" and h_text:
                new_h = int(h_text)
                width_entry.delete(0, tk.END)
                width_entry.insert(0, str(int(new_h * aspect)))
        except:
            pass  # Ignore invalid input

    width_entry.bind("<FocusIn>", on_focus_in_width)
    width_entry.bind("<FocusOut>", on_focus_out)
    width_entry.bind("<KeyRelease>", update_dimensions)

    height_entry.bind("<FocusIn>", on_focus_in_height)
    height_entry.bind("<FocusOut>", on_focus_out)
    height_entry.bind("<KeyRelease>", update_dimensions)

    # Resize and display
    def apply_resize():
        global resized_image
        try:
            new_w = int(width_entry.get())
            new_h = int(height_entry.get())
            resized_image = loaded_image.resize((new_w, new_h))
            display_image(resized_image)
            update_original_size_label(f"New Size: {new_w} x {new_h}")
        except:
            update_original_size_label("Invalid dimensions.")

    tk.Button(settings_frame, text="Apply Resize", command=apply_resize).pack(pady=10)

    # Download resized image
    def download_image():
        if not resized_image:
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpeg")])
        if save_path:
            resized_image.save(save_path)

    tk.Button(settings_frame, text="Download Resized Image", command=download_image).pack(pady=10)

def show_invert_image():
    global loaded_image, inverted_image

    if not loaded_image:
        return

    inverted_image = ImageOps.invert(loaded_image.convert("RGB"))

    # Prevent creating multiple buttons
    for widget in settings_frame.winfo_children():
        widget.destroy()

    def download_image():
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpeg")]
        )
        if save_path:
            inverted_image.save(save_path)
            
    
    result_image = ImageTk.PhotoImage(inverted_image.resize((400, 400)))
    image_canvas = tk.Canvas(settings_frame, width=400, height=400, bg="white")
    image_canvas.image = result_image
    image_canvas.create_image(0, 0, image=result_image, anchor="nw")
    image_canvas.pack()

    tk.Button(settings_frame, text="Download Inverted Image", width=20, height=2, command=download_image).pack(pady=10)

def show_flipped_image():
    global loaded_image, flipped_image

    if not loaded_image:
        return

  
    # Clear the right panel first
    for widget in settings_frame.winfo_children():
        widget.destroy()

    # Canvas to display flipped image
    image_canvas = tk.Canvas(settings_frame, width=400, height=400, bg="white")
    image_canvas.pack()

    def render_image(img):
        result_image = ImageTk.PhotoImage(img.resize((400, 400)))
        image_canvas.image = result_image  # prevent garbage collection
        image_canvas.delete("all")
        image_canvas.create_image(0, 0, image=result_image, anchor="nw")

    def flip_horizontal():
        global flipped_image
        flipped_image = flipped_image.transpose(Image.FLIP_LEFT_RIGHT)
        render_image(flipped_image)

    def flip_vertical():
        global flipped_image
        flipped_image = flipped_image.transpose(Image.FLIP_TOP_BOTTOM)
        render_image(flipped_image)
        
    def reset_flip():
        global flipped_image
        flipped_image = loaded_image
        render_image(flipped_image)

    def download_image():
        if not flipped_image:
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpeg")]
        )
        if save_path:
            flipped_image.save(save_path)

    # Default display (original image)
    flipped_image = loaded_image
    render_image(flipped_image)
    
    options_frame = tk.Frame(settings_frame)
    options_frame.pack(pady=10)
    

    # Buttons
    tk.Button(options_frame, text="Flip Horizontally", width=20, height=2, command=flip_horizontal).grid(column=0, row=0)
    tk.Button(options_frame, text="Flip Vertically", width=20, height=2, command=flip_vertical).grid(column=1, row=0)
    tk.Button(options_frame, text="Reset Flip", width=20, height=2, command=reset_flip).grid(column=2, row=0)
    tk.Button(settings_frame, text="Download Flipped Image", width=20, height=2, command=download_image).pack(pady=10)

def show_rotated_image():
    global loaded_image, rotated_image

    if not loaded_image:
        return
    
    # Clear the right panel first
    for widget in settings_frame.winfo_children():
        widget.destroy()
    
    # Canvas to display flipped image
    image_canvas = tk.Canvas(settings_frame, width=400, height=400, bg="white")
    image_canvas.pack()
    
    def render_image(img):
        result_image = ImageTk.PhotoImage(img.resize((400, 400)))
        image_canvas.image = result_image  # prevent garbage collection
        image_canvas.delete("all")
        image_canvas.create_image(0, 0, image=result_image, anchor="nw")
        
    def rotate_clockwise():
        global rotated_image
        rotated_image = rotated_image.rotate(-90, expand=True) # !!! Keep this in the multiple of 90 !!!
        render_image(rotated_image)
        
    def rotate_anti_clockwise():
        global rotated_image
        rotated_image = rotated_image.rotate(90, expand=True) # !!! Keep this in the multiple of 90 !!!
        render_image(rotated_image)
        
    def reset_flip():
        global rotated_image
        rotated_image = loaded_image
        render_image(rotated_image)
    
    
    def download_image():
        if not rotated_image:
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpeg")]
        )
        if save_path:
            rotated_image.save(save_path)
            
    rotated_image = loaded_image
    render_image(rotated_image)
    
    options_frame = tk.Frame(settings_frame)
    options_frame.pack(pady=10)
    

    # Buttons
    tk.Button(options_frame, text="Rotate Clockwise", width=20, height=2, command=rotate_clockwise).grid(column=0, row=0)
    tk.Button(options_frame, text="Rotate Anti-Clockwise", width=20, height=2, command=rotate_anti_clockwise).grid(column=1, row=0)
    tk.Button(options_frame, text="Reset Flip", width=20, height=2, command=reset_flip).grid(column=2, row=0)
    tk.Button(settings_frame, text="Download Rotated Image", width=20, height=2, command=download_image).pack(pady=10)

def show_convert_image_format():
    global loaded_image

    if not loaded_image:
        return

    # Clear the right panel
    for widget in settings_frame.winfo_children():
        widget.destroy()

    # Get original image format
    original_format = loaded_image.format
    if not original_format:
        original_format = "PNG"  # fallback if format is None

    all_formats = ["PNG", "JPEG", "BMP", "WEBP", "TIFF"] #Add more if you like
    available_formats = [fmt for fmt in all_formats if fmt != original_format.upper()] #Removes the original format from the list

    tk.Label(settings_frame, text=f"Original Format: {original_format}", font=("Arial", 12)).pack(pady=10)

    format_var = tk.StringVar(value=available_formats[0])

    tk.Label(settings_frame, text="Convert to:", font=("Arial", 11)).pack(pady=5)
    tk.OptionMenu(settings_frame, format_var, *available_formats).pack(pady=5)

    def convert_and_save():
        target_format = format_var.get()
        ext = target_format.lower()

        save_path = filedialog.asksaveasfilename(
            defaultextension=f".{ext}",
            filetypes=[(f"{target_format} files", f"*.{ext}")]
        )
        if save_path:
            img = loaded_image.convert("RGB") if target_format in ["JPEG", "BMP"] else loaded_image
            img.save(save_path, format=target_format)

    tk.Button(settings_frame, text="Convert & Save", width=20, height=2, command=convert_and_save).pack(pady=15)

def show_compress_by_filesize():
    global loaded_image, compressed_image

    if not loaded_image:
        return

    # Clear settings panel
    for widget in settings_frame.winfo_children():
        widget.destroy()

    compressed_image = loaded_image

    # Canvas
    image_canvas = tk.Canvas(settings_frame, width=400, height=400, bg="white")
    image_canvas.pack()

    def render_image(img):
        preview = ImageTk.PhotoImage(img.resize((400, 400)))
        image_canvas.image = preview
        image_canvas.delete("all")
        image_canvas.create_image(0, 0, image=preview, anchor="nw")

    def compress_image():
        global compressed_image
        target_kb = target_entry.get()

        try:
            target_kb = int(target_kb)
            format = loaded_image.format if loaded_image.format else "JPEG"

            img = loaded_image.copy()
            quality = 95
            step = 5
            width, height = img.size

            while True:
                buffer = io.BytesIO()
                img.save(buffer, format=format, quality=quality)
                size_kb = buffer.getbuffer().nbytes // 1024

                if size_kb <= target_kb:
                    buffer.seek(0)
                    compressed_image = Image.open(buffer).copy()  # ensure full load
                    render_image(compressed_image)
                    
                    # Acknowledgement message
                    messagebox.showinfo("Success", f"Image successfully reduced to {size_kb} KB., Download IT !!!")
                    return

                if quality > 10:
                    quality -= step
                else:
                    # Resize if quality is already very low
                    width = int(width * 0.9)
                    height = int(height * 0.9)
                    if width < 50 or height < 50:
                        break  # stop if image becomes too small
                    img = img.resize((width, height), Image.Resampling.LANCZOS)

            # Final fallback
            buffer.seek(0)
            compressed_image = Image.open(buffer).copy()
            render_image(compressed_image)
            messagebox.showinfo("Notice", "Could not reach target size exactly. This is the smallest possible.")

        except Exception as e:
            messagebox.showerror("Error", f"Invalid size or error: {e}")

    def download_compressed():
        if not compressed_image:
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=filetypes
        )
        if save_path:
            compressed_image.save(save_path)

    # Input & buttons
    input_frame = tk.Frame(settings_frame)
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="Target Size (KB):").grid(row=0, column=0, padx=5)
    target_entry = tk.Entry(input_frame, width=10)
    target_entry.grid(row=0, column=1, padx=5)

    tk.Button(settings_frame, text="Compress", width=20, height=2, command=compress_image).pack(pady=10)
    tk.Button(settings_frame, text="Download Compressed Image", width=25, height=2, command=download_compressed).pack(pady=5)

    # Default preview
    render_image(loaded_image)



   
# ==== GUI ====
window = tk.Tk()
window.title("Image Processor")
window.configure(bg="#ecf0f1")
window.minsize(800, 500)

# ==== Title ====
title_label = tk.Label(window, text="Image Processor", font=("Segoe UI", 14, "bold"), bg="#ecf0f1", fg="#2c3e50")
title_label.grid(row=0, column=0, columnspan=3, pady=(10, 0))

# ==== Left Panel - Buttons ====
button_frame = tk.Frame(window, bg="#ecf0f1")
button_frame.grid(row=1, column=0, padx=15, pady=20, sticky="ns")

buttons = [
    ("Reduce by dimension", show_resize_inputs),
    ("Reduce by size", show_compress_by_filesize),
    ("Invert the colors", show_invert_image),
    ("Convert the image", show_convert_image_format),
    ("Rotate the image", show_rotated_image),
    ("Flip the image", show_flipped_image),
]

for text, cmd in buttons:
    tk.Button(button_frame, text=text, command=cmd, **BTN_STYLE).pack(pady=4)

# ==== Center Panel - Canvas & Browse ====
image_frame = tk.Frame(window, bg="#ecf0f1")
image_frame.grid(row=1, column=1, padx=15, pady=20, sticky="n")

canvas = tk.Canvas(image_frame, width=400, height=400, bg="#bdc3c7", highlightthickness=0)
canvas.pack()

original_size_label = tk.Label(image_frame, text="No image loaded.", **LABEL_STYLE)
original_size_label.pack(pady=5)

tk.Button(image_frame, text="Browse Images", command=browse_images, **BTN_STYLE).pack(pady=(10, 0))

# ==== Right Panel - Settings ====
settings_frame = tk.Frame(window, bg="#ecf0f1")
settings_frame.grid(row=1, column=2, padx=15, pady=20, sticky="n")

placeholder = tk.Label(settings_frame, text="Settings will appear here", **LABEL_STYLE)
placeholder.pack()

# ==== Mainloop ====
window.mainloop()


