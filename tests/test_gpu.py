import atexit

from nvfan.gpu import GPU
from threading import Thread
import mock
import sure
import os


@mock.patch('nvfan.gpu.sb')
def test_gpu_creation(sb):
    gpu = GPU(0, True)
    gpu.constant(30)
    cmd = f'nvidia-settings -c {os.environ.get("DISPLAY", ":0")} -a [gpu:0]/GPUFanControlState=1 -a [fan:0]/GPUTargetFanSpeed=30'
    sb.run.assert_called_with(cmd, check=False, shell=True, stdout=sb.DEVNULL, stderr=sb.DEVNULL)

    gpu2 = GPU(1, False, display=":1")
    gpu2.constant(10)
    cmd = "nvidia-settings -c :1 -a [gpu:1]/GPUFanControlState=1 -a [fan:1]/GPUTargetFanSpeed=10"
    sb.run.assert_called_with(cmd, check=True, shell=True, stdout=sb.DEVNULL, stderr=sb.DEVNULL)

    gpu._thread.should.be(None)
    gpu2._thread.should.be(None)


@mock.patch('nvfan.gpu.sb')
def test_gpu_destruction(sb):
    gpu = GPU(0, True)
    atexit.unregister(gpu.do_exit)
    del gpu

    cmd = f'nvidia-settings -c {os.environ.get("DISPLAY", ":0")} -a [gpu:0]/GPUFanControlState=0'
    calls = [mock.call(cmd, check=False, shell=True, stdout=sb.DEVNULL, stderr=sb.DEVNULL)]
    sb.run.assert_has_calls(calls, any_order=True)


@mock.patch('nvfan.gpu.sb')
def test_gpu_aggressive(sb):
    gpu = GPU(0, True)
    gpu._thread.should.be(None)
    gpu.aggressive()
    gpu._thread.should.be.a(Thread)
    gpu._thread.is_alive().should.be(True)

    # Make sure a subsequent call to aggressive does not work
    thr = gpu._thread
    gpu.aggressive()
    gpu._thread.should.be(thr)

    gpu.driver()
    gpu._thread.is_alive().should.be(False)
