# SPDX-FileCopyrightText: 2021 Kevin Matocha
#
# SPDX-License-Identifier: MIT

"""
`Animation`
================================================================================
CircuitPython Animation Class to make it easy to move around displayio and
vectorio graphical elements.

* Author(s): Kevin Matocha

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

"""

# Animation class for use with displayio Groups
from displayio import Palette

from adafruit_displayio_layout.widgets.easing import linear_interpolation


# pylint: disable=too-many-arguments, anomalous-backslash-in-string, invalid-name
# pylint: disable=unused-argument, too-few-public-methods, useless-super-delegation


class Animation(list):
    """An Animation class to make it easy to making moving animations with CircuitPython's
    displayio and vectorio graphical elements.

    After instancing an `Animation()` object, use `Animation.add_entry()` to add
    frame animation sections.  Once all your animation entries are added, then perform
    the frame animation using `Animation.execute_frame()`.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_entry(self, group, frame_start, frame_end, function, **kwargs):
        """Adds an animation entry into the Animation list.

        :param displayio.Group group: the displayio Group that will be animated
         within this frame range
        :param float frame_start: the starting frame position for this animation
        :param float frame_end: the ending frame position for this animation
        :param function: the name of the function to be called to mutate
         the ``group`` during the frame range
        :param \*\*kwargs: the additional arguments that should be passed to
         `function` when `Animation.execute_frame()` is called to trigger the
         animation to execute

        Note: See the definition of `Animation.execute_frame()` to understand
        what other parameters are sent to `function` during animations.

        """

        myentry = Entry(
            group,
            frame_start,
            frame_end,
            function,  # will be called function(position=position, arguments...)
            kwargs,
        )

        self.append(myentry)

    def execute_frame(self, frame):
        """The function that performs the actual frame animation execution.

        This function searches through all ``Entry`` items that have been added to
        the Animation instance to determine if this frame is within the window of
        ``frame_start`` to ``frame_end``.  If the requested frame is within the window,
        this calls the ``Entry.function`` with several "internal" parameters along
        with the additional "user" parameters that were input as additional arguments
        in the ``Animation.add_entry()`` function.

        The parameters that are sent to ``Entry.function()`` are:
        - float position: a value between 0.0 and 1.0 representing the current ``frame``
        distance within the window of ``frame_start`` and ``frame_end``.  For example, if
        the current ``frame`` is equal to ``frame_start``, then ``position`` is 0.0.
        - displayio.Group group: the group to be animated using ``function``
        - int x0: the x-position of the group at ``frame_start``
        - int y0: the y-position of the group at ``frame_start``
        - float frame: the current frame that is being executed
        - float frame_start: the starting frame for this frame window
        - float frame_end: the ending frame for this frame window
        - \*\*kwargs: any other parameters that were defined in the Entry

        The ``function`` should be designed to ignore any unneeded input parameters by
        including ``**kwargs`` as one of the input parameters.  This will cause the
        function to ignore excess arguments.

        Note: If a function requires the (x0,y0) values, you **must** initally perform
        ``Animation.execute_frame()`` at frame == frame_start.  The ``Animation.execute_frame()``
        initializes the (x0, y0) values only when called with the value of ``frame_start``.

        Other Note: The frame window is "exclusive", so no animation is performed when
        ``frame == frame_end``.

        :param float frame: The frame to be displayed.  Note: This is a float, so subframes
         can be animated.
        """
        for entry in self:

            if (frame == entry.frame_start) and (entry.group is not None):  # initialize startx, starty
                entry.startx = entry.group.x
                entry.starty = entry.group.y

            if entry.frame_start <= frame <= entry.frame_end:
                # This frame is within the entry frame range, so animate it

                # calculate a value between 0.0 and 1.0 to show the current frame's
                # position within this entry's frame range

                if (
                    entry.frame_end - entry.frame_start
                ) <= 0:  # prevent divide by zero
                    position = 1.0
                else:
                    position = (frame - entry.frame_start) / (
                        entry.frame_end - entry.frame_start
                    )
                entry.function(
                    position=position,
                    group=entry.group,
                    x0=entry.startx,
                    y0=entry.starty,
                    frame=frame,
                    frame_start=entry.frame_start,
                    frame_end=entry.frame_end,
                    **entry.kwargs,
                )


class Entry:
    """This `Entry` class is a holder for the conditions that define an animated
    frame range.  This holds the group, the "augmentation" function and arguments
    that are run at each call of `Animation.execute_frame`.

    Before running your loop with `Animation.execute_frame`, add all of your
    entries to the Animation object using `Animation.add_entry()`. Any excess
    arguments that are not handled by `Animation.execute_frame` will be passed
    to the `function` parameter (see notes on using the ``kwargs`` notation).

    Here is a code example.  Append some display elements into ``group1``, create
    an Animation instance and then add an animation entry:

    .. code-block:: python

            group1=displayio.Group(max_size=1)

            animation=Animation()

            animation.add_entry(group=group1,
             frame_start=5, frame_end=20,
             function=translate,
             x1=50, y1=20, x2=50, y2=50,
             easing_function_x=quadratic_easeinout,
             easing_function_y=quadratic_easeinout)

    :param displayio.Group group: the group that is animated in this set of frames
    :param float frame_start: the starting frame for this animation
    :param float frame_end: the ending frame for this animation
    :param function: the function that mutates the group to cause the animation
    :param kwargs: a set of additional arguments that will be passed to the
     ``function`` during the animation
    """

    def __init__(
        self,
        group,
        frame_start,
        frame_end,
        function,
        kwargs,
    ):
        self.group = group
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.function = function
        self.kwargs = kwargs

        # Create placeholder instance variables, to store the initial
        # group's (x,y) position at the initial action frame
        self.startx = None
        self.starty = None


#####################
# Animation functions
#####################
# This is a starter set of functions that can be used with the Animation class
#
# The function can ignore some parameters that the ``execute_frame`` function sends.
# Be sure to include ``**kwargs`` to the function input parameters
# so the function will ignore all unused input parameters.
#
# Here are the parameters that ``execute_frame`` always sends to the function:
# float position: a linear interpolation of the current frame's position between ``frame_start``
#  and ``frame_end``
# displayio.Group group: the group in the Entry
# int x0: initial x-position at the starting frame
# int y0: initial y-position at the starting frame
# float frame: the current frame
# float frame_start: the starting frame of this animation entry
# float frame_end: the ending frame of this animation entry (should be used as exclusive)
# Other arguments that are defined in the `add_entry` call.


def translate(
    *,
    x1,
    y1,
    x2,
    y2,
    easing_function_x=linear_interpolation,
    easing_function_y=linear_interpolation,
    group,
    position,
    **kwargs
):
    """Performs a translation animation between two endpoints.    Use two different
    easing functions to get all kinds of variety of cool motion.

    :param int x1: initial x-position of ``group``
    :param int y1: initial y-position of ``group``
    :param int x2: final x-position of ``group``
    :param int y2: final y-position of ``group``

    :param function easing_function_x: easing function that modifies the ``position`` value
     for the x-motion (default: linear_interpolation)
    :param function easing_function_y: easing function that modifies the ``position`` value
     for the y-motion (default: linear_interpolation)

    :param displayio.Group group: the display group that is sent to the ``function``.  If using
     `Animation.execute_frame()` the group input parameter will be included automatically
     from the Entry.
    :param float position: float position: a linear interpolation of the current frame's
     position between ``frame_start`` and ``frame_end``. If using
     `Animation.execute_frame()` the ``position`` parameter will be included automatically.
    """
    # including kwargs here is necessary to ignore excess arguments
    # user parameters: x1, y1, x2, y2, easing_function_x, easing_function_y
    # parameters handled from `execute_frame`: group, position

    group.x = round((x2 - x1) * easing_function_x(position)) + x1
    group.y = round((y2 - y1) * easing_function_y(position)) + y1

def translate_relative(
    *,
    delta_x,
    delta_y,
    easing_function_x=linear_interpolation,
    easing_function_y=linear_interpolation,
    group,
    x0,
    y0,
    position,
    **kwargs
):
    """Performs a relative translation animation between two endpoints.  Use two different
    easing functions to get all kinds of variety of cool motion.

    Note: To use relative translations, be sure to run `execute_frame` at ``frame_start`` first
    so the initial (x0, y0) position is stored.  For example, if you run the frames in reverse,
    you must run `execute_frame` at ``frame_start`` at least once initialize the initial (x0, y0)
    position.

    Special note: Relative translations can get complicated.  If you want to tightly control
    predefined positions, then `translate` is the best approach.  By combining overlapping
    relative translations, you can probably come up with all kinds of clever and confusing
    animations.  Perhaps the `translate_relative` function is an avenue to create animated
    "generative art" projects.

    :param int x2: final x-position of ``group``
    :param int y2: final y-position of ``group``

    :param function easing_function_x: easing function that modifies the ``position`` value
     for the x-motion (default: linear_interpolation)
    :param function easing_function_y: easing function that modifies the ``position`` value
     for the y-motion (default: linear_interpolation)

    :param displayio.Group group: the display group that is sent to the ``function``.  If using
     `Animation.execute_frame()` the ``group`` input parameter will be included automatically
     from the Entry.
    :param int x0: initial x-position of ``group``.  If using `Animation.execute_frame()`
     the ``x0`` input parameter will be included automatically from the Entry.
    :param int y0: initial y-position of ``group``.  If using `Animation.execute_frame()`
     the ``y0`` input parameter will be included automatically from the Entry.
    :param float position: float position: a linear interpolation of the current frame's
     position between ``frame_start`` and ``frame_end``. If using
     `Animation.execute_frame()` the ``position`` parameter will be included automatically.
    """
    # including kwargs here is necessary to ignore excess arguments
    # user parameters: x2, y2, easing_function_x, easing_function_y
    # parameters handled from `execute_frame`: group, x0, y0, position
    group.x = round((delta_x) * easing_function_x(position)) + x0
    group.y = round((delta_y) * easing_function_y(position)) + y0


def wiggle(
    *,
    delta_x=0,
    delta_y=0,
    xsteps=None,
    ysteps=None,
    group,
    x0,
    y0,
    frame_start,
    frame,
    **kwargs
    ):
    """Performs a nervous wiggling animation around the starting point. To achieve a random-looking
    wiggle, set ``xsteps`` and ``ysteps`` to two different prime numbers.

    Note: To use `wiggle`, be sure to run `execute_frame` at ``frame_start`` first
    so the initial (x0, y0) position is stored.  For example, if you run the frames in reverse,
    you must run `execute_frame` at ``frame_start`` at least once initialize the initial (x0, y0)
    position.

    :param int delta_x: amount of x-movement, in pixels (default = 0)
    :param int delta_y: amount of y-movement, in pixels (default = 0)
    :param int xsteps: number of frame steps it takes to make a full x-direction wiggle
    :param int ysteps: number of frame steps it takes to make a full y-direction wiggle
    :param displayio.Group group: the display group that is sent to the ``function``.  If using
     `Animation.execute_frame()` the ``group`` input parameter will be included automatically
     from the Entry.
    :param int x0: initial x-position of ``group``.  If using `Animation.execute_frame()`
     the ``x0`` input parameter will be included automatically from the Entry.
    :param int y0: initial y-position of ``group``.  If using `Animation.execute_frame()`
     the ``y0`` input parameter will be included automatically from the Entry.
    :param float frame_start: the starting frame of this animation entry.  If using
     `Animation.execute_frame()` the ``frame_start`` parameter will be included automatically
     from the Entry.
    :param float frame: the current frame being animated.  If using
     `Animation.execute_frame()` the ``frame`` parameter will be included automatically.
    """

    # including kwargs here is necessary to ignore excess arguments
    # user parameters: delta_x, delta_y, xsteps, ysteps
    # parameters handled from `execute_frame`: group, x0, y0, position, frame_start, frame

    if (xsteps is not None) and (delta_x != 0):
        xpositions = (
            list(range(xsteps // 2))
            + list(range(xsteps // 2 - 2, -1 * xsteps // 2, -1))
            + list(range(-1 * xsteps // 2 + 2, 0))
        )
        group.x = x0 + round(
            delta_x / xsteps * xpositions[int((frame - frame_start) % len(xpositions))]
        )

    if (ysteps is not None) and (delta_y != 0):
        ypositions = (
            list(range(ysteps // 2))
            + list(range(ysteps // 2 - 2, -1 * ysteps // 2, -1))
            + list(range(-1 * ysteps // 2 + 2, 0))
        )
        group.y = y0 + round(
            delta_y / ysteps * ypositions[int((frame - frame_start) % len(ypositions))]
        )

def color_morph_vector_shape(
                *,
                color_start,
                color_end,
                vector_shape,
                position,
                **kwargs,
                ):
    """Performs color morphing for a vector shape, with color between the ``color_start`` and ``color_end``
    values based on the position parameter.

    :param int color_start: the starting color
    :param int color_end: the ending_color
    :param vectorio.VectorShape vector_shape: the VectorShape whose palette color index 1
     should be morphed.
    :param float position: float position: a linear interpolation of the current frame's
     position between ``frame_start`` and ``frame_end``. If using
     `Animation.execute_frame()` the ``position`` parameter will be included automatically.
    """
    morphed_color = _color_fade(color_start, color_end, position)

    palette=Palette(2)
    palette[1]=morphed_color
    palette.make_transparent(0)

    vector_shape.pixel_shader=palette

def color_morph_label(
                *,
                color_start,
                color_end,
                label,
                position,
                **kwargs,
                ):
    """Performs color morphing for a text label between the ``color_start`` and ``color_end``
    values based on the position parameter.

    :param int color_start: the starting color
    :param int color_end: the ending_color
    :param label: the label whose color is to be morphed
    :param float position: float position: a linear interpolation of the current frame's
     position between ``frame_start`` and ``frame_end``. If using
     `Animation.execute_frame()` the ``position`` parameter will be included automatically.
    """
    morphed_color = _color_fade(color_start, color_end, position)
    label.color = morphed_color

def color_morph_palette(
                *,
                palette_start,
                color_end,
                palette_target,
                position,
                **kwargs,
                ):
    """Performs color morphing for a color palette between the ``palette_start`` and a single
    ``color_end`` value based on the position parameter.  At the final position=1.0, the
    ``palette_target`` will be filled with the ``color_end`` value.

    :param displayio.palette palette_start: the starting palette for the image
    :param int color_end: the single ending_color for all the colors in the palette
    :param displayio.palette palette_target: the destination palette to be "morphed" to the
     ending_color
    :param float position: float position: a linear interpolation of the current frame's
     position between ``frame_start`` and ``frame_end``. If using
     `Animation.execute_frame()` the ``position`` parameter will be included automatically.
    """
    for i, color in enumerate(palette_start):
        morphed_color = _color_fade(color, color_end, position)
        palette_target[i] = morphed_color


def _color_to_tuple(value):
    """Converts a color from a 24-bit integer to a tuple.
    :param value: RGB LED desired value - can be a RGB tuple or a 24-bit integer.
    """
    if isinstance(value, tuple):
        return value
    if isinstance(value, int):
        if value >> 24:
            raise ValueError("Only bits 0->23 valid for integer input")
        r = value >> 16
        g = (value >> 8) & 0xFF
        b = value & 0xFF
        return [r, g, b]

    raise ValueError("Color must be a tuple or 24-bit integer value.")

def _tuple_to_color(rgb_tuple):
    rgb_int = rgb_tuple[0] << 16 | rgb_tuple[1] << 8 | rgb_tuple[2]
    return rgb_int

def _color_fade(start_color, end_color, fraction):
    """Linear extrapolation of a color between two RGB colors (tuple or 24-bit integer).
    :param start_color: starting color
    :param end_color: ending color
    :param fraction: Floating point number  ranging from 0 to 1 indicating what
    fraction of interpolation between start_color and end_color.
    """

    start_color = _color_to_tuple(start_color)
    end_color = _color_to_tuple(end_color)
    if fraction >= 1:
        return end_color
    if fraction <= 0:
        return start_color

    faded_color = [0, 0, 0]
    for i in range(3):
        faded_color[i] = start_color[i] - int(
            (start_color[i] - end_color[i]) * fraction
        )
    return _tuple_to_color(faded_color)
