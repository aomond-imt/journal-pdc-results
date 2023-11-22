import os

import pandas as pd
import yaml

STRESS_CONSO =1.358

results_dir = "raw_results"
esds_results = []
for expe_dir in os.listdir(results_dir):
    abs_expe_dir = f"{results_dir}/{expe_dir}"
    coord_name, net_tplgy, srv_tplgy, size, upt_duration = expe_dir.split("-")
    for id_run in os.listdir(abs_expe_dir)[:10]:
        try:
            abs_id_run_dir = f"{abs_expe_dir}/{id_run}"
            accumulated_results = {
                "comms": 0,
                "time": 0,
                "idle": 0,
                "reconf": 0
            }
            for node_file in os.listdir(abs_id_run_dir):
                if node_file.endswith(".yaml") and node_file.split(".")[0].isdigit():
                    with open(f"{abs_id_run_dir}/{node_file}") as f:
                        res = yaml.safe_load(f)
                        reconf = res["tot_reconf_duration"]*STRESS_CONSO
                        accumulated_results["comms"] += res["comms_cons"]
                        accumulated_results["idle"] += res["node_cons"] - reconf
                        accumulated_results["reconf"] += reconf
                        accumulated_results["time"] = max(res["global_termination_time"], accumulated_results["time"])

            formatted_results = {
                "comms": f"{round(accumulated_results['comms'], 2)} J",
                "idle": f"{round(accumulated_results['idle']/1000, 2)} kJ",
                "reconf": f"{round(accumulated_results['reconf'], 2)} J",
                "time": f"{round(accumulated_results['time']/3600, 2)} h",
            }

            esds_results.append(
                (coord_name, net_tplgy, srv_tplgy, size, upt_duration, id_run, formatted_results)
            )
        except FileNotFoundError as e:
            continue

d = pd.DataFrame(
    esds_results,
    columns=("coord_name", "net_tplgy", "srv_tplgy", "size", "upt_duration", "id_run", "res")
)

for key, pandas_vals in d.groupby("net_tplgy"):
    print(key)
    for v in sorted(pandas_vals.values, key=lambda val: float(val[-1]["time"][:-2]), reverse=True):
        n = len(str(v[-1]))
        to_str = f"{v[-1]}{' '*(90-n)}{' '.join(v[:-1])}"
        print(to_str)

