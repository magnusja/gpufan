"""This module contains GPU object.

A GPU representes an physical gpu based on its index in the list of
available gpus.
"""
import os
from threading import Thread, Event

from .utils import exec_command
from .curve import Curve
import subprocess as sb
import time
import atexit
import logging

logger = logging.getLogger(__name__)


class GPU(object):
    """GPU is a representation of a physical gpu based on its index in the list of available gpus.

    Arguments
    ---------
    device_id int : Index of the GPU
    prevent_exceptions boolean : Silent exceptions
    display str : X display identifier
    """

    def __init__(self, device_id, prevent_exceptions=False, display=None):  # noqa: D107
        self.id = device_id
        self.display = display
        self.check_exceptions = not prevent_exceptions
        self._stop = Event()
        self._thread = None

        self.check_display()
        atexit.register(self.do_exit)

    def check_display(self):
        if not self.display:
            self.display = os.environ.get("DISPLAY", ":0")

    def stop(self):
        """Signal the thread to stop execution."""
        self._stop.set()

    @property
    def stopped(self):
        """Check if stopping execution is requested."""
        return self._stop.isSet()

    def speed(self, speed):
        cmd = [
                "nvidia-settings",
                "-c {0}".format(self.display),
                "-a [gpu:{0}]/GPUFanControlState=1".format(self.id),
                "-a [fan:{0}]/GPUTargetFanSpeed={1}".format(self.id, speed)
        ]
        # using sb.run(cmd, ...) did not work! I guess there is a conflict in -c switch.
        sb.run(" ".join(cmd), shell=True, stdout=sb.DEVNULL, stderr=sb.DEVNULL, check=self.check_exceptions)
    speed = property(None, speed)

    def __loop_custom_curve_speed(self, delay=1.0):
        curve = Curve()
        while not self.stopped:
            new_fan_speed = curve.evaluate(self.temperature)
            logger.debug("set speed for gpu " + str(self.id) + " to " + str(new_fan_speed))
            self.speed = new_fan_speed
            time.sleep(delay)
        logger.debug("exiting custom curve loop")

    def __thread_alive(self):
        if self._thread and self._thread.is_alive():
            return True
        return False

    @property
    def temperature(self):
        """Get temperature of the GPU."""

        command = "nvidia-smi -i %d --query-gpu=temperature.gpu --format=csv,noheader" % self.id
        temperature = exec_command(command).strip()

        return int(temperature)

    def constant(self, percentage):
        """Set a constant fan speed.

        Arguments
        ---------
        percentage int : An integer from 0 to 100
        """
        logger.debug("set mode constant for gpu " + str(self.id) + " with speed " + str(percentage))
        if self.__thread_alive():
            self.stop()
            self._thread.join()
        self.speed = percentage

    def aggressive(self):
        """Control GPU fan based on an aggressive regime.

        It tries to set GPU fan to a high speed as soon as temperature rises.
        """
        logger.debug("set mode aggresive for gpu " + str(self.id))
        if self.__thread_alive():
            return
        self._thread = Thread(target=self.__loop_custom_curve_speed)
        self._thread.daemon = True
        self._thread.start()

    def driver(self):
        """Return control of fan speed to the driver."""
        logger.debug("returning control to nvidia driver for gpu " + str(self.id))
        if self.__thread_alive():
            self.stop()
            self._thread.join()

        cmd = [
                "nvidia-settings",
                "-c {0}".format(self.display),
                "-a [gpu:{0}]/GPUFanControlState=0".format(self.id)
        ]
        sb.run(" ".join(cmd), shell=True, stdout=sb.DEVNULL, stderr=sb.DEVNULL, check=self.check_exceptions)

    def do_exit(self):
        logger.debug("do exit (atexit)")
        if self.__thread_alive():
            self.stop()
            self._thread.join()
        self.driver()

    def __del__(self):
        """Make sure thread is stopped before destruction."""
        self.do_exit()
