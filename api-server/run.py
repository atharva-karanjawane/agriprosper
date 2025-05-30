#!/usr/bin/env python3
import subprocess
import sys
import os
import signal
import time

def run_processes():
    # Define the commands to run
    app_cmd = ["python", "../app/app.py"]
    api_cmd = ["python", "server.py"]
    
    processes = []
    
    try:
        # Start the app process
        print("Starting app process...")
        app_process = subprocess.Popen(app_cmd)
        processes.append(app_process)
        
        # Short delay to let the first process initialize
        time.sleep(1)
        
        # Start the API server process
        print("Starting API server process...")
        api_process = subprocess.Popen(api_cmd)
        processes.append(api_process)
        
        print("Both processes are running. Press Ctrl+C to stop.")
        
        # Wait for processes to finish (unlikely in this case)
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\nShutting down processes...")
        
    finally:
        # Ensure all processes are terminated
        for process in processes:
            if process.poll() is None:  # If process is still running
                try:
                    # Send SIGTERM to allow graceful shutdown
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if process doesn't terminate in time
                    print("Process did not terminate gracefully, forcing...")
                    process.kill()
        
        print("All processes stopped.")

if __name__ == "__main__":
    run_processes()