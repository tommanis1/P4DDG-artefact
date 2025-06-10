from dataclasses import dataclass
from typing import List 
import matplotlib.pyplot as plt
import numpy as np

@dataclass
class LinesResult:
    result:list
    name:str

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

    plt.figure()

    for line in lines:
        plt.plot(x_axis, line.result, label=line.name)

    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    # plt.title(title)
    plt.legend()
    # plt.xticks(ticks=x_axis, labels=[str(int(x)) for x in x_axis], rotation=-90, ha="right")
    tick_indices = np.arange(0, len(x_axis), 4)
    tick_values = [x_axis[i] for i in tick_indices]
    tick_labels = [str(int(x)) for x in tick_values]

    plt.xticks(ticks=tick_values, labels=tick_labels, rotation=45, ha="right")
    # plt.gcf().autofmt_xdate()

    plt.savefig(fp, dpi=300, bbox_inches="tight")
    plt.savefig(fp + ".pdf", bbox_inches="tight")
