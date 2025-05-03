import os
import re
import json
import glob

K = 32
PLOTTER = "chiapos"
LOGS_DIR = "logs"

def parse_chia_log(log_file_path):

    data = {
        "Parameters": {
            "k": None,
            "buffer_size": None,
            "buckets": None,
            "nb_threads": None,
            "compression": None
        },
        "Phase 1": {},
        "Phase 2": {},
        "Phase 3": {},
        "Phases times": {},
        "Final Stats": []
    }

    with open(log_file_path, 'r') as log_file:
        log_lines = log_file.readlines()

    # Initial parameters
    data["Parameters"]["k"] = log_lines[3].split(":")[1].strip()
    data["Parameters"]["buffer_size"] = log_lines[4].split(":")[1].strip()
    data["Parameters"]["buckets"] = log_lines[5].split()[1].strip()

    phase_1_table = re.compile(r'Computing table (\d+)')
    phase_1_table_time = re.compile(r'Forward propagation table time: (\d+(?:\.\d+)?) seconds\. CPU \((\d+(?:\.\d+)?)%\)')
    phase_1_table_time_F1 = re.compile(r'F1 complete, time: (\d+(?:\.\d+)?) seconds\. CPU \((\d+(?:\.\d+)?)%\)')
    
    phase_2_table = re.compile(r'Backpropagating on table (\d+)')
    phase_2_table_scan_time = re.compile(r'scanned time =\s+(\d+(?:\.\d+)?) seconds\. CPU \((\d+(?:\.\d+)?)%\)')
    phase_2_table_sort_time = re.compile(r'sort time =\s+(\d+(?:\.\d+)?) seconds\. CPU \((\d+(?:\.\d+)?)%\)')
    
    phase_3_tables = re.compile(r'Compressing tables (\d+) and (\d+)')
    phase_3_table_time = re.compile(r'First computation pass time: (\d+(?:\.\d+)?) seconds\. CPU \((\d+(?:\.\d+)?)%\)')
    phase_3_table_time_second = re.compile(r'Second computation pass time: (\d+(?:\.\d+)?) seconds\. CPU \((\d+(?:\.\d+)?)%\)')
    phase_3_total_time = re.compile(r'Total compress table time: (\d+(?:\.\d+)?) seconds\. CPU \((\d+(?:\.\d+)?)%\)')
    
    phase_time = re.compile(r'Time for phase (\d) = (\d+(?:\.\d+)?) seconds\. CPU \((\d+(?:\.\d+)?)%\)')
    final_stats = re.compile(r'(Approximate working space used \(without final file\)|Final File size|Total time) = (\d+\.\d+|\d+) (GiB|seconds)\. CPU \((\d+\.\d+)%\)')

    current_phase = None
    current_table = None

    for line in log_lines:
        if "Starting phase 1/4" in line:
            current_phase = "Phase 1"
        elif "Starting phase 2/4" in line:
            current_phase = "Phase 2"
        elif "Starting phase 3/4" in line:
            current_phase = "Phase 3"
        elif "Starting phase 4/4" in line:
            current_phase = "Phase 4"

        if current_phase == "Phase 1":
            if "Computing table" in line:
                match = phase_1_table.search(line)
                if match:
                    current_table = match.group(1)
            elif "F1 complete" in line:
                match = phase_1_table_time_F1.search(line)
                if match:
                    time_value = match.group(1)
                    cpu_value = match.group(2)
                    data["Phase 1"][current_table] = data["Phase 1"].get(current_table, {})
                    data["Phase 1"][current_table]["Forward propagation"] = {"time": time_value, "cpu": cpu_value}
            elif "Forward propagation table time" in line:
                match = phase_1_table_time.search(line)
                if match:
                    time_value = match.group(1)
                    cpu_value = match.group(2)
                    data["Phase 1"][current_table] = data["Phase 1"].get(current_table, {})
                    data["Phase 1"][current_table]["Forward propagation"] = {"time": time_value, "cpu": cpu_value}

        elif current_phase == "Phase 2":
            if "Backpropagating on table" in line:
                match = phase_2_table.search(line)
                if match:
                    current_table = match.group(1)
            elif "scanned time" in line:
                match = phase_2_table_scan_time.search(line)
                if match:
                    time_value = match.group(1)
                    cpu_value = match.group(2)
                    data["Phase 2"][current_table] = data["Phase 2"].get(current_table, {})
                    data["Phase 2"][current_table]["Backpropagation scanned"] = {"time": time_value, "cpu": cpu_value}
            elif "sort time" in line:
                match = phase_2_table_sort_time.search(line)
                if match:
                    time_value = match.group(1)
                    cpu_value = match.group(2)
                    data["Phase 2"][current_table] = data["Phase 2"].get(current_table, {})
                    data["Phase 2"][current_table]["Backpropagation sort"] = {"time": time_value, "cpu": cpu_value}

        elif current_phase == "Phase 3":
            if "Compressing tables" in line:
                match = phase_3_tables.search(line)
                if match:
                    current_table = match.group(1) + "-" + match.group(2)
            elif "First computation pass time" in line:
                match = phase_3_table_time.search(line)
                if match:
                    time_value = match.group(1)
                    cpu_value = match.group(2)
                    data["Phase 3"][current_table] = data["Phase 3"].get(current_table, {})
                    data["Phase 3"][current_table]["First computation pass"] = {"time": time_value, "cpu": cpu_value}
            elif "Second computation pass time" in line:
                match = phase_3_table_time_second.search(line)
                if match:
                    time_value = match.group(1)
                    cpu_value = match.group(2)
                    data["Phase 3"][current_table] = data["Phase 3"].get(current_table, {})
                    data["Phase 3"][current_table]["Second computation pass"] = {"time": time_value, "cpu": cpu_value}
            elif "Total compress table time" in line:
                match = phase_3_total_time.search(line)
                if match:
                    time_value = match.group(1)
                    cpu_value = match.group(2)
                    data["Phase 3"][current_table] = data["Phase 3"].get(current_table, {})
                    data["Phase 3"][current_table]["Total compress table"] = {"time": time_value, "cpu": cpu_value}

        if "Time for phase" in line:
            match = phase_time.search(line)
            if match:
                phase = match.group(1)
                time_value = match.group(2)
                cpu_value = match.group(3)
                # data[f"Phase {phase}"] = data.get(f"Phase {phase}", {})
                # data[f"Phase {phase}"]["Total phase"] = {"time": time_value, "cpu": cpu_value}
                data["Phases times"][phase] = {"time": time_value, "cpu": cpu_value}

        if any(keyword in line for keyword in ["Approximate working space used", "Final File size", "Total time"]):
            match = final_stats.search(line)
            if match:
                stat_type = match.group(1)
                value = match.group(2)
                unit = match.group(3)
                cpu_value = match.group(4) if match.group(4) else None
                data["Final Stats"].append({"stat_type": stat_type, "value": value, "unit": unit, "cpu": cpu_value})
    

    return data


def save_to_json(data, file_path):
    file_path = file_path.split("output/")
    json_dir = file_path[0]
    json_dir = os.path.join(json_dir, "json")
    os.makedirs(json_dir, exist_ok=True)
    file_name = file_path[1].split(".")[0] + ".json"
    json_file_path = os.path.join(json_dir, file_name)

    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


if __name__ == "__main__":
    log_files = glob.glob(os.path.join(LOGS_DIR,'k'+str(K),PLOTTER, "output", "*.txt"), recursive=True)
    for log_file in log_files:
        data = parse_chia_log(log_file)
        save_to_json(data, log_file)
        print(f"Parsed {log_file} and saved to JSON.")
    print(f"Parsed {log_file} and saved to JSON.")
