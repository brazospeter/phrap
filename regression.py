import trimesh
import sys
import matplotlib.pyplot as plt
import numpy as np

from image import Image

file_name = "image.npy"
save = False
pixel_size = 0.1 # 1 inch per x pixel

def mesh_to_image(mesh, step, min, max):
    x = min
    y = min
    image = []
    while y < max:
        print(str(round(100 * ((y - min)) / ((max - min)), 1)) + "%")
        x = min
        row = []

        while x < max:
            row.append(int(mesh.contains([(x, y, 1)])[0]))
            x += step
            x = round(x, 1)

        image.append(row)
        y += step
        y = round(y, 1)

    return image

def save_image(image, filename):
    np.save(filename, np.asarray(image, dtype=np.uint8))

def load_image(filename):
    return np.load(filename)


if save:
    fuel_grain = trimesh.load_mesh("fuel_grain.stl")
    image = Image(mesh_to_image(fuel_grain, pixel_size, -4, 4))

    save_image(image.data, file_name)
else:
    image = load_image(file_name)


def overlay_images(before, after):
    fig, ax = plt.subplots(figsize=(7, 7))
    
    ax.imshow(
        before,
        origin="lower",
        cmap="Blues",
    )

    ax.imshow(
        after,
        origin="lower",
        cmap="Reds",
    )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Fuel Grain Regression")

    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    plt.show()

overlay_images(image.data, image.data)