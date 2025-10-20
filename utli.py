import subprocess
import time
import threading
from tqdm import tqdm


def show_loading(message, process, position):
    """Display a loading bar for one subprocess until it completes."""
    with tqdm(
        total=100,
        desc=message,
        position=position,
        leave=True,
        bar_format="{l_bar}{bar}| {elapsed}",
    ) as pbar:
        while process.poll() is None:
            time.sleep(0.1)
            pbar.update(2)
            if pbar.n >= 100:
                pbar.n = 0
        pbar.n = 100
        pbar.refresh()


def load_receivers(file_path):
    receivers = []
    with open(file_path, "r") as file:
        for line in file:
            try:
                name, ip = line.strip().split(",")
                receivers.append({"name": name, "ip": ip})
                print(f"Loaded receiver: {name} with IP: {ip}")
            except ValueError:
                print(f"Skipping invalid line: {line.strip()}")
    return receivers


def run_with_loading(cmd, desc, position):
    """Run a subprocess with a progress bar in a thread."""
    try:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        thread = threading.Thread(target=show_loading, args=(desc, process, position))
        thread.start()
        return process, thread, None
    except Exception as e:
        return None, None, f"{desc} error: {str(e)}"


def run_parallel(receivers, cmd_template, action_name, fileName=None, filepath=None):
    """Run commands on all receivers in parallel with progress bars."""
    processes = []
    threads = []
    errors = []

    for i, receiver in enumerate(receivers):
        # build the command string based on action
        if "{fileName}" in cmd_template:
            cmd = cmd_template.format(ip=receiver["ip"], fileName=fileName)
        elif "{filepath}" in cmd_template:
            cmd = cmd_template.format(ip=receiver["ip"], filepath=filepath)
        else:
            cmd = cmd_template.format(ip=receiver["ip"])

        desc = f"{action_name} {receiver['name']}"
        process, thread, err = run_with_loading(cmd, desc, i)
        if process:
            processes.append(process)
        if thread:
            threads.append(thread)
        if err:
            errors.append(err)

    # Wait for all processes and threads to finish
    for t in threads:
        t.join()
    for p in processes:
        p.wait()
   


  
    # Collect stderr if any
    for receiver, process in zip(receivers, processes):
        if process.returncode != 0:
            stderr = process.stderr.read().strip()
            if stderr:
                errors.append(f"{receiver['name']} failed: {stderr}")

    return processes, errors


# === Command Functions ===
def start_all(receivers, fileName):
    cmd_template = "sshpass -p nicerocket ssh receiver@{ip} 'tmux new-session -d \"python3 {fileName}\"'"
    return run_parallel(receivers, cmd_template, "Starting", fileName=fileName)


def stop_all(receivers, fileName):
    cmd_template = "sshpass -p nicerocket ssh receiver@{ip} 'tmux kill-server'"
    return run_parallel(receivers, cmd_template, "Stopping")


def download_all(receivers, filepath):
    cmd_template = "sshpass -p nicerocket scp -r receiver@{ip}:~/data/ {filepath}"
    return run_parallel(receivers, cmd_template, "Downloading", filepath=filepath)

def upload_all(receivers, filepath):
    cmd_template = "sshpass -p nicerocket scp -r {filepath} receiver@{ip}:~/"
    return run_parallel(receivers, cmd_template, "Uploading", filepath=filepath)


# === Single Receiver Versions ===
def start_one(receiver, fileName):
    cmd = f"sshpass -p nicerocket ssh receiver@{receiver['ip']} 'tmux new-session -d \"python3 {fileName}\"'"
    return run_parallel([receiver], cmd, "Starting", fileName=fileName)


def stop_one(receiver, fileName):
    cmd = f"sshpass -p nicerocket ssh receiver@{receiver['ip']} 'tmux kill-server'"
    return run_parallel([receiver], cmd, "Stopping")


def download_one(receiver, filepath):
    cmd = f"sshpass -p nicerocket scp -r receiver@{receiver['ip']}:~/data/ {filepath}"
    return run_parallel([receiver], cmd, "Downloading", filepath=filepath)

def upload_one(receiver, filepath):
    cmd = f"sshpass -p nicerocket scp -r {filepath} receiver@{receiver['ip']}:~/"
    return run_parallel([receiver], cmd, "Uploading", filepath=filepath)


# === Main CLI ===
def main():
    fileName = "simple_test.py"
    receivers = load_receivers("ipp.txt")

    while True:
        command = input("\nEnter command (start/stop/download/upload/exit): ")
        commands = command.split()
        processes, errors = [], []

        try:
            if commands[0] == "start":
                if commands[1] == "all":
                    processes, errors = start_all(receivers, fileName)
                else:
                    name = commands[1]
                    receiver = next((r for r in receivers if r["name"] == name), None)
                    if receiver:
                        processes, errors = start_one(receiver, fileName)
                    else:
                        print(f"No receiver found with name {name}")

            elif commands[0] == "stop":
                if commands[1] == "all":
                    processes, errors = stop_all(receivers, fileName)
                else:
                    name = commands[1]
                    receiver = next((r for r in receivers if r["name"] == name), None)
                    if receiver:
                        processes, errors = stop_one(receiver, fileName)
                    else:
                        print(f"No receiver found with name {name}")

            elif commands[0] == "download":
                if len(commands) < 3:
                    print("Usage: download [receiver|all] [local_path]")
                    continue
                filepath = commands[2]
                if commands[1] == "all":
                    processes, errors = download_all(receivers, filepath)
                else:
                    name = commands[1]
                    receiver = next((r for r in receivers if r["name"] == name), None)
                    if receiver:
                        processes, errors = download_one(receiver, filepath)
                    else:
                        print(f"No receiver found with name {name}")

            elif commands[0] == "upload":
                if len(commands) < 3:
                    print("Usage: upload [receiver|all] [local_path]")
                    continue
                filepath = commands[2]
                if commands[1] == "all":
                    processes, errors = upload_all(receivers, filepath)
                else:
                    name = commands[1]
                    receiver = next((r for r in receivers if r["name"] == name), None)
                    if receiver:
                        processes, errors = upload_one(receiver, filepath)
                    else:
                        print(f"No receiver found with name {name}")

            elif commands[0] == "exit":
                print("Exiting...")
                break

        except IndexError:
            print("Invalid arguments. Example: start all | stop receiver1 | download all /path/to/folder")

        if errors:
            print("\nErrors:")
            for e in errors:
                print(" -", e)
        else:
            print("\n✅ All commands executed successfully")

if __name__ == "__main__":
    main()
