import sys
sys.path.append('../fastapi_server')

from ax.service.ax_client import AxClient
import matplotlib.pyplot as plt
import numpy as np

def load_ax_client():
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
    ax.scatter(F_slosh_vals, V_baffle_vals, color='dodgerblue')
    ax.set_title("Pareto Frontier", fontsize='large')
    ax.set_xlabel("Peak Sloshing Force", fontsize='large')
    ax.set_ylabel("Baffle Volume", fontsize='large')
    ax.grid(True)
    plt.show()
    plt.close(fig)

def get_trace(ax_client):
    trace = np.array(ax_client.get_trace())
    indicies = np.arange(len(trace)) + 1

    return indicies, trace

def plot_trace(indicies, trace):
    fig, ax = plt.subplots()
    ax.plot(indicies, trace, color='dodgerblue')
    ax.set_title("Hypervolume Convergence", fontsize='large')
    ax.set_xlabel("Trial Number", fontsize='large')
    ax.set_ylabel("Hypervolume", fontsize='large')
    ax.grid(True)
    plt.show()
    plt.close(fig)

if __name__ == '__main__':
    ax_client = load_ax_client()

    F_slosh_vals, V_baffle_vals = pareto_frontier(ax_client)
    plot_pareto_frontier(F_slosh_vals, V_baffle_vals)

    indicies, trace = get_trace(ax_client)
    plot_trace(indicies, trace)
