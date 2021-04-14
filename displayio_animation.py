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

            if frame == entry.frame_start:  # initialize startx, starty
                entry.startx = entry.group.x
                entry.starty = entry.group.y

            if entry.frame_start <= frame <= entry.frame_end:
                # This frame is within the entry frame range, so animate it

                # calculate a value between 0.0 and 1.0 to show the current frame's
                # position within this entry's frame range

                if (entry.frame_end - entry.frame_start) <= 0:  # prevent divide by zero
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
