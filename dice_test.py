import datetime
import random
import sys
from matplotlib import animation
import matplotlib.pyplot as plt
import seaborn as sns

def update(frame_number, rolls, faces, frequencies, dice_sides, num_dice):
    
    random.seed(None)
    for i in range(rolls):
        value = 0
        for i in range(num_dice):
            value += random.randrange(1, dice_sides + 1)
        frequencies[value - 1] += 1
    
    plt.cla()
    
    axes = sns.barplot(x=faces, y=frequencies, hue=faces, palette="bright", legend=False)
    axes.set_title(f"Dice frequencies for {sum(frequencies):,} rolls")
    axes.set(xlabel="Dice Value", ylabel="Frequency")
    axes.set_ylim(top=max(frequencies) * 1.15)
    
    for bar, frequency in zip(axes.patches, frequencies):
        text_x = bar.get_x() + bar.get_width() / 2.0
        text_y = bar.get_height()
        text = f"{frequency:,}\n{frequency / sum(frequencies):.3%}"
        axes.text(text_x, text_y, text, ha="center", va="bottom")

number_of_frames = 1000 # for command line args use int(sys.argv[1]) instead  
rolls_per_frame = 5 # for command line args use int(sys.argv[2]) instead

sns.set_style("darkgrid")


num_dice = 3
dice_sides = 8

figure = plt.figure(f"Rolling {num_dice} {dice_sides}-sided dice")
values = list(range(1, dice_sides * num_dice + 1))
frequencies = [0] * num_dice * dice_sides

die_animation = animation.FuncAnimation(
    figure, update, repeat=False, frames=number_of_frames,
    interval=33, fargs=(rolls_per_frame, values, frequencies, dice_sides, num_dice))

plt.show()