import matplotlib.pyplot as plt
import numpy as np
import random
import time


MAX_LENGTH = 100

class Visualizer:
    def __init__(self) -> None:
        # Create a figure and 6 subplots (2x3 grid)
        self.fig, self.axs = plt.subplots(2, 3, figsize=(12, 6))

        # Titles for the subplots
        self.titles = ['Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz']
        self.colors = ['r', 'g', 'b', 'c', 'm', 'y']

        # Initialize empty lists to store data for plotting
        self.data = {'Fx': [], 'Fy': [], 'Fz': [], 'Mx': [], 'My': [], 'Mz': []}
        self.time_data = []

        # Plot placeholders
        self.lines = []

        for i, ax in enumerate(self.axs.flat):
            ax.set_title(self.titles[i])
            ax.set_xlim(0, 100)
            ax.set_ylim(-20, 100)
            line, = ax.plot([], [], self.colors[i], label=self.titles[i])
            self.lines.append(line)
            ax.legend()

        # Draw and show the initial empty plot
        plt.tight_layout()
        plt.ion()
        plt.show()

        self.current_time = 0

    def calibrate(self, msgs):
        # Calibrate the sensor
        self.cal_data = {
        'Fx': msgs[0],
        'Fy': msgs[1],
        'Fz': msgs[2],
        'Mx': msgs[3],
        'My': msgs[4],
        'Mz': msgs[5],
        }

    def update(self, msgs):
        new_data = {
        'Fx': msgs[0] - self.cal_data['Fx'],
        'Fy': msgs[1] - self.cal_data['Fy'],
        'Fz': msgs[2] - self.cal_data['Fz'],
        'Mx': msgs[3] - self.cal_data['Mx'],
        'My': msgs[4] - self.cal_data['My'],
        'Mz': msgs[5] - self.cal_data['Mz'],
        }

        self.current_time += 1

        # Append new data to the lists
        self.time_data.append(self.current_time)
        for key in self.data.keys():
            self.data[key].append(new_data[key])

        # Keep the lists within a certain length (e.g., 100 points)
        if len(self.time_data) > MAX_LENGTH:
            self.time_data.pop(0)
            for key in self.data.keys():
                self.data[key].pop(0)

        # Update the data for each subplot
        for i, key in enumerate(self.data.keys()):
            self.lines[i].set_data(self.time_data, self.data[key])
            self.axs.flat[i].set_xlim(max(0, self.current_time - MAX_LENGTH), self.current_time)
            # scale y-axis to fit the data (max and min values)
            self.axs.flat[i].set_ylim(min(self.data[key]), max(self.data[key]))

            

        # Redraw the figure
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        # Adjust the interval to fit your real-time requirements
        time.sleep(0.005)  # Update every 0.005 seconds


    def close(self):
        plt.close(self.fig)
        plt.ioff()
