## ReadMe

The three code serve different purposes.

- `Server_vrpn.py` monitors and controls the procedure of the experiment.
- `Environments.py` creates elements of the virtual environments.
- `Experiment_VR.py` creates and presents the virtual stimuli. It runs on the computer that connects to the HMD.

Each participant had a folder to store the data. The folder name contains information about the condition or condition sequence that the participant went through during the experiment. `Environments.py` and `experiment_VR.py` should be placed in each participant folder.

## About the study

The study contains two experiments. Experiment 1 investigates the use of symmetry cues in the guidance of walking. Participants walked in the same virtual room but in three different directions: to the centre of frontal wall, to the corner and to a point between the two.

Experiment 2 investigates the role of target drift by manipulating the distance of the target from the starting point. 

Each participant finished the two experiments in a row. The order was counterbalanced and randomised.