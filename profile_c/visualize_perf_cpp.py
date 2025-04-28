# visualize_perf_cpp.py
import subprocess
import os

FLAMEGRAPH_DIR = os.path.expanduser("~/softwares/FlameGraph")
STACK_FILE = "perf.stacks"
SVG_OUT = "perf_flamegraph.svg"

subprocess.run([
    os.path.join(FLAMEGRAPH_DIR, "stackcollapse-perf.pl"),
    STACK_FILE
], stdout=open("perf.folded", "w"))

subprocess.run([
    os.path.join(FLAMEGRAPH_DIR, "flamegraph.pl"),
    "perf.folded"
], stdout=open(SVG_OUT, "w"))

print(f"Flamegraph generated: {SVG_OUT}")
