import copy
import os
from os.path import exists

from joblib import Memory
import numpy as np
import pandas as pd
import yaml
import csv

STRESS_CONSO = 1.358
columns = ["net_tplgy", "srv_tplgy", "rn_type", "size", "res"]
memory = Memory("/tmp", verbose=0)


@memory.cache
def get_df():
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
            if not exists(rel_run_num_dir) or len(os.listdir(rel_run_num_dir)) != int(size):
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

    return pd.DataFrame(
        esds_results,
        columns=columns
    )


net = ["clique", "star", "grid", "ring", "chain"]
rn = ["no_rn", "rn_agg", "rn_not_agg"]
colors = ["blue", "orange"]
srv = ["fav", "nonfav"]


energy_type = "static"
csvfile = open(f"e_{energy_type}.csv", "w")
csvwriter = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
csvwriter.writerow(["net_tplgy", "size", "energy_mean", "energy_std", "srv_tplgy", "rn_type"])
for rn_type in ["no_rn", "rn_agg", "rn_not_agg"]:
# rn_type = "rn_not_agg"
    def p(gb):
        list_gb = copy.deepcopy(columns)
        list_gb.remove("res")
        list_gb.remove(gb)
        list_gb = ["size"]
        df = get_df()

        res_cpt = 0
        all_res = []
        for key, pandas_vals in df.groupby(list_gb):
            # results = sorted(pandas_vals.values, key=lambda val: val[-1]["time"].mean(), reverse=True)
            vals_to_print = filter(lambda el: el[2] in [rn_type], pandas_vals.values)
            results = sorted(vals_to_print, key=lambda el: (net.index(el[0]), srv.index(el[1]), rn.index(el[2])))
            to_print = [key[0]]
            for res_num in range(len(results)):
                if results[res_num][:-1][0] in ["clique", "ring"] and results[res_num][:-1][1] == "nonfav":
                    continue
                # res_to_compare_num = len(results) - 1
                res_to_compare_num = res_num-1
                if res_to_compare_num > 0:
                    delta_dynamic = f' & {-round((results[res_to_compare_num][-1]["dynamic"].mean()-results[res_num][-1]["dynamic"].mean())*100/results[res_to_compare_num][-1]["dynamic"].mean(), 2)}\%'
                    delta_static = f' & {-round((results[res_to_compare_num][-1]["static"].mean()-results[res_num][-1]["static"].mean())*100/results[res_to_compare_num][-1]["static"].mean(), 2)}\%'
                    delta_time = f' & {-round((results[res_to_compare_num][-1]["time"].mean()-results[res_num][-1]["time"].mean())*100/results[res_to_compare_num][-1]["time"].mean(), 2)}\%'
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
                n = len(str(formatted_results['time']))
                # to_str = f"{formatted_results['dynamic']}{' '*(25-n)}{' '.join(map(str,results[res_num][:-1]))}"
                to_str = f"\cellcolor{{{colors[srv.index(results[res_num][:-1][1])]}!10}}{formatted_results[energy_type]}"
                to_print.append(to_str)
                # to_str = f"{formatted_results[energy_type]}"
                csvwriter.writerow([results[res_num][0], results[res_num][3], round(values[energy_type].mean(), 2), round(values[energy_type].std(), 2), results[res_num][1], rn_type])
                # if results[res_num][1] == "nonfav":
                #     to_str = f"{results[res_num][:-1]}, {formatted_results['dynamic']}"
                # print(to_str, end=" & ")
            print(*to_print, sep=" & ", end="\\\\\n\\hline\n")
            all_res.append(results)
            # print()
            if res_cpt > 0:
                to_print = [""]
                for prev, curr in zip(all_res[0], all_res[res_cpt]):
                    if curr[:-1][0] in ["clique", "ring"] and curr[:-1][1] == "nonfav":
                        continue
                    delta = f' {-round((prev[-1][energy_type].mean() - curr[-1][energy_type].mean()) * 100 / prev[-1][energy_type].mean(), 2)}\%'
                    to_print.append(delta)
                print(*to_print, sep=" & &", end="\\\\\n\\hline\n")
            res_cpt += 1
        print(gb)
        print(columns)


    p("size")

csvfile.close()
