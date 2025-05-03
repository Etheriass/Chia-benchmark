from benchmark_chia_plot import run_plotter

PLOTTER = "chiapos"
K = 28
BUCKETS = [32,64,128] # Chiapos maximum is 128
THREADS = [4,8,16]
COMPRESSIONS = [0]

def main():
    for buckets in BUCKETS:
        for threads in THREADS:
            for compression in COMPRESSIONS:
                run_plotter(K, threads, buckets, PLOTTER, to_json=False, compression=compression)

if __name__ == "__main__":
    main()
