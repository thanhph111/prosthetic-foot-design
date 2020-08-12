"""Plot the output data.
"""

# Standard library
import os
import json
import matplotlib as maplot
import matplotlib.pyplot as pyplot
from datetime import datetime

# User library
from sub.inputprocess import IS_ANIMATION
from sub.inputprocess import OUTPUT_FILE
from sub.inputprocess import ICON_FILE
from sub.inputprocess import PHOTO_TYPE
from sub.inputprocess import OUTPUT_PHOTO_DIRECTORY


# **json.loads(json_data)
def get_data():
    """Read output file to get data."""
    try:
        with open(OUTPUT_FILE, "r") as file:
            data = json.load(file)[1]
        return data
    except FileNotFoundError:
        print("Data file not found.")
        exit()


def get_objectives(data):
    """Get a list of all first chromosomes' objective values."""
    objectives = [population[0]["objective"] for population in data]
    return objectives


def get_new_values(values):
    """Record any changes higher. Its size is the same as its argument's."""
    new_values = []
    new_value = values[0]
    for value in values:
        if value > new_value:
            new_value = value
        new_values.append(new_value)
    return new_values


def main(values, is_animation=False):
    """Main function to show the plot which could be played with animation."""

    def on_clicked(event):
        """Direct the program when a key is pressed."""

        if event.key == "x":
            # Use this os._exit(0) to close whole window, even when playing
            os._exit(0)

        if event.key == "s":
            # Get time to define image's name
            now = datetime.now()
            current_time = now.strftime("%H-%M-%S")
            plot_name = "Plot" + "-" + current_time

            # Remove left title, then save image
            pyplot.title("", loc="left", pad=20)
            fig.savefig(
                "%s%s%s" % (OUTPUT_PHOTO_DIRECTORY, plot_name, PHOTO_TYPE),
                transparent=False,
                dpi=300,
            )

            # Use this exit(0) to prevent exiting when playing the plot
            # but allow closing when plotting finishes
            exit(0)

    def draw(values):
        """Plot the grid, the line graphs and the titles."""

        # Turn on grid with dashed style
        subplot.yaxis.grid(True, linestyle="dashed")

        # Get list of new higher values
        new_values = get_new_values(values)

        # Plot 2 lines
        subplot.plot(range(len(values)), values)
        subplot.plot(range(len(new_values)), new_values, linewidth=2)

        # Print left plot title
        pyplot.title(
            "Press X to exit\nPress S to save",
            loc="left",
            fontsize=14,
            color="#1F76B4",
            style="italic",
            pad=20,
        )

        # Print right plot title
        pyplot.title(
            f"{'Max objective:':>25}{max(values):>10.2E}\n"
            f"{'Generation:':>25}{values.index(max(values)):>10}",
            loc="right",
            fontfamily="Lucida Sans Typewriter",
            fontsize=12,
            color="#FF7E0E",
            pad=20,
        )

    # The following code configures some elements of the plot window

    # Disable toolbar
    maplot.rcParams["toolbar"] = "None"

    # Set font
    maplot.rcParams["font.family"] = "Candara"
    maplot.rcParams["font.size"] = 12
    maplot.rcParams["font.weight"] = 500

    # Set window title
    fig = pyplot.figure(figsize=(12, 5))
    fig.canvas.set_window_title("Prosthetic Foot Design by Genetic Algorithm")

    # Set icon
    manager = pyplot.get_current_fig_manager()
    manager.window.wm_iconbitmap(ICON_FILE)

    # Disable some borders
    subplot = fig.add_subplot(111, frameon=True)
    subplot.spines["right"].set_visible(False)
    subplot.spines["left"].set_visible(False)
    subplot.spines["top"].set_visible(False)

    # Push verticle axis to the right
    subplot.yaxis.tick_right()

    # Padding axis label from plot area, maybe unnecessary
    subplot.tick_params(axis="y", which="major", pad=5)
    subplot.tick_params(axis="x", which="major", pad=5)

    # Adjust subplot size based on window size
    pyplot.subplots_adjust(left=0.03, right=0.94, top=0.82, bottom=0.1)

    # Reconize key pressed
    pyplot.connect("key_press_event", on_clicked)

    if is_animation:
        for index in range(1, len(values) + 1):
            subplot.clear()
            draw(values[:index])
            pyplot.pause(0.0001)
    else:
        draw(values)

    # Hold window
    pyplot.show()


if __name__ == "__main__":
    __package__ = "inputprocess"
    objectives = get_objectives(get_data())
    main(objectives, is_animation=IS_ANIMATION)
