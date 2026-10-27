import trimesh
import sys
import matplotlib.pyplot as plt
import numpy as np

fuel_grain = trimesh.load_mesh("fuel_grain.stl")

""" def mesh_to_image(mesh, step, min, max):
    x = min
    y = min
    image = []
    while y < max:
        x = min
        row = []

        while x < max:
            print(x, y)
            row.append(int(mesh.contains([(x, y, 1)])[0]))
            x += step
            x = round(x, 1)

        image.append(row)
        y += step
        y = round(y, 1)

    return image """

def save_image(image, filename):
    np.save(filename, np.asarray(image, dtype=np.uint8))


def load_image(filename):
    return np.load(filename)

def mesh_to_image(mesh, step, z=1, padding=0):
    # Slice the 3D mesh with a horizontal plane
    section = mesh.section(
        plane_origin=[0, 0, z],
        plane_normal=[0, 0, 1]
    )

    if section is None:
        return np.zeros((1, 1), dtype=np.uint8), 0, 0

    # Convert 3D section into 2D
    planar, _ = section.to_planar()
    polygons = planar.polygons_full

    # Get the actual STL bounds
    bounds = planar.bounds
    min_x, min_y = bounds[0]
    max_x, max_y = bounds[1]

    # Make the coordinate system centered at 0, 0
    half_width = max(abs(min_x), abs(max_x))
    half_height = max(abs(min_y), abs(max_y))
    half_size = max(half_width, half_height)

    # Add padding on every side
    half_size += padding

    min_coord = -half_size
    max_coord = half_size

    # Number of pixels
    size = int(np.ceil((max_coord - min_coord) / step))

    # Pixel-center coordinates
    x = min_coord + (np.arange(size) + 0.5) * step
    y = min_coord + (np.arange(size) + 0.5) * step

    X, Y = np.meshgrid(x, y)
    points = np.column_stack((X.ravel(), Y.ravel()))

    # Test points against polygons
    from shapely import contains_xy

    inside = np.zeros(len(points), dtype=bool)

    for polygon in polygons:
        inside |= contains_xy(
            polygon,
            points[:, 0],
            points[:, 1]
        )

    image = inside.reshape((size, size))

    return image.astype(np.uint8), min_coord, max_coord

pixel_size = 0.02  # Size of each pixel in the image
image, min_coord, max_coord = mesh_to_image(
    fuel_grain,
    pixel_size,
    z=1,
    padding=2
)

area = 0
for row in image:
    for col in row:
        area += col * (pixel_size * pixel_size)  # Each pixel represents a pixel_size x pixel_size area

print(area)

def blur_binary(image, radius):
    image = np.asarray(image, dtype=bool)

    height, width = image.shape

    # Create circular kernel
    y, x = np.ogrid[-radius:radius + 1, -radius:radius + 1]
    circle = x**2 + y**2 <= radius**2

    # Output image
    result = image.copy()

    # Find every pixel that is currently filled
    filled_y, filled_x = np.where(image)

    for cy, cx in zip(filled_y, filled_x):
        # Bounds of the circle
        y_min = max(0, cy - radius)
        y_max = min(height, cy + radius + 1)

        x_min = max(0, cx - radius)
        x_max = min(width, cx + radius + 1)

        # Portion of the circular kernel that fits in the image
        kernel_y_min = y_min - (cy - radius)
        kernel_y_max = kernel_y_min + (y_max - y_min)

        kernel_x_min = x_min - (cx - radius)
        kernel_x_max = kernel_x_min + (x_max - x_min)

        # Fill pixels inside the circle
        result[y_min:y_max, x_min:x_max] |= circle[
            kernel_y_min:kernel_y_max,
            kernel_x_min:kernel_x_max
        ]

    return result.astype(int)

save_image(image, "fuel_grain.npy")

def overlay_images(before, after, pixel_size):
    # Get dimensions
    before_h, before_w = before.shape
    after_h, after_w = after.shape

    # Physical half-sizes
    before_half_x = before_w * pixel_size / 2
    before_half_y = before_h * pixel_size / 2

    after_half_x = after_w * pixel_size / 2
    after_half_y = after_h * pixel_size / 2

    # Bounds large enough for BOTH images
    half_x = max(before_half_x, after_half_x)
    half_y = max(before_half_y, after_half_y)

    extent = [
        -half_x,
        half_x,
        -half_y,
        half_y
    ]

    fig, ax = plt.subplots(figsize=(7, 7))

    ax.imshow(
        before,
        origin="lower",
        extent=[
            -before_half_x,
            before_half_x,
            -before_half_y,
            before_half_y
        ],
        cmap="Blues",
        alpha=0.5,
        interpolation="none"
    )

    ax.imshow(
        after,
        origin="lower",
        extent=[
            -after_half_x,
            after_half_x,
            -after_half_y,
            after_half_y
        ],
        cmap="Reds",
        alpha=0.5,
        interpolation="none"
    )

    ax.set_xlim(-half_x, half_x)
    ax.set_ylim(-half_y, half_y)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("Fuel Grain Regression")

    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    plt.show()



after = blur_binary(image, radius=35)

overlay_images(
    image,
    after,
    pixel_size
)
sys.exit()

# Display the shape
plt.imshow(
    image,
    origin="lower",
    extent=[-3, 3, -3, 3],
    interpolation="none"
)

plt.xlabel("X")
plt.ylabel("Y")
plt.title("Fuel Grain Cross Section")
plt.axis("equal")
plt.show()



# Display the shape
plt.imshow(
    blur_binary(image, radius=2),
    origin="lower",
    extent=[-3, 3, -3, 3],
    interpolation="none"
)

plt.xlabel("X")
plt.ylabel("Y")
plt.title("Fuel Grain Cross Section")
plt.axis("equal")
plt.show()