import json
import matplotlib.pyplot as plt
import sys
import glob
import os

def plot_latest():
    # Find the most recent result file
    files = glob.glob("d:/ci lang/research_sandbox/results/run_*.json")
    if not files:
        print("No results found.")
        return
    
    latest_file = max(files, key=os.path.getctime)
    print(f"Plotting results from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    history = data['history']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Entropy Plot
    ax1.plot(history['tick'], history['entropy'], label='Observed Entropy (KSG)', color='cyan')
    ax1.axhline(y=data['config']['target_e'], color='r', linestyle='--', label='Target Entropy')
    ax1.set_ylabel("Shannon Entropy (bits)")
    ax1.set_title(f"CI Sandbox: {data['config']['name']}")
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Volatility Plot
    ax2.plot(history['tick'], history['volatility'], label='System Volatility', color='orange')
    ax2.set_ylabel("Volatility (sigma)")
    ax2.set_xlabel("Ticks")
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    output_img = latest_file.replace('.json', '.png')
    plt.savefig(output_img)
    plt.show()
    print(f"Plot saved to {output_img}")

if __name__ == "__main__":
    plot_latest()
