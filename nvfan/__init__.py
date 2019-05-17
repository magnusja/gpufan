"""GPUFan helps cooling GPUs inside python code."""

import multiprocessing as mp
from threading import Lock

from nvfan import utils
from .gpu import GPU
import signal


DRIVER_CONTROL = 'driver'
AGGRESSIVE_CONTROL = 'aggressive'
CONSTANT_CONTROL = 'constant'


_gpus_in_control = {}
_prevent_exceptions = False
_started = False
_start_lock = Lock()


def _get_device_id(device):
    try:
        import torch
        return device.index or torch.cuda.current_device().index
    except (AttributeError, ImportError):
        return int(device)


class Task(object):
    """A Task is a struct to keep info regarding a message between processes.

    Arguments
    ---------
    command : One of the command constants
    id int : Index of GPU device
    args list : arguments to pass to the command
    kwargs list : keyword arguments to pass to the command
    """

    def __init__(self, command, device_id, *args, **kwargs):  # noqa: D107
        self.command = command
        self.device_id = device_id
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):  # noqa: D105
        return '<Task GPU:{0} command:{1}>'.format(self.device_id, self.command)


def _controller(q):
    gpus = {}

    def signal_handler(*args):
        for gpu in gpus.values():
            gpu.driver()
        exit()

    signal.signal(signal.SIGTERM, signal_handler)

    while 1:
        task = q.get()
        device_id = task.device_id

        try:
            gpu = gpus[device_id]
        except KeyError:
            gpu = GPU(device_id, _prevent_exceptions)
            gpus[device_id] = gpu

        if task.command == CONSTANT_CONTROL:
            gpu.constant(*task.args)
        elif task.command == AGGRESSIVE_CONTROL:
            gpu.aggressive()
        elif task.command == DRIVER_CONTROL:
            gpu.driver()


_mp_ctx = mp.get_context('fork')
_mp_q = _mp_ctx.Queue()
_mp_p = _mp_ctx.Process(target=_controller, args=(_mp_q,))
_mp_p.daemon = True


def _start():
    global _started
    with _start_lock:
        if not _started:
            _mp_p.start()
        _started = True


def _send_task(task, device, *args, **kwargs):
    if device:
        device_id = _get_device_id(device)
        _mp_q.put(Task(task, device_id, *args, **kwargs))
    else:
        # use ALL gpus
        for g in range(utils.query_number_gpus()):
            _mp_q.put(Task(task, g, *args, **kwargs))


def constant(percentage, device=None):
    """Set fan to a constant speed.

    Arguments
    ---------
    device int : GPU index or `torch.device` instance
    percentage int : a number indicating constant fan speed (0-100)
    """
    _start()
    _send_task(CONSTANT_CONTROL, device, percentage)


def aggressive(device=None):
    """Control fan in aggressive mode.

    In this mode, the fan is set to higher number comparing to
    driver controller for a given temperature.

    Arguments
    ---------
    device int : GPU index or `torch.device` instance
    """
    _start()
    _send_task(AGGRESSIVE_CONTROL, device)


def driver(device=None):
    """Put Nvidia driver back in charge to control fan speed.

    Arguments
    ---------
    device int : GPU index or `torch.device` instance
    """
    _start()
    _send_task(DRIVER_CONTROL, device)


def prevent_exceptions():
    """Avoid raising exceptions if something did not work.

    Use this function if having control over gpu fan is not a priority
    and you prefer it to fail silently.
    """
    global _prevent_exceptions
    _prevent_exceptions = True
