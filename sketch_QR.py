import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import qrcode
from PIL import Image, ImageTk
import numpy as np
import imageio.v2 as imageio
from scipy.ndimage import gaussian_filter
import cv2

# Global variables
qr_image = None
current_sketch = None


# Function to generate QR code
def generate_qr():
    global qr_image
    link = entry_link.get()
    if not link:
        messagebox.showerror("Error", "Please enter a valid URL.")
        return

    qr = qrcode.QRCode(
        version=10,  # size of the QR Code
        box_size=8,  # size of each box in the QR grid
        border=5  # border size
    )
    qr.add_data(link)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Displaying the QR Code in the GUI
    qr_image.thumbnail((300, 300))
    img_tk = ImageTk.PhotoImage(qr_image)
    label_img_qr.config(image=img_tk)
    label_img_qr.image = img_tk
    label_qr_info.config(text="QR Code generated successfully!")


# Function to save the generated QR code
def save_qr():
    global qr_image
    if qr_image is None:
        messagebox.showerror("Error", "No QR code generated to save.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        title="Save QR Code"
    )

    if file_path:
        qr_image.save(file_path)
        messagebox.showinfo("Success", f"QR Code saved to {file_path}")


# Function to convert RGB to grayscale(The logic to convert is taken from ChatGPT)
def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])


# Function for dodge blend effect (Blends according to the intensity)
def dodge(front, back):
    epsilon = 1e-5  # Avoid division by zero
    blend = cv2.divide(front, 255 - back + epsilon, scale=256)
    return np.clip(blend, 0, 255).astype('uint8')


# Function to convert an image to a sketch
def convert_to_sketch(input_image_path):
    ss = imageio.imread(input_image_path)
    gray = rgb2gray(ss)
    i = 255 - gray
    blur = gaussian_filter(i, sigma=1)
    r = dodge(blur, gray)
    r = cv2.equalizeHist(r.astype('uint8')) #(equalizing onto a 8bit image)
    contrast = 1.4
    brightness = -50  #reducing overexposure dure to overbright image can be adjusted to your image preference
    r = cv2.convertScaleAbs(r, alpha=contrast, beta=brightness)
    return r


# Function to open an image and display its original and sketch version side by side 
def open_image():
    global current_sketch
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        original_image = Image.open(file_path).convert("RGB")
        sketch = convert_to_sketch(file_path)
        # Resize images to fit
        original_image.thumbnail((300, 300))
        sketch_img = Image.fromarray(sketch).convert("RGB")
        sketch_img.thumbnail((300, 300))
        # Create a side-by-side comparison image
        combined_img = Image.new("RGB", (original_image.width + sketch_img.width, max(original_image.height, sketch_img.height)))
        combined_img.paste(original_image, (0, 0))
        combined_img.paste(sketch_img, (original_image.width, 0))
        img_tk = ImageTk.PhotoImage(combined_img)
        label_img_sketch.config(image=img_tk)
        label_img_sketch.image = img_tk
        # Enable save button
        btn_save_sketch.config(state=tk.NORMAL)
        current_sketch = sketch


# Function to save the sketch
def save_sketch():
    if current_sketch is not None:
        save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
        if save_path:
            cv2.imwrite(save_path, current_sketch)
            messagebox.showinfo("Success", f"Sketch saved at: {save_path}")


# GUI Setup
root = tk.Tk()
root.title("QR Code Generator & Image to Sketch Converter")
root.geometry("650x800")

# Tab layout
tab_control = ttk.Notebook(root)

# QR Code Generator Tab
tab_qr = ttk.Frame(tab_control)
tab_control.add(tab_qr, text='QR Code Generator')

frame_qr = tk.Frame(tab_qr)
frame_qr.pack(pady=20)

label_link = tk.Label(frame_qr, text="Enter Link:", font=("Arial", 14))
label_link.pack(pady=5)

entry_link = tk.Entry(frame_qr, width=30, font=("Arial", 14))
entry_link.insert(0, "www.linkedin.com/in/parth-kale13")
entry_link.pack(pady=5)

btn_generate_qr = tk.Button(frame_qr, text="Generate QR Code", command=generate_qr, font=("Arial", 14))
btn_generate_qr.pack(pady=10)

label_qr_info = tk.Label(frame_qr, text="", font=("Arial", 12))
label_qr_info.pack(pady=5)

label_img_qr = tk.Label(tab_qr)
label_img_qr.pack()

btn_save_qr = tk.Button(tab_qr, text="Save QR Code", command=save_qr, font=("Arial", 14))
btn_save_qr.pack(pady=10)

# Image to Sketch Converter Tab
tab_sketch = ttk.Frame(tab_control)
tab_control.add(tab_sketch, text='Image to Sketch Converter')

frame_sketch = tk.Frame(tab_sketch)
frame_sketch.pack(pady=20)

btn_open_image = tk.Button(frame_sketch, text="Open Image", command=open_image, font=("Arial", 14))
btn_open_image.pack(pady=10)

label_img_sketch = tk.Label(tab_sketch)
label_img_sketch.pack()

btn_save_sketch = tk.Button(tab_sketch, text="Save Sketch", command=save_sketch, font=("Arial", 14))
btn_save_sketch.pack(pady=10)
btn_save_sketch.config(state=tk.DISABLED)

# Display tabs
tab_control.pack(expand=1, fill="both")

root.mainloop()
