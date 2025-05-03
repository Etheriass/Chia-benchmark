import json
import glob
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

K = 32
PLOTTER = "chiapos" # "bladebit"

def get_metrics_json(json_file):
    phase_1_data = []
    phase_1_tables_order = []

    phase_2_data_scan_times = []
    phase_2_data_scan_cpu = []
    phase_2_data_sort_times = []
    phase_2_data_sort_cpu = []
    phase_2_tables_order = []

    phase_3_data_first_times = []
    phase_3_data_first_cpu = []
    phase_3_data_second_times = []
    phase_3_data_second_cpu = []
    phase_3_data_total_times = []
    phase_3_data_total_cpu = []
    phase_3_tables_order = []

    phases_total_times = []

    with open(json_file, 'r') as f:
        data = json.load(f)


    # Phase 1 - Forward propagation table time
    phase_1_tables = data.get('Phase 1', {})
    for table, metrics in phase_1_tables.items():
        phase_1_tables_order.append(table)
        if 'Forward propagation' in metrics:
            time = float(metrics['Forward propagation']['time'])
            phase_1_data.append(time)

    # Phase 2 - Backpropagation scan and sort times
    phase_2_tables = data.get('Phase 2', {})
    for table, metrics in phase_2_tables.items():
        scan_times = None
        sort_times = None
        phase_2_tables_order.append(table)
        if 'Backpropagation scanned' in metrics:
            scan_times = float(metrics['Backpropagation scanned']['time'])
            phase_2_data_scan_times.append(scan_times)
        if 'Backpropagation sort' in metrics:
            sort_times = float(metrics['Backpropagation sort']['time'])
            phase_2_data_sort_times.append(sort_times)
        

    # Phase 3 - First, second pass, and total compress table times
    phase_3_tables = data.get('Phase 3', {})
    for table, metrics in phase_3_tables.items():
        phase_3_tables_order.append(table)
        if 'First computation pass' in metrics:
            first_times = float(metrics['First computation pass']['time'])
            phase_3_data_first_times.append(first_times)
        if 'Second computation pass' in metrics:
            second_times = float(metrics['Second computation pass']['time'])
            phase_3_data_second_times.append(second_times)
        if 'Total compress table' in metrics:
            total_times = float(metrics['Total compress table']['time'])
            phase_3_data_total_times.append(total_times)

    # Phase 4 - Total compress table times
    phase_4_tables = data.get('Phase 4', {})
    for table, metrics in phase_4_tables.items():
        phase_3_tables_order.append(table)
        if 'First computation pass' in metrics:
            first_times = float(metrics['First computation pass']['time'])
            phase_3_data_first_times.append(first_times)
        if 'Second computation pass' in metrics:
            second_times = float(metrics['Second computation pass']['time'])
            phase_3_data_second_times.append(second_times)
        if 'Total compress table' in metrics:
            total_times = float(metrics['Total compress table']['time'])
            phase_3_data_total_times.append(total_times)

    # Phases total times
    phases_total = data.get('Phases times', {})
    for phase, metrics in phases_total.items():
        time = float(metrics['time'])
        phases_total_times.append(time)

    # Total time
    total_time = float(data.get('Final Stats', {})[0].get('value', 0))

    metrics = {
        'phase_1_data': phase_1_data,
        'phase_2_data_scan_times': phase_2_data_scan_times,
        'phase_2_data_sort_times': phase_2_data_sort_times,
        'phase_3_data_total_times': phase_3_data_total_times,
        'phases_total_times': phases_total_times,
        'total_time': total_time
    }

    return metrics

def file_name_to_label(file_name):
    return file_name.split("log_")[-1].split(".")[0]

