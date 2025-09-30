import subprocess


def load_receivers(file_path):
    receivers = []
    with open(file_path, 'r') as file:
        for line in file:
            try:
                name, ip = line.strip().split(',')
                receivers.append({'name': name, 'ip': ip})
            except ValueError:
                print(f"Skipping invalid line: {line.strip()}")
    return receivers


def start_all(receivers, fileName):
    """Starts the gnu radio recording for every ground receiver"""
    processes = []
    errors = []
    for receiver in receivers:
        cmd = "ssh " + "receiver@" + receiver['ip'] + " tmux new-window \"python3" + fileName + "\""
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            processes.append(process)
        except subprocess.CalledProcessError as e:
            errors.append(f"Error starting receiver {receiver['name']} at {receiver['ip']}: {str(e)} \n")
            print(f"Exit code: {e.returncode}")
            print(f"Standard output: {e.stdout}")
            print(f"Standard error: {e.stderr}")
    return processes, errors

def start_one(receiver, fileName):
    """Starts the gnu radio recording for every ground receiver"""
    processes = []
    errors = []
    
    cmd = "ssh " + "receiver@" + receiver['ip'] + " tmux new-window \"python3" + fileName + "\""
    try:
        process = subprocess.Popen(cmd, shell=True)
        processes.append(process)
    except Exception as e:
        errors.append(f"Error starting receiver {receiver['name']} at {receiver['ip']}: {str(e)} \n")
    return processes, errors

def stop_all(receivers, fileName):
    """Stops the gnu radio recording for every ground receiver"""
    processes = []
    errors = []
    for receiver in receivers:
        cmd = "ssh " + "receiver@" + receiver['ip'] + " tmux kill-window -t " + fileName
        try:
            process = subprocess.Popen(cmd, shell=True)
            processes.append(process)
        except Exception as e:
            errors.append(f"Error stopping receiver {receiver['name']} at {receiver['ip']}: {str(e)} \n")
    return processes, errors

def stop_one(receiver, fileName):
    """Stops the gnu radio recording for every ground receiver"""
    processes = []
    errors = []
    cmd = "ssh " + "receiver@" + receiver['ip'] + " tmux kill-window -t " + fileName
    try:
        process = subprocess.Popen(cmd, shell=True)
        processes.append(process)
    except Exception as e:
        errors.append(f"Error stopping receiver {receiver['name']} at {receiver['ip']}: {str(e)} \n")
    return processes, errors

def main():
    fileName = 'recording_script.py'
    receivers = load_receivers('ipp.txt')
    while True:
        command = input("Enter 'start' to start recording, 'stop' to stop recording, or 'exit' to quit: ")
        commands = command.split()
        processes = []
        errors = []
        try:
            if commands[0] == 'start':
                if commands[1] == 'all':
                    processes, errors = start_all(receivers, fileName)
                else:
                    receiver_name = commands[1]
                    receiver = next((s for s in receivers if s['name'] == receiver_name), None)
                    if receiver:
                        processes, errors = start_one(receiver, fileName)
                    else:
                        print(f"No receiver found with name {receiver_name}")
            
            elif commands[0] == 'stop':
                if commands[1] == 'all':
                    processes, errors = stop_all(receivers, fileName)
                else:
                    receiver_name = commands[1]
                    receiver = next((s for s in receivers if s['name'] == receiver_name), None)
                    if receiver:
                        processes, errors = stop_one(receiver, fileName)
                    else:
                        print(f"No receiver found with name {receiver_name}")
            
            elif commands[0] == 'exit':
                break
            
        except IndexError:
            print("Invalid arguments. Type \"help\" for a list of commands.")

        print("Errors:\n", errors);
        print("Processes:\n", processes);

if __name__ == "__main__":
    main()