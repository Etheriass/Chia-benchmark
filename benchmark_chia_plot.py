import os
import subprocess
import threading
import time
import psutil 
from benchmark_log_parser import parse_chia_log, save_to_json

LOGS_DIR = "logs" 
MONITOR_INTERVAL = 1  # seconds

def monitor_process(pid, output_file, stop_event):
    proc = psutil.Process(pid)

    with open(output_file, 'w') as f:
        f.write("timestamp,cpu_percent,ram_used_mb,ram_percent,read_MBps,write_MBps,read_IOPS,write_IOPS\n")

        last_read_bytes = 0
        last_write_bytes = 0
        last_read_count = 0
        last_write_count = 0
        last_time = time.time()

        while not stop_event.is_set():
            timestamp = time.strftime("%H:%M:%S")

            try:
                # parent + children
                procs = [proc] + proc.children(recursive=True)

                # CPU (waits 0.5s)
                cpu_percent = sum(p.cpu_percent(interval=MONITOR_INTERVAL) for p in procs)

                # RAM sum
                total_rss = 0
                total_mem_percent = 0
                for p in procs:
                    try:
                        mem_info = p.memory_info()
                        total_rss += mem_info.rss
                        total_mem_percent += p.memory_percent()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                ram_used_mb = total_rss / 1024 / 1024
                ram_percent = total_mem_percent

                # IO sum
                total_read_bytes = 0
                total_write_bytes = 0
                total_read_count = 0
                total_write_count = 0
                for p in procs:
                    try:
                        io = p.io_counters()
                        total_read_bytes += io.read_bytes
                        total_write_bytes += io.write_bytes
                        total_read_count += io.read_count
                        total_write_count += io.write_count
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                now_time = time.time()
                delta_seconds = now_time - last_time
                if delta_seconds == 0:
                    delta_seconds = 1e-6

                read_MBps = (total_read_bytes - last_read_bytes) / 1024 / 1024 / delta_seconds
                write_MBps = (total_write_bytes - last_write_bytes) / 1024 / 1024 / delta_seconds
                read_IOPS = (total_read_count - last_read_count) / delta_seconds
                write_IOPS = (total_write_count - last_write_count) / delta_seconds

                f.write(f"{timestamp},{cpu_percent:.2f},{ram_used_mb:.2f},{ram_percent:.2f},{read_MBps:.2f},{write_MBps:.2f},{read_IOPS:.2f},{write_IOPS:.2f}\n")
                f.flush()

                last_read_bytes = total_read_bytes
                last_write_bytes = total_write_bytes
                last_read_count = total_read_count
                last_write_count = total_write_count
                last_time = now_time

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break


def run_plotter(k, threads, buckets, plotter, compression=0, to_json=True, tmp_dir='plot/tmp', dst_dir='plot/final'):
    log_file = f"log_k{k}_{threads}t_{buckets}b_c{compression}"
    dir_log_file = os.path.join(LOGS_DIR, "k" + str(k), plotter, 'output')
    dir_res_file = os.path.join(LOGS_DIR, "k" + str(k), plotter, 'res')
    os.makedirs(dir_log_file, exist_ok=True)
    os.makedirs(dir_res_file, exist_ok=True)
    log_file_path = os.path.join(dir_log_file, log_file + ".txt")
    log_res_file_path = os.path.join(dir_res_file, log_file + "_res.csv")

    plot_cmd = [
        "chia",
        "plotters",
        plotter,        
        "--override-k" if plotter == "chiapos" else "",
        "-k", str(k),
        "-n", "1",
        "-r", str(threads),
        "-u", str(buckets),
        "-t", tmp_dir,
        "-d", dst_dir
    ]
    if compression:
        plot_cmd += ["--compress", str(compression)]

    print("Running command:", " ".join(plot_cmd))
    
    proc = subprocess.Popen(plot_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    stop_event = threading.Event()

    monitor_thread = threading.Thread(
        target=monitor_process,
        args=(proc.pid, log_res_file_path, stop_event),
        daemon=False
    )
    monitor_thread.start()

    with open(log_file_path, "w") as f:
        for line in iter(proc.stdout.readline, b''):
            f.write(line.decode())

    proc.wait()
    stop_event.set()
    monitor_thread.join()
    print("Command finished. Log saved to", log_file)

    if to_json:
        data = parse_chia_log(log_file_path)
        save_to_json(data, log_file_path)