def plot_metrics(json_files):
    sns.set_theme(style="whitegrid")  # Set Seaborn style

    phase_1_tables_order = ['1', '2', '3', '4', '5', '6', '7']
    phase_2_tables_order = ['7', '6', '5', '4', '3', '2']
    phase_3_tables_order = ['1-2', '2-3', '3-4', '4-5', '5-6', '6-7']

    all_metrics = []
    for file in json_files:
        metrics = get_metrics_json(file)
        all_metrics.append(metrics)

    # Figure for line plots
    fig1 = plt.figure(figsize=(20, 18))
    gs1 = gridspec.GridSpec(2, 2, hspace=0.4)

    palette = sns.color_palette("hls", len(json_files))  # Use a Seaborn color palette

    # Plot Phase 1: Forward propagation times
    ax0 = fig1.add_subplot(gs1[0, 0])
    for i in range(len(json_files)):
        sns.lineplot(ax=ax0, x=phase_1_tables_order, y=all_metrics[i]['phase_1_data'], label=file_name_to_label(json_files[i]), color=palette[i])
    ax0.set_title('Phase 1: Forward Propagation Time')
    ax0.set_xlabel('Table')
    ax0.set_ylabel('Time (s)')
    ax0.get_legend().remove()
    # ax0.legend()

    # # Plot Phase 2: Backpropagation scan times
    # ax1 = fig1.add_subplot(gs1[0, 1])
    # for i in range(len(json_files)):
    #     sns.lineplot(x=phase_2_tables_order, y=all_metrics[i]['phase_2_data_scan_times'], label=file_name_to_label(json_files[i]), color=palette[i])
    # ax1.set_title('Phase 2: Backpropagation Scan Times')
    # ax1.set_xlabel('Table')
    # ax1.set_ylabel('Time (s)')
    # ax1.get_legend().remove()
    # # ax1.legend()

    # Plot Phase 2: Backpropagation sort times
    ax1 = fig1.add_subplot(gs1[0, 1])
    for i in range(len(json_files)):
        sns.lineplot(x=phase_2_tables_order[1:], y=all_metrics[i]['phase_2_data_sort_times'], label=file_name_to_label(json_files[i]), color=palette[i])
    ax1.set_title('Phase 2: Backpropagation Sort Times')
    ax1.set_xlabel('Table')
    ax1.set_ylabel('Time (s)')
    ax1.get_legend().remove()
    # ax2.legend()

    # Plot Phase 3: First, second pass, and total compress times
    ax2 = fig1.add_subplot(gs1[1, 0])
    for i in range(len(json_files)):
        sns.lineplot(x=phase_3_tables_order, y=all_metrics[i]['phase_3_data_total_times'], label=file_name_to_label(json_files[i]), color=palette[i])
    ax2.set_title('Phase 3: Compress Table Times')
    ax2.set_xticks(phase_3_tables_order)
    ax2.set_xlabel('Table Pair')
    ax2.set_ylabel('Time (s)')
    ax2.get_legend().remove()


    # Plot Phase 4: Write Checkpoint tables
    ax3 = fig1.add_subplot(gs1[1, 1])
    time_phase_4 = []
    for i in range(len(json_files)):
        time_phase_4.append(all_metrics[i]['phases_total_times'][3])
    for i in range(len(json_files)):
        ax3.bar(0 + i*0.1 , time_phase_4[i], label=file_name_to_label(json_files[i]), color=palette[i], width=0.1)
    ax3.set_title('Phase 4: Write Checkpoint Tables')
    ax3.set_xticks([]) # No x-ticks

    fig1.suptitle('Plotting Times by table - K'+str(K), fontsize=16)

    # Create a single legend for the entire figure
    handles, labels = ax0.get_legend_handles_labels()
    fig1.legend(handles, labels)


    # Figure for histograms
    fig2, axes2 = plt.subplots(2, 1, figsize=(20,18))
    fig2.subplots_adjust(hspace=0.4)  # Adjusted wspace

    # Total time for each phase histoplot
    phases_range = np.arange(1, 5)
    bar_width = 0.1
    for i in range(len(json_files)):
        axes2[0].bar(phases_range + i * bar_width, all_metrics[i]['phases_total_times'], width=bar_width, label=f'{json_files[i].split("log_")[-1].split(".")[0]}', color=palette[i])
    axes2[0].set_xticks(phases_range + bar_width * (len(json_files) - 1) / 2)
    axes2[0].set_xticklabels([f'Phase {i}' for i in range(1, 5)])
    axes2[0].set_title('Total Time for Each Phase')
    axes2[0].set_xlabel('Phase')
    axes2[0].set_ylabel('Time (s)')
    axes2[0].legend()

    # Total time
    bar_width = 0.4
    total_time_labels = [f'{json_files[i].split("log_")[-1].split(".")[0]}' for i in range(len(json_files))]
    total_times = [all_metrics[i]['total_time'] for i in range(len(json_files))]

    sns.barplot(ax=axes2[1], x=total_time_labels, y=total_times, hue=total_time_labels, palette=palette, dodge=False, legend=False)
    axes2[1].set_title('Total Time for Plotting')
    axes2[1].set_xlabel('Log File')
    axes2[1].set_ylabel('Time (s)')

    fig2.suptitle('Plotting Times - K'+str(K), fontsize=16)

    # plt.show()

    # Get res files
    csv_files = []
    for i in range(len(json_files)):
        csv_file = json_files[i].replace('.json', '_res.csv')
        csv_file = csv_file.replace('json', 'res')
        if glob.glob(csv_file):
            csv_files.append(csv_file)

    print(f"Found {len(csv_files)} CSV files.")

    # Figure for disk and system usage
    # csv cols: timestamp,device,rkB/s,wkB/s,util,cpu_percent,ram_used_mb,ram_percent
    # each file as a file json_file.replace('.json', '_res.csv')
    fig3, axes3 = plt.subplots(2, 2, figsize=(20, 24))
    fig3.subplots_adjust(hspace=0.4, wspace=0.2)  # Adjusted wspace
    for i, csv_file in enumerate(csv_files):
        df = pd.read_csv(csv_file, sep=',', header=0)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%H:%M:%S')
        df['timestamp'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()
        df = smoothen_df(df, window_size=100)

        # Plot write_MBps
        sns.lineplot(ax=axes3[0, 0], x=df['timestamp'], y=df['write_MBps'], label=file_name_to_label(csv_file), color=palette[i])
        axes3[0, 0].set_title('Disk Write Speed (MB/s)')
        axes3[0, 0].set_xlabel('Time (s)')
        axes3[0, 0].set_ylabel('Write (MB/s)')
        axes3[0, 0].get_legend().remove()

        # Plot read IOPS
        sns.lineplot(ax=axes3[0, 1], x=df['timestamp'], y=df['read_IOPS'], label=file_name_to_label(csv_file), color=palette[i])
        axes3[0, 1].set_title('Disk Read IOPS')
        axes3[0, 1].set_xlabel('Time (s)')
        axes3[0, 1].set_ylabel('Count')
        axes3[0, 1].get_legend().remove()

        # Plot CPU usage
        sns.lineplot(ax=axes3[1, 0], x=df['timestamp'], y=df['cpu_percent'], label=file_name_to_label(csv_file), color=palette[i])
        axes3[1, 0].set_title('CPU Usage (%)')
        axes3[1, 0].set_xlabel('Time (s)')
        axes3[1, 0].set_ylabel('CPU Usage (%)')
        axes3[1, 0].get_legend().remove()

        # Plot RAM usage in MB
        sns.lineplot(ax=axes3[1, 1], x=df['timestamp'], y=df['ram_used_mb'], label=file_name_to_label(csv_file), color=palette[i])
        axes3[1, 1].set_title('RAM Usage (MB)')
        axes3[1, 1].set_xlabel('Time (s)')
        axes3[1, 1].set_ylabel('RAM Used (MB)')
        axes3[1, 1].get_legend().remove()

        # # Plot RAM usage percentage
        # sns.lineplot(ax=axes3[1, 1], x=df['timestamp'], y=df['ram_percent'], label=file_name_to_label(csv_file), color=palette[i])
        # axes3[1, 1].set_title('RAM Usage (%)')
        # axes3[1, 1].set_xlabel('Time (s)')
        # axes3[1, 1].set_ylabel('RAM Usage (%)')
        # axes3[1, 1].get_legend().remove()

        

        # # Plot write IOPS
        # sns.lineplot(ax=axes3[2, 1], x=df['timestamp'], y=df['write_IOPS'], label=file_name_to_label(csv_file), color=palette[i])
        # axes3[2, 1].set_title('Disk Write IOPS')
        # axes3[2, 1].set_xlabel('Time (s)')
        # axes3[2, 1].set_ylabel('Count')
        # axes3[2, 1].get_legend().remove()


    fig3.suptitle('Resource utilization - K'+str(K), fontsize=16)

    # Create a single legend for the entire figure
    handles, labels = axes3[0, 0].get_legend_handles_labels()
    fig3.legend(handles, labels)
    
    plt.show()

def smoothen_df(df, window_size=5):
    # Apply a rolling mean to smoothen the data
    smoothed_df = df.rolling(window=window_size, min_periods=1).mean()
    return smoothed_df

def select_files(json_files):
    PATTERN = 'c0.' #'128b'
    selected_files = []
    for file in json_files:
        if PATTERN in file:
            selected_files.append(file)
    return selected_files

def key_function(path):
    filename = path.split('/')[-1]
    parts = filename.split('_')[2:]

    key = []
    for part in parts:
        # Extract numeric part and suffix (e.g., '2t' -> ('2', 't'), '128b' -> ('128', 'b'))
        num = ''
        suffix = ''
        for char in part:
            if char.isdigit():
                num += char
            else:
                suffix += char
        # Convert numeric part to int for numerical sorting, keep suffix as string
        key.append((int(num) if num else 0, suffix))
    return key

if __name__ == "__main__":
    json_files = glob.glob('./logs/k'+ str(K) +'/'+ PLOTTER+'/json/*.json')
    selected_files = select_files(json_files)
    selected_files = sorted(selected_files, key=key_function)
    print(f"Found {len(selected_files)} JSON files.")
    plot_metrics(selected_files)
