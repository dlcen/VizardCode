## ReadMe

The three code serve different purposes.

- `Server_vrpn.py` monitors and controls the procedure of the experiment.
- `Environments.py` creates elements of the virtual environments.
- `experiment_VR.py` creates and presents the virtual stimuli. It runs on the computer that connects to the HMD.

Each participant had a folder to store the data. The folder name contains information about the condition or condition sequence that the participant went through during the experiment. `Environments.py` and `experiment_VR.py` should be placed in each participant folder.