import argparse
import subprocess
import line_plot
import ast
import sim
import sys
from typing import NamedTuple, List
import logging
from dataclasses import dataclass
from typing import List, Dict, TypeVar, Generic
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

plt.rcParams['text.usetex'] = True

# import parser as p

N_PACKETS=128
REPEAT_EACH_PACKET = 50

def write_to_file(chart, filename):
    with open(filename, "w") as f:
        for group_name, bars_group in chart.Elements.items():
            for bar in bars_group:
                f.write(f"{group_name},{bar.Id},{bar.Value}\n")

def decimal_to_hex_string(decimal_number, pad=4):
    """Convert a decimal number to a hexadecimal string with leading zeros."""
    hex_string = hex(decimal_number)[2:]  # Convert to hex and remove '0x'
    return hex_string.zfill(pad)  # Pad with leading zeros

def parse_list(string):
    begin = string.split("Result for")[-1].split("[")[-1]
    ls = "[" + begin
    l = ast.literal_eval(ls)
    return l

def filter_out_short_packets(p):
    return [packet for packet in p if len(packet) > 32]


def mk_chart(chart=None ,y_label="", out_name=""):
    keys = list(chart.Elements.keys())
    group_positions = np.arange(len(keys))
    bar_width = 0.2
    colors = ["red", "blue", "green", "yellow"]
    
    bar_offsets = {}

    fig, ax = plt.subplots()
    plt.ylabel(y_label)


    patches = {}

    for group_idx, (group_name, bars_group) in enumerate(chart.Elements.items()):
        offset = 0
        group_patches = []
        for bar in bars_group:
            if bar.Id not in bar_offsets:
                bar_offsets[bar.Id] = offset
                offset += 1
            pos = group_positions[group_idx] + bar_offsets[bar.Id] * bar_width
            color = colors[bar_offsets[bar.Id] % len(colors)]
            ax.bar(pos, bar.Value, bar_width, color=color)
            group_patches.append(mpatches.Patch(color=color, label=f"   {bar.Id}"))  
        patches[group_name] = group_patches

    ax.set_xticks(group_positions + bar_width)
    ax.set_xticklabels(keys)

    custom_legend = []
    for group, group_patches in patches.items():
        custom_legend.append(mpatches.Patch(color="white", label=f"{group}:", alpha=0))  
        custom_legend.extend(group_patches)

    ax.legend(handles=custom_legend, loc="upper right", fontsize=8, title="Legend", frameon=False, bbox_to_anchor=(1.35, 1))

    plt.savefig(f"img/{out_name}", dpi=300, bbox_inches="tight")

def main():




            




            
            files = {
                "hand-written" : "programs/stack_usage/stack_usage.p4"
                # , "stack_usage-ddg" : "programs/stack_usage/stack_usage-ddg.p4"
                , "ddg" : "programs/stack_usage/stack_usage-ddg-single-result.p4"

                # , "stack_usage-ddg-loop" : "programs/stack_usage/stack_usage-ddg-loop.p4"
                # , "stack-usage-no-result-stack": "programs/stack_usage/stack_usage-no-result-array.p4"
                , "Kleene" : "programs/stack_usage/stack_usage-ddg-loop.p4"
            }

            # Prep result dir
            # collection_dir = "/tmp/p4ddg-experiment-stack_usage"
            # subprocess.call("mkdir -p {collection_dir}", shell=True)
            # subprocess.call("rm -rf {collection_dir}", shell=True)
            # subprocess.call("mkdir -p {collection_dir}", shell=True)
            num_packets = N_PACKETS
            packets = [ decimal_to_hex_string(i, pad=4) + i * "00000000000000000000000000000000" for i in range(1, num_packets+1)]
            generated_packets_file = "programs/stack_usage/packets_generated.txt"
            with open(generated_packets_file, "w") as f:
                f.write(f"{num_packets}\n")
                for packet in packets:
                    f.write(packet + "\n")
            
            title = "Parser delay for different levels of stack usage"
            x_label = "Number of Headers"
            y_label = "Delay (ns)"
            # caption = ""
            # args = "--debug "
            # for k,v in options[o].items():
            # args += "-n " + str(N_PACKETS) + " "
            # args += "-r " + str(REPEAT_EACH_PACKET) + " "
            results = []
            
            for desc,file in files.items():
                collection_dir = "stack_usage"
                out_dir = f"{collection_dir}/{desc}"
                subprocess.call(f"mkdir -p {out_dir}", shell=True)
                
                sim.prepare_run(file, generated_packets_file, N_PACKETS, REPEAT_EACH_PACKET, None)
                r = sim.run_bmv2(file, packets, N_PACKETS, REPEAT_EACH_PACKET, None)
                # print(f"r {r}")
                # delays = []
                # First get all measurements for each packet across all runs
                # print(f"len r 0 : {len(r[0].measurements)}")
                # print(f"len r : {len(r)}")
                # for packet_idx in range(len(r[0].measurements)):
                #     packet_delays = []
                #     for packet_run in r:
                #         packet_delays.append(packet_run.measurements[packet_idx].value)
                #     avg = sum(packet_delays)/len(packet_delays)
                #     delays.append(avg)
                # print(f"len delays {len(delays)} ")
                # results.append((desc, delays))
                delays = []
                std_errors = []
                print(f"len(results): {len(r)}")
                for result in r:
                    d = []
                    for m in result.measurements:
                        d.append(m.value)
                    avg = sum(d)/len(d)
                    # Calculate standard error of the mean (SEM)
                    std_dev = np.std(d, ddof=1)  # ddof=1 for sample standard deviation
                    sem = std_dev / np.sqrt(len(d))
                    print(f"len(d) {len(d)} {d}")
                    delays.append(avg)
                    std_errors.append(sem)
                results.append((desc, delays, std_errors))

                subprocess.call(f"cp /tmp/p4ddg-experiment-runner-log.txt {out_dir}", shell=True)
                subprocess.call(f"cp -r /tmp/p4ddg-experiment-runner-tmp/ {out_dir}",  shell=True)
            
            plot_data = line_plot.Plot(
                x_axis=list(range(1, num_packets+1)), 
                x_axis_label=x_label,
                y_axis_label=y_label,
                title=title,
                lines=[
                    line_plot.LinesResult(
                        result=delays,
                        name=desc,
                        yerr=std_errors
                    ) for desc, delays, std_errors in results
                ]
            )
            line_plot.plot_graph(plot_data, "img/stack-usage-graph")

            # print(decimal_to_hex_string(32, pad=4))
            # print(f"Results {results}:")
            print("Image created")


if __name__ == "__main__":
    main()