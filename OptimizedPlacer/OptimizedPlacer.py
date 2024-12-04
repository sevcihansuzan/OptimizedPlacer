import tkinter as tk
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, box
from shapely.affinity import rotate, translate, scale
import numpy as np

# Construct the main panel
root = tk.Tk()
root.title("Coordinate Panel")
root.geometry("900x900")

# A list to handle the coordinates of points provided by the user
global click_coordinates 
click_coordinates = []

# A function to add points to the clicked coordinates and show them
def on_click(event):
    x, y = event.x, event.y
    click_coordinates.append((x, y))
    
    # Adds a blue point to the clicked coordinate
    size = 5  # size of the point
    canvas.create_oval(x - size, y - size, x + size, y + size, fill="blue")

# To create a new canvas after the next button is clicked 
def on_next_button():
    # Remove the old panel and canvas 
    for widget in root.winfo_children():
        widget.destroy()
    
    # Create new canvas
    global new_canvas
    new_canvas = tk.Canvas(root, width=700, height=700, bg="white", bd=2, relief="solid")
    new_canvas.pack(pady=0, padx=0)

    # Calculate the edge points to create convex hull 
    if len(click_coordinates) > 2:
        
        points = np.array(click_coordinates)
        hull = ConvexHull(points)
        
        # Connect the points
        for simplex in hull.simplices:
            x1, y1 = points[simplex[0]]
            x2, y2 = points[simplex[1]]
            new_canvas.create_line(x1, y1, x2, y2, fill="red", width=2)

    # Add back button
    back_button = tk.Button(root, text="BACK", font=("Arial", 10), command=restart_app)
    back_button.pack(side="left", padx=10, pady=10)
    
    # Add next button
    next_button = tk.Button(root, text="NEXT", font=("Arial", 10), command=on_next_button_next)
    next_button.pack(side="left", padx=10, pady=10)
    
# Next button function 
def on_next_button_next():
    # Remove the old panel and canvas
    for widget in root.winfo_children():
        widget.destroy()

    # Create new canvas
    global new_canvas
    new_canvas = tk.Canvas(root, width=700, height=700, bg="white", bd=0, relief="solid")
    new_canvas.pack(pady=0, padx=0)

    # Calculate the edge points for convex hull and arrange the coordinates for convex hull placement
    if len(click_coordinates) > 2:
        temp_coord = click_coordinates
        xs= []
        ys = []
        
        for x, y in click_coordinates:
            xs.append(x)
            ys.append(y)
        
        minux = min(xs)
        minuy = min(ys) 

        for i in range(len(xs)):
            xs[i] -= minux
        for j in range(len(ys)):
            ys[j] -= minuy
        
        temp_coord = list(zip(xs,ys))
        
        points = np.array(temp_coord)
        hull = ConvexHull(points)
        
        # Take the edge points for convex hull
        hull_vertices = points[hull.vertices]
        
        # Draw the shape and keep the bounds
        original_shape = Polygon([tuple(point) for point in hull_vertices])
        minx, miny, maxx, maxy = original_shape.bounds

        # Calculate the current width and height of the shape 
        original_width = maxx - minx
        original_height = maxy - miny

        # Calculate the scaling variables 
        scale_x = 50 / original_width
        scale_y = 50 / original_height

        # Scale the shape
        scaled_shape = scale(original_shape, xfact=scale_x, yfact=scale_y, origin=(minx, miny))

    # Arrange the container and angles for placement and start placing the shapes
    container = box(0, 0, 700, 700)  # A box in new canvas size
    angles = [0, 90, 180, 270]  # Rotation angles
    placed_shapes = place_shapes(container, scaled_shape, angles, grid_step=10)

    # Visualization will be on tkinter canvas
    visualize_on_canvas(container, placed_shapes)
    
    # Add back button to the last page
    back_button = tk.Button(root, text="BACK", font=("Arial", 10), command=restart_app)
    back_button.pack(side="left", padx=10, pady=10)
    
    # Calculate the efficency and display it in the rightmost bottom of the canvas
    calculate_efficiency_and_display(container, placed_shapes)
    
def create_rotated_shapes(shape, angles):
    """
    Create rotated versions of the given shape for each angle in the list.
    """
    rotated_shapes = {}
    for angle in angles:
        rotated_shapes[angle] = rotate(shape, angle, origin='centroid', use_radians=False)
    return rotated_shapes

def can_place(candidate, placed_shapes, bounds):
    """
    Check if the candidate shape can be placed without overlapping or going out of bounds.
    """
    if not bounds.contains(candidate):
        return False
    for existing_shape in placed_shapes:
        if candidate.intersects(existing_shape):
            return False
    return True

def place_shapes(rectangle, shape, angles, grid_step=10):
    """
    Place as many rotated instances of a shape as possible into the rectangle.
    """
    bounds = box(*rectangle.bounds)
    rotated_shapes = create_rotated_shapes(shape, angles)
    placed_shapes = []

    # Iterate over grid points within the rectangle
    x_min, y_min, x_max, y_max = rectangle.bounds
    for x in np.arange(x_min, x_max, grid_step):
        for y in np.arange(y_min, y_max, grid_step):
            for angle, rotated in rotated_shapes.items():
                # Translate the rotated shape to the current grid point
                candidate = translate(rotated, xoff=x, yoff=y)
                if can_place(candidate, placed_shapes, bounds):
                    placed_shapes.append(candidate)
                    break  # Proceed to next grid point after placing

    return placed_shapes

def calculate_efficiency_and_display(rectangle, shapes):
    """
    Calculate efficiency and display it on the tkinter canvas.
    """
    # Calculate the total area of placed shapes
    total_area = sum(shape.area for shape in shapes)
    container_area = rectangle.area
    efficiency = (total_area / container_area) * 100

    # Create a white box to display efficiency
    new_canvas.create_rectangle(400, 700, 900, 900, fill="white", outline="black")

    # Display efficiency on the canvas 650 600
    new_canvas.create_text(650, 600, text=f"Efficiency: %{efficiency:.2f}", anchor="se", font=("Arial", 14, "bold"), fill="black")

def visualize_on_canvas(rectangle, shapes):
    """
    Visualize the rectangle and placed shapes on tkinter canvas.
    """
    # Plot the rectangle (container)
    x_min, y_min, x_max, y_max = rectangle.bounds
    new_canvas.create_rectangle(x_min, y_min, x_max, y_max, outline="black")

    # Plot each placed shape
    for shape in shapes:
        x, y = shape.exterior.xy
        coords = []
        for xi, yi in zip(x, y):
            coords.extend([xi, yi])
        new_canvas.create_polygon(coords, outline="blue", fill='', width=2)

# A function to restart the app
def restart_app():
    # Revert the panel to its initial state
    for widget in root.winfo_children():
        widget.destroy()
    
    del click_coordinates[:]     
    create_main_ui()

# A function for the main UI components
def create_main_ui():
    global canvas
    # Create a canvas for the main panel
    canvas = tk.Canvas(root, width=700, height=700, bg="white", bd=2, relief="solid")
    canvas.pack(pady=10, padx=10)

    # Add click sensitivity to panel
    canvas.bind("<Button-1>", on_click)

    # A label for coordinate plane
    label = tk.Label(root)
    label.pack()

    # Next Button
    next_button = tk.Button(root, text="NEXT", font=("Arial", 10), command=on_next_button)
    next_button.place(x=627, y=750)

# Start the app
create_main_ui()
root.mainloop()