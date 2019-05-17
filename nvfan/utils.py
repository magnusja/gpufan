import shlex
import subprocess


def exec_command(cmd: str):
    command = shlex.split(cmd)
    result = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)

    return result.stdout.read()


def query_number_gpus():
    output = exec_command('nvidia-smi --query-gpu=gpu_name,gpu_bus_id,vbios_version --format=csv')

    return len(output.split('\n')) - 2  # minus header, minus last new line
