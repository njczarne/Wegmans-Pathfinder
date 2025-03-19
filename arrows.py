import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def reportGraph(path):
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Separate x and y coordinates
    x, y = zip(*path)

    # Plot the path
    ax.plot(x, y, color='#00008B', linewidth=2, zorder=1) 

    # Add direction arrows
    for i in range(len(path) - 1):
        dx = path[i+1][0] - path[i][0]
        dy = path[i+1][1] - path[i][1]
        ax.arrow(path[i][0], path[i][1], dx, dy,
                 head_width=0.2, head_length=0.2, fc='r', ec='r',
                 length_includes_head=True, color='#00008B', zorder=2)
    # top aisles
    rect = Rectangle((0.5, 0.5), 1, 3, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    rect = Rectangle((2.5, 0.5), 1, 3, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    rect = Rectangle((4.5, 0.5), 1, 3, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    rect = Rectangle((6.5, 0.5), 1, 3, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    # bottom aisles
    rect = Rectangle((0.5, 5.5), 1, 3, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    rect = Rectangle((2.5, 5.5), 1, 3, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    rect = Rectangle((4.5, 5.5), 1, 3, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    rect = Rectangle((6.5, 5.5), 1, 3, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    # side aisles
    rect = Rectangle((8.5, 2.5), 1, 1, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    rect = Rectangle((8.5, 4.5), 1, 1, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    rect = Rectangle((8.5, 6.5), 1, 1, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)
    rect = Rectangle((8.5, 8.5), 1, 1, facecolor='black', edgecolor='gray', zorder=0)
    ax.add_patch(rect)

    # Set the limits and invert the y-axis
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(9.5, -0.5)

    # Add grid lines
    ax.grid(True, linestyle='--', alpha=0.7)

    # Move x-axis to the top
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')

    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Optimal Grocery Store Route')

    return fig, ax



