import shutil
import sys
import os
import argparse
import logging
import subprocess
import docker
from datetime import datetime
import re
from typing import NamedTuple, List
IMG = "p4c-with-fix" #"tommanis/p4c-with-fix:latest"

class Measurement(NamedTuple):
    value: int  # The measured value (delay in nanoseconds)
    log: List[str]  # The associated log lines

class Result(NamedTuple):
    packet: str  # The packet used
    measurements: List[Measurement]  # The associated measurements

def call(cmd, silent=False):
    if not silent: logging.debug(f"Executing command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    except Exception as e:
        print(e)
    if not silent:
        logging.debug(f"Command output: {result.stdout.strip()}")
        logging.debug(f"Command error: {result.stderr.strip()}")

def setup_logging(debug):
    # Get the root logger
    logger = logging.getLogger()
    
    # Remove any existing handlers to avoid duplicate logging
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    if not debug:
        # If debug is not enabled, set up a NullHandler to do nothing
        logger.addHandler(logging.NullHandler())
        return

    log_level = logging.DEBUG
    log_file = "/tmp/p4ddg-experiment-runner-log.txt"
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Configure logging to write to file
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file)
        ]
    )

    print(f"Logging enabled. Logs will be written to {log_file}")
    logging.debug(f"Logging enabled")


def p4testgen(target, arch, f, ws, n):
    cmd = f"p4testgen --target {target} --arch {arch} --out-dir out-p4testgen --max-tests {n+1} --test-backend STF {f}"

    # cmd = f"p4testgen -O0 --target {target} --arch {arch} --out-dir out-p4testgen --max-tests {n+1} --test-backend STF {f}"
    try:
        client = docker.from_env()
        container = client.containers.run(
            IMG,
            command=cmd,
            volumes={ws: {"bind": "/workspace", "mode": "rw"}},
            working_dir="/workspace",
            remove=True,  # Automatically remove the container after it exits
            detach=False  # Run in the foreground and return output
        )
        print(container)
        return True
    except Exception as e:
        print(e)
        print("p4testgen failed, this is probably a ddg generated p4 file")
        return False
def format_dir_name(f):
    d_name = os.path.dirname(f).split("/")[-1] 
    f_name =os.path.basename(f).split(".p4")[0]
    d = d_name +"." +f_name + ".p4app"
    return d
def extract_hex_packet(packet_str):
    return packet_str.strip().split("packet")[-1].strip().split(" ")[-1]

def prepare_run(sf, packets, n, r, p ):
    setup_logging(True)


    tmp = "/tmp/p4ddg-experiment-runner-tmp"
    call(f"mkdir -p {tmp}")
    call(f"rm -rf {tmp}/")
    call(f"mkdir -p {tmp}")

    f = sf
    logging.info(f"Performing step 1 for {sf}")
    d = format_dir_name(f)
    logging.debug(f"Dirname {d}")
    call(f"mkdir -p {tmp}/{d}", silent=True)
    call(f"cp {os.path.dirname(f)}/* {tmp}/{d}", silent=True)
    call(f"mkdir -p {tmp}/{d}", silent=True)
    if p:
        logging.info("Custom file for generating packets specified")
        call(f"cp {p} {tmp}/{d}", silent=True)

    
    p4testgensuccess = False

    if packets:
        logging.debug(f"Using custom packets file{packets}")
        dd = f"{tmp}/{format_dir_name(f)}"
        call(f"cp {packets} {dd}")
        with open(packets, "r") as packets_file:
            packets = [l.strip() for l in packets_file.readlines()[1:]]
    else:
        # make test input files
        # print(os.path.basename(f))
        # print(f"{tmp}/{d}")
        # p4testgensuccess = False 
        if not p:
                s = p4testgen("bmv2", "v1model", os.path.basename(f), f"{tmp}/{d}", n)
        else:
                s = p4testgen("bmv2", "v1model", os.path.basename(p), f"{tmp}/{d}", n)


        packets =  parse_stf_files(f"{tmp}/{d}/out-p4testgen")
        p4testgensuccess = s

    # logging.debug(f"packets: {packets}")


    return (p4testgensuccess, packets)

def parse_stf_files(dir):
    logging.debug("CALLED parse_stf_files")
    tests = []
    for f in os.listdir(dir):
        if f.endswith(".stf"):
            with open(os.path.join(dir, f), "r") as f:
                lines = f.readlines()
                packets_str = [l for l in lines if l.lstrip().startswith("packet")]
                entries_str = [l for l in lines if l.lstrip().startswith("add")]

                packets = [extract_hex_packet(p) for p in packets_str]

                if len(packets) > 1 :
                    print(f"There are multiple packets in the stf file {f}")
                    sys.exit(1)
                else:
                    tests.append(packets[0])
    n_test = tests[0]
    return tests[1:]
