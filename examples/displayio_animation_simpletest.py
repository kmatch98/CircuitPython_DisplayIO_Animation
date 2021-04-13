# SPDX-FileCopyrightText: Copyright (c) 2021 Kevin Matocha
#
# SPDX-License-Identifier: MIT
#############################
"""
An example showing the use of the Animation class
using CircuitPython displayio and vectorio.
"""

import gc
import time
import board
import vectorio
import displayio

# pylint: disable=wildcard-import

from adafruit_displayio_layout.widgets.displayio_animation import (
    wiggle,
    quadratic_easeout,
    back_easeinout,
    elastic_easeout,
    quartic_easeinout,
    exponential_easeinout,
    translate,
    Animation,
    translate_relative,
)
from adafruit_displayio_layout.widgets.easing import *

# initialize the display
display = board.DISPLAY

# Store the initial memory usage
gc.collect()
# pylint: disable=no-member
start_mem = gc.mem_free()
# pylint: enable=no-member
print("1 gc.mem_free: {}".format(start_mem))

###################################
# 1. Create the graphical elements
#
# create three vectorio.Rectangles and put them into groups
###################################

rect1 = vectorio.Rectangle(10, 20)
rect2 = vectorio.Rectangle(30, 20)
rect3 = vectorio.Rectangle(20, 40)
rect4 = vectorio.Rectangle(20, 20)

palette1 = displayio.Palette(2)
palette2 = displayio.Palette(2)
palette3 = displayio.Palette(2)
palette4 = displayio.Palette(2)

palette1.make_transparent(0)
palette1[1] = 0xFF0000  # red
palette1[0] = 0x000000

palette2.make_transparent(0)
palette2[1] = 0x00FF00  # green
palette2[0] = 0x000000

palette3.make_transparent(0)
palette3[1] = 0x0000FF  # blue
palette3[0] = 0x000000

palette4.make_transparent(0)
palette4[1] = 0x00FFFF  # cyan
palette4[0] = 0x000000

shape1 = vectorio.VectorShape(shape=rect1, pixel_shader=palette1)
shape2 = vectorio.VectorShape(shape=rect2, pixel_shader=palette2)
shape3 = vectorio.VectorShape(shape=rect3, pixel_shader=palette3)
shape4 = vectorio.VectorShape(shape=rect4, pixel_shader=palette4)

main_group = displayio.Group(max_size=4)
group1 = displayio.Group(max_size=1)
group2 = displayio.Group(max_size=1)
group3 = displayio.Group(max_size=1)
group4 = displayio.Group(max_size=1)

group1.append(shape1)
group1.x = 50
group1.y = 20
group2.append(shape2)
group2.x = 20
group2.y = 220
group3.append(shape3)
group3.x = 180
group3.y = 150
group4.append(shape4)
group4.x = 280
group4.y = 30

main_group.append(group1)
main_group.append(group2)
main_group.append(group3)
main_group.append(group4)

# Store the memory usage after creating the graphical elements
gc.collect()
# pylint: disable=no-member
graphics_mem = gc.mem_free()
# pylint: enable=no-member
print("2 gc.mem_free:   {}".format(graphics_mem))

display.show(main_group)


###################################
# 2. Instance the Animation and add the animation entries
#
# add entries for all four display groups
###################################

animation = Animation()

# group1 (red): translate with default easing function (linear_interpolation)
# linear interpolation animations appear "unphysical"
animation.add_entry(
    group=group1,
    frame_start=5,
    frame_end=20,
    function=translate,
    x1=50,
    y1=20,
    x2=50,
    y2=80,
)

animation.add_entry(
    group=group1,
    frame_start=55,
    frame_end=75,
    function=translate,
    x1=50,
    y1=80,
    x2=180,
    y2=180,
)

# group2 (green): translate with the same easing functions for x,y
animation.add_entry(
    group=group2,
    frame_start=10,
    frame_end=40,
    function=translate,
    x1=20,
    y1=220,
    x2=240,
    y2=80,
    easing_function_x=quartic_easeinout,
    easing_function_y=quartic_easeinout,
)

animation.add_entry(
    group=group2,
    frame_start=45,
    frame_end=60,
    function=translate,
    x1=240,
    y1=80,
    x2=60,
    y2=50,
    easing_function_x=back_easeinout,
    easing_function_y=back_easeinout,
)

# group3 (blue):
#         1. wiggle
#         2. translate with two different easing functions for x and y
#         3. wiggle nervously again
animation.add_entry(
    group=group3,
    frame_start=0,
    frame_end=15,
    function=wiggle,
    delta_x=10,
    delta_y=10,
    xsteps=5,
    ysteps=3,
)

animation.add_entry(
    group=group3,
    frame_start=15,
    frame_end=80,
    function=translate,
    x1=180,
    y1=150,
    x2=60,
    y2=50,
    easing_function_x=elastic_easeout,
    easing_function_y=back_easeinout,
)

animation.add_entry(
    group=group3,
    frame_start=80,
    frame_end=100,
    function=wiggle,
    delta_x=5,
    delta_y=5,
    xsteps=3,
    ysteps=5,
)


# group4 (cyan): use two relative translations, with two separate easing functions for x and y
animation.add_entry(
    group=group4,
    frame_start=5,
    frame_end=35,
    function=translate_relative,
    delta_x=-120,
    delta_y=+50,
    easing_function_x=quadratic_easeout,
    easing_function_y=exponential_easeinout,
)

animation.add_entry(
    group=group4,
    frame_start=40,
    frame_end=90,
    function=translate_relative,
    delta_x=+120,
    delta_y=-50,
    easing_function_x=exponential_easeinout,
    easing_function_y=quadratic_easeout,
)


# Store the memory usage after creating the Animation elements
gc.collect()
# pylint: disable=no-member
animation_mem = gc.mem_free()
# pylint: enable=no-member
print("3 gc.mem_free:   {}".format(graphics_mem))
print("Memory used for graphic elements: {} bytes".format(start_mem - graphics_mem))
print(
    "Memory used for animation elements: {} bytes".format(graphics_mem - animation_mem)
)


###################################
# 3. Setup and execute the animation
#
# The main loop performs the animation in forward direction, then in the reverse direction
###################################

# Setup parameters for executing the animation frame rate
frame_multiplier = 15  # add additional "sub-frames" to smooth the animation
max_frames = 100  # the total number of frames to be displayed
delay_time = (
    0.05 / frame_multiplier
)  # Adjust the sub-frame speed by adding a small delay between subframes

# this main loop is where the animation is performed
while True:

    # Run the animation forward
    for frame in range(max_frames):  # Pick the frame to show
        for subframe in range(
            frame_multiplier
        ):  # divide the frame into smaller "subframes"
            animation.execute_frame(
                frame + subframe / frame_multiplier
            )  # execute the current frame
            time.sleep(delay_time)

    # Run the animation in reverse
    for frame in range(max_frames):  # Pick the frame to show
        for subframe in range(
            frame_multiplier
        ):  # divide the frame into smaller "subframes"
            animation.execute_frame(max_frames - (frame + subframe / frame_multiplier))
            # execute the current frame, but in reverse from max_frames
            time.sleep(delay_time)

    time.sleep(0.5)  # pause slightly before restarting the animation
