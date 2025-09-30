## Inputs and Outputs
The user will provide terminal based command inputs. The program will output ssh commands to the ground station receivers. 

## Sending Commands
The utility shall use subproccess, a python library, to send ssh commands to each of the ground stations. A function will be called to send out the commands. 
Pseudo Code:
````md
