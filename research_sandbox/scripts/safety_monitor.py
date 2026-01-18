import os
import signal
import time
import json

def safety_watcher(metrics_path, stop_event):
    """
    Background thread to monitor swarm metrics and kill the process if
    anomaly is detected (entropy collapse).
    """
    print("Safety Monitor: ACTIVE")
    while not stop_event.is_set():
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r') as f:
                    data = json.load(f)
                    
                if not data:
                    continue
                    
                recent = data[-1]
                entropy = recent.get('entropy', 1.0)
                
                # Entropy Collapse Detection
                if entropy < 0.05:
                    print(f"!!! SAFETY ALERT: Entropy Collapse ({entropy:.4f}) !!!")
                    print("Initiating Emergency Stop...")
                    # In a real system, we'd kill the specific experimentation process
                    os.kill(os.getpid(), signal.SIGTERM)
                    break
            except Exception as e:
                pass # Silent fail to prevent monitor itself from crashing
        time.sleep(1)
