import os
import sys
sys.path.append('../server')

from ax.service.ax_client import AxClient
from ax.storage.sqa_store.db import init_engine_and_session_factory
from ax.storage.sqa_store.structs import DBSettings
from matplotlib import font_manager
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np

# Plotting colors
PLOT_COLOR = 'hotpink'
LABEL_COLOR = 'dodgerblue'

plt.style.use('dark_background')

# Set font
font_path = 'JetBrainsMono-Regular.ttf'
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

def load_ax_client_db():
    DB_URL = os.getenv('MYSQL_URL')
    DB_URL = DB_URL.replace('mysql://', 'mysql+mysqldb://', 1)

    ax_client = AxClient(db_settings=DBSettings(url=DB_URL))
    init_engine_and_session_factory(url=DB_URL)
    ax_client.load_experiment_from_database('sloshzero')
    return ax_client

def load_ax_client_json():
    ax_client = AxClient.load_from_json_file('sloshzero.json')
    #ax_client = AxClient(db_settings=get_db_settings())
    #ax_client.load_experiment_from_database('sloshzero')
    return ax_client

def pareto_frontier(ax_client):
    x =  list(ax_client.get_pareto_optimal_parameters().values())

    F_slosh_vals = []
    V_baffle_vals = []
    for y in x:
        pareto_vals = y[1][0]
        F_slosh_vals.append(pareto_vals['F_slosh'])
        V_baffle_vals.append(pareto_vals['V_baffle'])

    F_slosh_vals = np.array(F_slosh_vals)
    V_baffle_vals = np.array(V_baffle_vals)

    return F_slosh_vals, V_baffle_vals

def plot_pareto_frontier(F_slosh_vals, V_baffle_vals):
    fig, ax = plt.subplots()
    ax.scatter(F_slosh_vals, V_baffle_vals, color=PLOT_COLOR, zorder=3, s=40)
    ax.set_title("Pareto Frontier", color=LABEL_COLOR)
    ax.set_xlabel("Peak Sloshing Force", color=LABEL_COLOR)
    ax.set_ylabel("Baffle Volume", color=LABEL_COLOR)
    ax.grid(True, zorder=0)
    fig.tight_layout()
    fig.savefig('pareto_front.svg', bbox_inches='tight', transparent=True)
    plt.close(fig)

def get_trace(ax_client):
    trace = np.array(ax_client.get_trace())
    indicies = np.arange(len(trace)) + 1

    return indicies, trace

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
    fig.savefig('trace.svg', bbox_inches='tight', transparent=True)
    plt.close(fig)

if __name__ == '__main__':
    ax_client = load_ax_client_json()

    F_slosh_vals, V_baffle_vals = pareto_frontier(ax_client)
    plot_pareto_frontier(F_slosh_vals, V_baffle_vals)

    indicies, trace = get_trace(ax_client)
    plot_trace(indicies, trace)
