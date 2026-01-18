import os
import signal
import sys

# Simple Kill-Switch script
def kill_swarm():
    print("Sending SIGTERM to all python experiment processes...")
    # This is a bit broad, but for a local sandbox it works.
    # In production, we'd use a PID file.
    os.system("pkill -f run_experiment.py")
    print("Swarm processes halted safely.")

if __name__ == "__main__":
    kill_swarm()
