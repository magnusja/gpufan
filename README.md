nvfan
======

A module to control Nvidia Graphic Cards' fan within python. Features:
* set constant fan speed
* set more aggressive fan schedule compared to stock to avoid overhaeting when doing Deep Learning or other computationally intense tasks

## Why?

My deep learning rig contains 2 GTX 1080ti graphic cards with no liquid cooling. It takes only a few minutes for the GPUs to hit the thermal threshold of 86°C after I start a training process. Yet, it only uses fans at 50% rate.

This module uses a more aggressive fan speed and therefore avoids overheating, and thus throttling of GPU frequency at around 90° Celsius. 

## What is special about it?

You only have to add two to three lines to your main Deep Learning python script and then the fan speed is adjusted to keep GPU temperature at max 80° Celsius. When you Deep Learning pipeline exists, the control of the fann speed is automatically given back to the nvidia driver. Hence, fan speed is significantly reduced when finished to reduce noise.

# How to use it?

Controlling nvidia gpu fan requires an `X` server to be running. To run `X` without having a monitor attached to the system requires special config.


## Preparation

Setup x config in a shell like below. You may need to use `sudo`.

```shell
$ nvidia-xconfig --enable-all-gpus --cool-bits=7 --connected-monitor=Monitor0 --allow-empty-initial-configuration --force-generate
```

*Warning: we used `--force-generate` flag. A backup of your previous config is saved and is reported as the result of running this function.*


Aa manual configuration could look likke this::

```shell
$ cat /etc/X11/xorg.conf.d/nv.conf 
# start

Section "Device"
    Identifier     "Device0"
    Driver         "nvidia"
    VendorName     "NVIDIA Corporation"
    BoardName      "GeForce GTX 1080 Ti"
    Option "Coolbits" "4"
EndSection
# trail
```

See also https://wiki.archlinux.org/index.php/NVIDIA/Tips_and_tricks

## Run X

I think the best way is to use xinit:

```shell
$ xinit &
```

Leavve this sttep out if  you are  using a desktoop envirronment like Gnoome, KDE, or similar.

## Dependencies

Please make sure `nvdia-smi` and `nvidia-settings` are installed. The latter usually needs to be installed manually whereas the former is usually included in the nvidia driver package.

## Install nvfan

```shell
$ pip install nvfan
```

## Usage

You can use command line script:

```shell
$ nvfan constant -g 0 -s 60  # sets a constant speed at 60%
```

Or in your python script:

```python
import nvfan

first_gpu = 0
nvfan.constant(first_gpu, 60)
```

The above script, puts GPU 0 in `constant` mode with 60% speed. You can use `aggressive` or `driver` modes too:

```python
second_gpu = 1

# In aggressive mode, a small increase in temperature causes a large increase in fan speed.
nvfan.aggressive(second_gpu)

# Give control back to the driver manually. Please note that after execution is finished, this line is automatically called so you don't have to.
nvfan.driver(first_gpu)
nvfan.driver(second_gpu)
```

Instead of using the module you can use the `GPU` class to have more control (i.e. setting custom X11 display, if not set `DISPLAY` environment variable is used, or if not set, `:0` is used as fallback)

```python
import nvfan

gpu = gpufan.GPU(0, display=":1")  # or use default `None` for automatic lookup of display
gpu.aggressive()
```

You can also omit the first parameter (`device`) like so:

```python
import nvfan

gpu = gpufan.GPU()  # or use default `None` for automatic lookup of display
gpu.aggressive()
```

Then all available GPUs are set to aggressive speed.

## Decorators

As another syntactic sugar you can annotate functions, which will set the constant/aggressive speed before calling the decorated method and as soon as it returns will give the control back to the nvidia driver:

```python
import time

from nvfan.decorators import constant, aggressive

@constant(percentage=95)
def main():
    time.sleep(60)


@aggressive()
def main_agg():
    time.sleep(60)


if __name__ == '__main__':
    main()
    main_agg()
```

## Caution

Use this module at your own risk. The author takes no responsibility and the scripts come with no warranty.
