from dataclasses import dataclass
from typing import List 
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['text.usetex'] = True

@dataclass
class LinesResult:
    result: list
    name: str
    yerr: list = None

@dataclass
class Plot:
    x_axis: list
    x_axis_label: str
    y_axis_label: str
    title: str
    lines: List[LinesResult]

def plot_graph(plot: Plot, fp):
    x_axis = plot.x_axis
    x_axis_label = plot.x_axis_label
    y_axis_label = plot.y_axis_label
    title = plot.title
    lines = plot.lines

    plt.figure(figsize=(10, 6))

    for line in lines:
        if line.yerr is not None:
            plt.errorbar(x_axis, line.result, 
                        yerr=line.yerr,
                        label=line.name,
                        capsize=3,
                        capthick=1,
                        elinewidth=1,
                        marker='o',
                        markersize=4,
                        linestyle='-',
                        alpha=0.8)
        else:
            plt.plot(x_axis, line.result, label=line.name)

    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    tick_indices = np.arange(0, len(x_axis), 8)  # Show fewer ticks for clarity
    tick_values = [x_axis[i] for i in tick_indices]
    tick_labels = [str(int(x)) for x in tick_values]

    plt.xticks(ticks=tick_values, labels=tick_labels, rotation=45, ha="right")
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    plt.savefig(fp, dpi=300, bbox_inches="tight")
    plt.savefig(fp + ".pdf", bbox_inches="tight")
