from benchmark_chia_plot import run_plotter

PLOTTER = "chiapos" #"~/chia-project/chiapos"
K = 28
BUCKETS = [32,64,128] # Chiapos maximum is 128
THREADS = [4,8,16]
COMPRESSIONS = [0] #[1, 3, 5, 7]

def main():
    for buckets in BUCKETS:
        for threads in THREADS:
            for compression in COMPRESSIONS:
                run_plotter(K, threads, buckets, PLOTTER, to_json=False, compression=compression)

if __name__ == "__main__":
    main()


# ./bladebit -t 8 -f b00d9e16c1c97e8d60172b4dd148d0e9a9d62f4aab7e048c1660f6af6db98f56e184903bc9a772e9b32cd497bb27df66 -p b7082e30b4d797a7e1103742164c3cac70ccf2c114071ac1a4fdeea5446796aa2d1f78f1839947febe6f85aead474bd7 diskplot -t1 ../../plot/tmp/ ../../plot/final/
