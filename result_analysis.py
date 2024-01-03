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
            "dynamic": [],
            "total": []
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
                "dynamic": 0,
                "total": 0
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
                accumulated_results["total"] += idle + reconf + res["comms_cons"]

            results_runs["comms"].append(accumulated_results["comms"])
            results_runs["time"].append(accumulated_results["time"])
            results_runs["reconf"].append(accumulated_results["reconf"])
            results_runs["static"].append(accumulated_results["static"])
            results_runs["dynamic"].append(accumulated_results["dynamic"])
            results_runs["total"].append(accumulated_results["total"])

        np_results = {
            "comms": np.array(results_runs['comms']),
            "reconf": np.array(results_runs['reconf']),
            "time": np.array(results_runs['time']),
            "static": np.array(results_runs['static']),
            "dynamic": np.array(results_runs['dynamic']),
            "total": np.array(results_runs['total']),
        }

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

m = {
    "fav": "best",
    "nonfav": "worst",
    "no_rn": "No RN",
    "rn_agg": "RN on agg",
    "rn_not_agg": "RN not on agg"
}

# indexes = [("fav","no_rn"), ("nonfav","no_rn"), ("fav","rn_agg"), ("nonfav","rn_agg"), ("fav","rn_not_agg"), ("nonfav","rn_not_agg")]
indexes = [("fav","clique"), ("nonfav","clique"), ("fav","star"), ("nonfav","star"), ("fav","grid"), ("nonfav","grid"), ("fav","ring"), ("nonfav","ring"), ("fav","chain"), ("nonfav","chain")]

for energy_type in ["total", "dynamic", "time"]:
    csvfile_name = f"e_{energy_type}.csv"
    csvfile = open(csvfile_name, "w")
    csvwriter = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
    csvwriter.writerow(["net_tplgy", "size", "energy_mean", "energy_std", "srv_tplgy", "rn_type", "srv_tplgy_index"])
    for rn_type in ["no_rn", "rn_agg", "rn_not_agg"]:
    # rn_type = "rn_not_agg"
        def p(gb, rn_type, energy_type):
            list_gb = copy.deepcopy(columns)
            list_gb.remove("res")
            list_gb.remove(gb)
            list_gb = ["size"]
            df = get_df()

            for key, pandas_vals in df.groupby(list_gb):
                vals_to_print = filter(lambda el: el[2] in [rn_type] and el[0] not in ["starchain", "tree"], pandas_vals.values)
                results = sorted(vals_to_print, key=lambda el: (net.index(el[0]), srv.index(el[1]), rn.index(el[2])))
                for res_num in range(len(results)):
                    index = indexes.index((results[res_num][1], results[res_num][0]))
                    values = results[res_num][-1]
                    if energy_type == "total":
                        div = 1000
                    elif energy_type == "time":
                        div = 3600
                    else:
                        div = 1
                    csvwriter.writerow([results[res_num][0], results[res_num][3], f"{values[energy_type].mean()/div:.2f}", f"{values[energy_type].std()/div:.2f}", m[results[res_num][1]], m[rn_type], index])

        p("size", rn_type, energy_type)

    csvfile.close()
    print(f"csv: {csvfile_name}")
