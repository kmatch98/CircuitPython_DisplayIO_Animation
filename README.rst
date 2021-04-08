Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-displayio_animation/badge/?version=latest
     :target: https://circuitpython-displayio-animation.readthedocs.io/
     :alt: Documentation Status


.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/kmatch98/CircuitPython_DisplayIO_Animation/workflows/Build%20CI/badge.svg
    :target: https://github.com/kmatch98/CircuitPython_DisplayIO_Animation/actions
    :alt: Build Status


.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

Get your graphics "on the move" with this Animation library that uses CircuitPython's displayio to make buttery-smooth animations for your LCD/TFT display or LED matrix.



Usage
=====

This library consists of a `Animation` class.

#. Create the graphical elements and put them into separate groups, depending upon which elements will be move together or separately.

#. Instance an `Animation()` object and creat the animation entries using `add_entry()` with all the desired parameters, including the starting and ending frames, the function for animating your object and all the relevant parameters for that function.

   * Several initial animation functions are provided:

     * `translate` - Move the group between two (x1,y1) and (x2,y2) locations with options for "easing" functions to make cool animations
	 * `translate_relative` - Move from the initial position by (delta_x, delta_y), also with options for easing functions
	 * `wiggle` - make some nervous jittery motion while generally staying in one spot

   * Add your own functions, maybe morphing colors, rotation or changing the shape altogether as it moves.

   * You can combine animations over the same frames, try it out and see what you can discover!

#. Make a `while` loop that calls `execute_frame()` for each frame.

#. Enjoy watching your animation.

**Bonus:** Try different settings for the "easing"  to get all kinds of smooth and creative animations.

`Here is an example showing how to use these Animations <https://github.com/kmatch98/CircuitPython_DisplayIO_Animation/tree/main/examples>`_

`Go check out the documentation with more details how to use these animation tools with displayio <https://circuitpython-displayio-animation.readthedocs.io/en/latest/api.html>`_.



Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Adafruit_DisplayIO_Layout <https://github.com/adafruit/Adafruit_CircuitPython_DisplayIO_Layout/>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Usage Example
=============

See scripts in the examples directory of this repository.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/kmatch98/CircuitPython_DisplayIO_Animation/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
