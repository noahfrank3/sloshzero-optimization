from pathlib import Path

from matplotlib import font_manager
from matplotlib import ticker
import matplotlib.pyplot as plt

from app.modules.logging_utils import new_logger
from config.config import config

logger = new_logger('Results')

IMAGE_PATH = 'static/images'
FONT_PATH = 'static/fonts/JetBrainsMono-Regular.ttf'

root_dir = Path(config['general']['root_dir'])
image_path = root_dir / IMAGE_PATH
font_path = root_dir / FONT_PATH

# Plotting colors
PLOT_COLOR = 'hotpink'
LABEL_COLOR = 'dodgerblue'

plt.style.use('dark_background')

# Set font
font_manager.fontManager.addfont(font_path)
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

# Other global plotting parameters
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['grid.linewidth'] = 0.25
plt.rcParams['axes.labelpad'] = 15
plt.rcParams['axes.titlepad'] = 15

def plot_pareto_frontier(objective_1_vals, objective_2_vals, objective_1_name, objective_2_name):
    fig, ax = plt.subplots()
    ax.scatter(objective_1_vals, objective_2_vals, color=PLOT_COLOR, zorder=3, s=40)
    ax.set_title("Pareto Frontier", color=LABEL_COLOR)
    ax.set_xlabel(objective_1_name, color=LABEL_COLOR)
    ax.set_ylabel(objective_2_name, color=LABEL_COLOR)
    ax.grid(True, zorder=0)
    fig.tight_layout()
    fig.savefig(image_path / 'pareto_front.svg', bbox_inches='tight', transparent=True)
    plt.close(fig)

def plot_trace(trace_indicies, trace):
    fig, ax = plt.subplots()
    ax.plot(trace_indicies, trace, color=PLOT_COLOR, zorder=3, linewidth=2)
    ax.set_title("Hypervolume Convergence", color=LABEL_COLOR)
    ax.set_xlabel("Trial Number", color=LABEL_COLOR)
    ax.set_ylabel("Hypervolume", color=LABEL_COLOR)
    ax.set_xlim(left=1)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True, zorder=0)
    fig.tight_layout()
    fig.savefig(image_path / 'trace.svg', bbox_inches='tight', transparent=True)
    plt.close(fig)

def generate_plots(ax_client):
    objective_1_vals, objective_2_vals = ax_client.get_pareto_front()
    trace_indices, trace_vals = ax_client.get_trace()

    objective_1_name = 'Peak Sloshing Force'
    objective_2_name = 'Total Baffle Volume'
    
    plot_pareto_frontier(objective_1_vals, objective_2_vals, objective_1_name, objective_2_name)
    plot_trace(trace_indices, trace_vals)
