## ReadMe

The three code serve different purposes.

- `Server_vrpn.py` monitors and controls the procedure of the experiment.
- `Environments.py` creates elements of the virtual environments.
- `Experiment_VR.py` creates and presents the virtual stimuli. It runs on the computer that connects to the HMD.

Each participant had a folder to store the data. The folder name contains information about the condition or condition sequence that the participant went through during the experiment. `Environments.py` and `experiment_VR.py` should be placed in each participant folder.

## About the study

The study investigates whether a mental representation could be developed during walking and its effects on the guidance of walking. It was a walking experiment that tried to replicate the findings of Andersen and Enriquez (2006) on a steering task. 

Participants walked through a forest-like environment. The layout of the "forest" was either randomly changed from trial to trial, or remained the same across trials. There were two conditions of remaining the same: (1) remaining the same relative to the world (so participants walked back and forth through the "forest"), and (2) remaining the same relative to the participants themselves (so participants walked in the same direction in the "forest" regardless of their real walking direction).



Andersen, G. J., & Enriquez, A. (2006). Use of landmarks and allocentric reference frames for the control of locomotion. *Visual Cognition, 13(1)*, 119–128. https://doi.org/10.1080/13506280500405675