def convert_to_timestamp(log_line):
    timestamp = re.search(r"\[(\d{2}:\d{2}:\d{2}\.\d+)\]", log_line).group(1)

    time_part, nanosec_part = timestamp.split('.')
    # print(timestamp_str)
    # print(f"convert_to_timestamp {time_part} {nanosec_part}")
    timestamp_obj = datetime.strptime(time_part, '%H:%M:%S')

    # Add the nanoseconds to the datetime object
    # timestamp_obj = timestamp_obj.replace(nanosecond=int(nanosec_part[:9]))

    # If you want nanoseconds separately, you can store them
    # nanoseconds = int(nanosec_part[6:])
    return timestamp_obj, nanosec_part

pattern_start = r"Parser\s+'([^']+)':\s+(start)"
pattern_end = r"Parser\s+'([^']+)':\s+(end)"

def process_p4s_log(lines):
    result_per_packet = []
    saving = False
    for line in lines:
        if re.search(pattern_start, line):
            saving = True
            result_per_packet.append([line])
            continue
        elif re.search(pattern_end, line):
            result_per_packet[-1].append(line)
            saving = False
            continue
        elif saving == True:
            result_per_packet[-1].append(line)
    return result_per_packet

def add_delay(result_per_packet, r):
    result = []
    for packet_log in result_per_packet:
        begin,end = packet_log[0], packet_log[-1]
        assert re.search(pattern_start, begin)
        assert re.search(pattern_end, end)

        t0, nanosec_part0 = convert_to_timestamp(begin)
        t1, nanosec_part1 = convert_to_timestamp(end)

        t0s = t0.hour * 3600 + t0.minute * 60 + t0.second
        t1s = t1.hour * 3600 + t1.minute * 60 + t1.second
        delay_in_nanoseconds = (t1s - t0s) * 10**9 + int(nanosec_part1) - int(nanosec_part0)

        result.append(Measurement(
            value=delay_in_nanoseconds,
            log=packet_log
        ))
    return result

def format_per_packet(result, packets, r):
    ret = []
    for i, packet in enumerate(packets):
        # print(f"format_per_packet {i} {packet}, {r}, {result}")
        corresponding_result = result[i:i+r]
        ret.append(Result(
            packet=packet,
            measurements=corresponding_result
        ))
    return ret

def run_bmv2(sf, packets, n, r, p, p4app_bin="submodules/p4app/p4app" ):
    d = format_dir_name(sf)
    tmp = "/tmp/p4ddg-experiment-runner-tmp"

    call(f"mkdir -p {tmp}/{d}", silent=True)
    call(f"cp {os.path.dirname(sf)}/* {tmp}/{d}", silent=True)
    call(f"mkdir -p {tmp}/{d}", silent=True)


    # copy the template
    call(f"cp -r template.p4app/* {tmp}/{d}", silent=True)
    call(f"touch {tmp}/{d}/packets.txt")
    with open(f"{tmp}/{d}/packets.txt", "w+") as packets_file:
        packets_file.write(f"{len(packets)}\n")
        for p in packets:
            packets_file.write(p + "\n")
    
    # print(f" REPEATPACKETS {args.r+1}")
    call(f"sed -i 's/REPEATPACKETS/{r}/g' {tmp}/{d}/p4app.json", silent=True)

    # Set the p4 file to be run in the p4app.json configuration
    name = os.path.basename(str(sf))
    call(f"sed -i 's/PROGRAM/{name}/g' {tmp}/{d}/p4app.json", silent=True)

    p4_app_dir = f"{tmp}/{d}"
    call(f"{p4app_bin} run {p4_app_dir}")
    # call(f"cat /tmp/p4app_logs/p4s.s1.log")
    # logs = 
    call(f"cp /tmp/p4app_logs/p4s.s1.log {p4_app_dir}/p4s.s1.log")
    call(f"rm -rf /tmp/p4app_logs/p4s.s1.log")
    # call(f"echo $PATH")
    lines_log = None
    with open(f"{p4_app_dir}/p4s.s1.log", "r") as f_log:
        lines_log = f_log.readlines()
    
    result = add_delay(process_p4s_log(lines_log), r)
    result = format_per_packet(result, packets, r)

    return result
    # delays = compute_delays_per_packet(timestamps, r)
    # 
    # avg_delay = compute_delay(timestamps)
    # print(f"Average delay for {f}: {avg_delay}")
    # logging.debug(f"Average delay for {f}: {avg_delay}")
    # if out_dir:
    #     call(f"cp -r {p4_app_dir}/* {out_dir}")
    #     call(f"cp /tmp/p4ddg-experiment-runner-log.txt {out_dir}")
    
    # split_by_r = analysis(lines_log, args.n, args.r)
    # c = []
    # logging.debug(f"539 {packets}")
    # for i, logs in enumerate(split_by_r):
    #     packet = packets[i]
    #     c.append({"logs": logs, "packet":packet})