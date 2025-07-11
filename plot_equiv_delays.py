import subprocess
import os
import sim
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.ticker import ScalarFormatter
from dataclasses import dataclass
from typing import List, Dict, TypeVar, Generic
plt.rcParams['text.usetex'] = True

T = TypeVar("T")

@dataclass
class BarChartBar:
    Id: str
    Value: float
    num_packets: int

@dataclass
class Chart(Generic[T]):
    Elements: Dict[str, List[T]]

def filter_out_short_packets(p):
    return [packet for packet in p if len(packet) > 32]

def get_equiv_pairs():
    pairs = []
    pairs = [
        ("programs/programs_with_equivalent_ddgs/firewall/firewall.p4", "programs/programs_with_equivalent_ddgs/firewall/firewall-ddg1.p4"),
    
        ("programs/programs_with_equivalent_ddgs/sfc-integrity/sfc.p4", "programs/programs_with_equivalent_ddgs/sfc-integrity/sfc-ddg1.p4"),
        ("programs/programs_with_equivalent_ddgs/tunnel/tunnel.p4", "programs/programs_with_equivalent_ddgs/tunnel/tunnel-ddg1.p4"),
        ("programs/programs_with_equivalent_ddgs/DetNetServices/detnetServices.p4", "programs/programs_with_equivalent_ddgs/DetNetServices/detnetServices-ddg1.p4"),
        ("programs/programs_with_equivalent_ddgs/cpsc435-switch-cache/cache.p4", "programs/programs_with_equivalent_ddgs/cpsc435-switch-cache/cache-ddg1.p4"),
        ("programs/programs_with_equivalent_ddgs/fastreact.p4app/fastreact.p4", "programs/programs_with_equivalent_ddgs/fastreact.p4app/fastreact-ddg1.p4"),
    ]



    return pairs
    

def mk_chart(chart, y_label="", out_name=""):
    keys = list(chart.Elements.keys())
    group_positions = np.arange(len(keys))
    bar_width = 0.2
    colors = ["red", "blue"]
    bar_offsets = {}
    fig, ax = plt.subplots(figsize=(12, 6))  # Increased figure width
    plt.ylabel(y_label)

    # Force scientific notation on y-axis
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    # Create single legend entries for each color
    legend_patches = [
        mpatches.Patch(color=colors[0], label="Original"),
        mpatches.Patch(color=colors[1], label="DDG"),
        mpatches.Patch(color='white', label="", alpha=0)  # Add empty line
    ]

    # Add invisible entries for each file showing packet counts
    for group_name in keys:
        num_packets = chart.Elements[group_name][0].num_packets
        legend_patches.append(
            mpatches.Patch(color='white', label=f"{group_name}: {num_packets} packets", alpha=0)
        )

    for group_idx, (group_name, bars_group) in enumerate(chart.Elements.items()):
        offset = 0
        for bar in bars_group:
            if bar.Id not in bar_offsets:
                bar_offsets[bar.Id] = offset
                offset += 1
            pos = group_positions[group_idx] + bar_offsets[bar.Id] * bar_width
            color = colors[bar_offsets[bar.Id] % len(colors)]
            ax.bar(pos, bar.Value, bar_width, color=color)

    ax.set_xticks(group_positions + bar_width)
    ax.set_xticklabels(keys, rotation=45, ha='right')

    # Add legend with both color entries and packet counts
    ax.legend(handles=legend_patches, loc="upper right", fontsize=8, title="Legend", frameon=False)
    plt.tight_layout()
    plt.savefig(f"img/{out_name}.png", dpi=300, bbox_inches="tight")
    plt.savefig(f"img/{out_name}.pdf", dpi=300, bbox_inches="tight")

def main():
    # Create output directory
    subprocess.call("mkdir -p img", shell=True)
    
    # Get equivalent pairs
    pairs = get_equiv_pairs()
    print(f"Found {len(pairs)} equivalent pairs to test")
    
    # Parameters for testing
    num_packets = 75
    repeat = 50
    
    
    # Store results
    elems = {}
    
    for original, ddg in pairs:
        base_name = os.path.splitext(os.path.basename(original))[0]
        print(f"Testing {original} and {ddg}")
        
        # Generate packets
        suc, packets_from_p4f = sim.prepare_run(original, None, num_packets, repeat, None)
        if not suc:
            print(f"P4TestGen failed for {original}")
            continue
            
        packets = filter_out_short_packets(list(set(packets_from_p4f)))
        
        # Run simulations
        r_original = sim.run_bmv2(original, packets, len(packets), repeat, None)
        r_ddg = sim.run_bmv2(ddg, packets, len(packets), repeat, None)
        
        # Calculate average delays
        delays_original = []
        delays_ddg = []
        
        for result in r_original:
            for measurement in result.measurements:
                delays_original.append(measurement.value)
                
        for result in r_ddg:
            for measurement in result.measurements:
                delays_ddg.append(measurement.value)
        
        avg_delay_original = sum(delays_original) / len(delays_original)
        avg_delay_ddg = sum(delays_ddg) / len(delays_ddg)
        
        elems[base_name] = [
            BarChartBar("Original", avg_delay_original, len(packets)),
            BarChartBar("DDG", avg_delay_ddg, len(packets))
        ]
    
    # Create and save chart
    chart = Chart(elems)
    mk_chart(chart, y_label="Average Delay (ns)", out_name="equiv_delays")
    print("Chart generated as img/equiv_delays")

if __name__ == "__main__":
    main()