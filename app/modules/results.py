from matplotlib import font_manager
from matplotlib import ticker
import matplotlib.pyplot as plt

# Plotting colors
PLOT_COLOR = 'hotpink'
LABEL_COLOR = 'dodgerblue'

plt.style.use('dark_background')

# Set font
font_path = '/static/fonts/JetBrainsMono-Regular.ttf'
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

def plot_pareto_frontier(F_slosh_vals, V_baffle_vals):
    fig, ax = plt.subplots()
    ax.scatter(F_slosh_vals, V_baffle_vals, color=PLOT_COLOR, zorder=3, s=40)
    ax.set_title("Pareto Frontier", color=LABEL_COLOR)
    ax.set_xlabel("Peak Sloshing Force", color=LABEL_COLOR)
    ax.set_ylabel("Baffle Volume", color=LABEL_COLOR)
    ax.grid(True, zorder=0)
    fig.tight_layout()
    fig.savefig('static/images/pareto_front.svg', bbox_inches='tight', transparent=True)
    plt.close(fig)

def plot_trace(indicies, trace):
    fig, ax = plt.subplots()
    ax.plot(indicies, trace, color=PLOT_COLOR, zorder=3, linewidth=2)
    ax.set_title("Hypervolume Convergence", color=LABEL_COLOR)
    ax.set_xlabel("Trial Number", color=LABEL_COLOR)
    ax.set_ylabel("Hypervolume", color=LABEL_COLOR)
    ax.set_xlim(left=1)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True, zorder=0)
    fig.tight_layout()
    fig.savefig('static/images/trace.svg', bbox_inches='tight', transparent=True)
    plt.close(fig)

def generate_plots():
    F_slosh_vals, V_baffle_vals = pareto_frontier(ax_client)
    plot_pareto_frontier(F_slosh_vals, V_baffle_vals)

    indicies, trace = get_trace(ax_client)
    plot_trace(indicies, trace)
