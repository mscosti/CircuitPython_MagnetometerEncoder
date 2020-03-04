# The MIT License (MIT)
#
# Copyright (c) 2020 Matthew Costi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`magnetometerencoder`
================================================================================

Helper library to use a 3D high resolution magnetometer to sense angular position of a magnet relative to sensor


* Author(s): Matthew Costi

Implementation Notes
--------------------

**Hardware:**


**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/mscosti/CircuitPython_MagnetometerEncoder.git"

import math

wrap_threshold = 300 # used to detect wrap around

class Encoder():
    """
    Base Encoder class that uses raw magnetic x, y, and z readings from different implemented sensors
    to provide functionality similiar to that of an absolute rotational encoder.
    """
    def __init__(self, min_increment=0.3, smooth=3):
        self._min_increment = min_increment
        if (smooth > 0):
            self._smooth_window = []
            self._smooth_size = smooth
            self._smooth = True
        else:
            self._smooth = False
        
        try:
            self.magnetic_xyz
        except AttributeError:
            raise Exception('Encoder can not be used without a magnetometer implementation with a magnetic_xyz property')
    
    def _get_angle(self,x,y):
        return((math.atan2(x,y) * 180) / math.pi) + 180

    def _get_smooth_angle(self,x,y):
        angle = self._get_angle(x,y)
        if len(self._smooth_window) > 0 and (wrap_threshold <= math.fabs(self._smooth_window[-1] - angle)):
            # we've wrapped around, and don't want to average with the spike
            self._smooth_window.clear() 

        self._smooth_window.append(angle)
        if len(self._smooth_window) < self._smooth_size:
            return angle # not enough data to start averaging 
        if len(self._smooth_window) > self._smooth_size:
            self._smooth_window.pop(0) # remove oldest from window

        s = 0
        for i in self._smooth_window:
            s += i
        return s / len(self._smooth_window)
    
    
    @property
    def angle(self):
        MX, MY, MZ = self.magnetic_xyz

        if (self._smooth):
            angle = self._get_smooth_angle(MX,MY)
        else:
            angle = self._get_angle(MX,MY)

        try:
            delta = angle - self._prev_angle
        except AttributeError:
            delta = 0

        if delta >= 180: #detect wrap from 0 -> 360
            delta = 360 - delta
        elif delta <= -180: #detect wrap from 360 -> 0
            delta = 360 + delta
        
        self._prev_angle = angle

        if math.fabs(delta) > self._min_increment:
            return angle, delta
        else:
            return angle, 0