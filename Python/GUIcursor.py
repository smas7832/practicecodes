import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import matplotlib.animation as animation

# Create the GUI window
root = tk.Tk()
root.title("Random Animation Around Cursor")

# Set the window size and position
root.geometry("500x500+100+100")

# Create a canvas to render the animation
canvas = tk.Canvas(root, width=500, height=500)
canvas.pack()

# Load some sample images for the animation
images = []
for i in range(10):
    img = Image.open(f"image_{i}.png")
    images.append(ImageTk.PhotoImage(img))

def update_animation():
    # Get the current cursor position
    x, y = root.winfo_pointerxy()

    # Randomly select an image from the list
    img = random.choice(images)

    # Create a random animation around the cursor
    canvas.delete("all")
    canvas.create_image(x, y, image=img)

    # Update the animation every 100ms
    root.after(100, update_animation)

# Start the animation loop
update_animation()

# Run the GUI event loop
root.mainloop()
