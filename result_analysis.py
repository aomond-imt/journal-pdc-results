import copy
import os

import numpy as np
import pandas as pd
import yaml

STRESS_CONSO = 1.358

results_dir = "raw_results"
esds_results = []
for expe_dir in os.listdir(results_dir):
    rel_expe_dir = f"{results_dir}/{expe_dir}"
    net_tplgy, srv_tplgy, rn_type, size = expe_dir.split("-")
    results_runs = {
        "comms": [],
        "time": [],
        "idle": [],
        "reconf": [],
        "static": [],
        "dynamic": []
    }
    for run_num in range(30):
        rel_run_num_dir = f"{rel_expe_dir}/{run_num}"
        if len(os.listdir(rel_run_num_dir)) != int(size):
            continue
        accumulated_results = {
            "comms": 0,
            "time": 0,
            "idle": 0,
            "reconf": 0,
            "static": 0,
            "dynamic": 0
        }
        for node_num in range(int(size)):
            with open(f"{rel_run_num_dir}/{node_num}.yaml") as f:
                res = yaml.safe_load(f)
            reconf = res["tot_reconf_duration"]*STRESS_CONSO
            idle = res["node_cons"] - reconf
            accumulated_results["comms"] += res["comms_cons"]
            accumulated_results["time"] = max(res["global_termination_time"], accumulated_results["time"])
            accumulated_results["reconf"] += reconf
            accumulated_results["static"] += idle
            accumulated_results["dynamic"] += reconf + res["comms_cons"]

        results_runs["comms"].append(accumulated_results["comms"])
        results_runs["time"].append(accumulated_results["time"])
        results_runs["reconf"].append(accumulated_results["reconf"])
        results_runs["static"].append(accumulated_results["static"])
        results_runs["dynamic"].append(accumulated_results["dynamic"])

    np_results = {
        "comms": np.array(results_runs['comms']),
        "reconf": np.array(results_runs['reconf']),
        "time": np.array(results_runs['time']),
        "static": np.array(results_runs['static']),
        "dynamic": np.array(results_runs['dynamic']),
    }
    # formatted_results = {
    #     "comms": f"{round(np_results['comms'].mean(), 2)} J ({round(np_results['comms'].std(), 2)})",
    #     "idle": f"{round(np_results['idle'].mean()/1000, 2)} kJ ({round(np_results['idle'].std()/1000, 2)})",
    #     "reconf": f"{round(np_results['reconf'].mean(), 2)} J ({round(np_results['reconf'].std(), 2)})",
    #     "time": f"{round(np_results['time'].mean()/3600, 2)} h ({round(np_results['time'].std()/3600, 2)})",
    # }
    # formatted_results = {
    #     "dynamic": f"{round(np_results['dynamic'].mean(), 2)} J ({round(np_results['dynamic'].std(), 2)})",
    #     "static": f"{round(np_results['static'].mean()/1000, 2)} kJ ({round(np_results['static'].std()/1000, 2)})",
    #     "time": f"{round(np_results['time'].mean() / 3600, 2)} h ({round(np_results['time'].std() / 3600, 2)})"
    # }

    esds_results.append(
        (net_tplgy, srv_tplgy, rn_type, int(size), np_results)
    )
    if net_tplgy in ["clique", "ring"]:
        esds_results.append(
            (net_tplgy, "nonfav", rn_type, int(size), np_results)
        )

columns = ["net_tplgy", "srv_tplgy", "rn_type", "size", "res"]

d = pd.DataFrame(
    esds_results,
    columns=columns
)


def p(gb):
    list_gb = copy.deepcopy(columns)
    list_gb.remove("res")
    list_gb.remove(gb)
    for key, pandas_vals in d.groupby(list_gb):
        print(key)
        results = sorted(pandas_vals.values, key=lambda val: val[-1]["time"].mean(), reverse=True)
        for res_num in range(len(results)):
            # res_to_compare_num = len(results) - 1
            res_to_compare_num = res_num+1
            if res_to_compare_num < len(results):
                delta_dynamic = f' {-round((results[res_to_compare_num][-1]["dynamic"].mean()-results[res_num][-1]["dynamic"].mean())*100/results[res_to_compare_num][-1]["dynamic"].mean(), 2)}%'
                delta_static = f' {-round((results[res_to_compare_num][-1]["static"].mean()-results[res_num][-1]["static"].mean())*100/results[res_to_compare_num][-1]["static"].mean(), 2)}%'
                delta_time = f' {-round((results[res_to_compare_num][-1]["time"].mean()-results[res_num][-1]["time"].mean())*100/results[res_to_compare_num][-1]["time"].mean(), 2)}%'
            else:
                delta_dynamic = ""
                delta_static = ""
                delta_time = ""
            values = results[res_num][-1]
            formatted_results = {
                "dynamic": f"{round(values['dynamic'].mean(), 2)} J ({round(values['dynamic'].std(), 2)}){delta_dynamic}",
                "static": f"{round(values['static'].mean()/1000, 2)} kJ ({round(values['static'].std()/1000, 2)}){delta_static}",
                "time": f"{round(values['time'].mean() / 3600, 2)} h ({round(values['time'].std() / 3600, 2)}){delta_time}"
            }
            n = len(str(formatted_results))
            to_str = f"{formatted_results}{' '*(125-n)}{' '.join(map(str,results[res_num][:-1]))}"
            print(to_str)

    print(gb)
    print(columns)


p("size")
