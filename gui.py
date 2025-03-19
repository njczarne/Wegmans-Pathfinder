import tkinter as tk
import os
from tkinter import messagebox
from grocery_algorithm import runrun

# Enable DPI awareness for high-resolution displays
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # 1: Process DPI aware
except Exception as e:
    print(f"Could not set DPI awareness: {e}")

def write_to_file(filename, text):
    # This forces the directed path to be the same path as this Python file you're reading right now
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    file_path = os.path.join(script_dir, filename)
    
    with open(file_path, 'w') as file:
        file.write(text)
    
    print(f"File '{filename}' created and text written in the same folder as the Python script.")

filename = "selected-foods.txt"

root = tk.Tk()
root.title("Select Your Options")
root.geometry("900x900")  # Set the size of the window
root.configure(bg='#222222')  # Background color to dark gray

# Set minimum window size to 900x900
root.minsize(900, 950)

# Header
header_label = tk.Label(root, text="Select Your Items", font=("Trebuchet MS", 24, "bold"), bg='#222222', fg='white')
header_label.pack(pady=20)

food_items = ["Bread", "Bananas", "Apples", "Tomatoes", "Pasta", "Rice", 
              "Onions", "Potatoes", "Cheese", "Yogurt", "Cereal", "Coffee", 
              "Lettuce", "Carrots", "Peanut Butter", "Jam", "Flour", "Olive Oil", 
              "Sugar", "Butter", "Milk", "Eggs", "Beef", "Chicken", "Paper Towel", 
              "Dish Soap", "Frozen Pizzas", "Ice Cream"]

selected_items = []
checkbox_vars = []

def submit_selection():
    global selected_items
    selected_items = [food for var, food in zip(checkbox_vars, food_items) if var.get() == 1]

    # Get the custom items from the entry field
    custom_items = custom_entry.get().split(',')
    custom_items = [item.strip() for item in custom_items if item.strip()]  # Strip whitespace and filter empty strings

    # Add custom items to selected items
    selected_items.extend(custom_items)

    # Display confirmation message
    if selected_items:
        messagebox.showinfo("Selection Confirmed", f"Your selection: {', '.join(selected_items)}")
        print(f"Selected items array: {selected_items}")  # Print array to terminal
        write_to_file(filename, str(selected_items))
        runrun()
    else:
        messagebox.showinfo("No Selection", "You did not select or enter any items.")
    
# Display checkboxes in a 3-column grid
checkbox_frame = tk.Frame(root, bg='#222222')
checkbox_frame.pack(pady=20)

# Adding checkboxes in a grid
for index, food in enumerate(food_items):
    var = tk.IntVar()  # Variable to track the checkbox state (checked/unchecked)
    checkbox = tk.Checkbutton(checkbox_frame, text=food, variable=var, bg='#222222', fg='white', 
                               font=("Trebuchet MS", 14), selectcolor='#222222', activebackground='#222222', 
                               activeforeground='white', highlightthickness=0)  # Remove shadow and set colors
    row = index // 3  # Determine the row index
    col = index % 3   # Determine the column index
    checkbox.grid(row=row, column=col, sticky="w", padx=10, pady=5)  # Use grid for placement
    checkbox_vars.append(var)

# Input field and label for custom selections
custom_label = tk.Label(root, text="Add custom items (comma-separated):", bg='#222222', fg='white', font=("Trebuchet MS", 14))
custom_label.pack(anchor="center", padx=20)

# Adjust the entry field to have a white background and a slightly narrower width
custom_entry = tk.Entry(root, width=50, font=("Trebuchet MS", 14), bg='#181818', fg='#f0f0f0', bd=0)  # White background and flat
custom_entry.pack(anchor="center", padx=20, pady=5)

submit_button = tk.Button(root, text="Submit", command=submit_selection, bg='#732b99', fg='white', font=("Trebuchet MS", 16), bd=0, highlightthickness=0)  # Flat button
submit_button.pack(pady=30)

# Center the checkbox frame
checkbox_frame.pack(expand=True)

root.mainloop()