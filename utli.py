import subprocess
import curses
import time

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
            status = f"{receiver['name']} ✅ Started"
        except subprocess.CalledProcessError as e:
            errors.append(f"Error starting receiver {receiver['name']} at {receiver['ip']}: {str(e)} \n")
            print(f"Exit code: {e.returncode}")
            print(f"Standard output: {e.stdout}")
            print(f"Standard error: {e.stderr}")
            status = f"{receiver['name']} ❌ Error"
    return processes, errors, status

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

def main(stdscr):
    curses.curs_set(1)  # show cursor
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # Split panes
    status_height = height - 3
    status_win = curses.newwin(status_height, width, 0, 0)
    input_win = curses.newwin(3, width, status_height, 0)

    
    
    fileName = 'recording_script.py'
    receivers = load_receivers('ipp.txt')

# Example receiver statuses
    statuses = []
    for receiver in receivers:
        statuses.append((receiver['name'], "OFF"))

    while True:
        # Draw status table
        status_win.clear()
        status_win.addstr(0, 0, "Ground Station Dashboard\n")
        for idx, (name, stat) in enumerate(statuses, start=1):
            status_win.addstr(idx, 0, f"{name}: {stat}")
        status_win.refresh()

        # Update statuses based on processes
        for idx, receiver in enumerate(receivers):
            if statuses[idx][1] == "OFF" and receiver['ip'] in [p.args[0].split('@')[1] for p in processes]:
                statuses[idx] = (receiver['name'], "ON")
            elif statuses[idx][1] == "ON" and receiver['ip'] not in [p.args[0].split('@')[1] for p in processes]:
                statuses[idx] = (receiver['name'], "OFF")

        # Draw input pane
        input_win.clear()
        input_win.addstr(0, 0, "Command > ")
        input_win.refresh()
        
        curses.echo()
        
        

        command = input_win.getstr(1, 0).decode("utf-8").strip()
        commands = command.split()
        curses.noecho()
        processes = []
        errors = []
        try:
            if commands[0] == 'start':
                if commands[1] == 'all':
                    processes, errors, status = start_all(receivers, fileName)
                    for i in range(len(receivers)):
                        statuses[i] = status[i]
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


curses.wrapper(main)