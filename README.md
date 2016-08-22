# MLND Capstone Submission

## Project Overview

This project simulates the growth of a slack community using reinforcement learning.
It is comprised of a simulator and acoompanying graph visualization


## Software and libraries (pip install these) for Simulator:
networkx
py2neo
matplotlib (for plotting)
pandas
scipy
--------
Also os, csv, and random libraries are used.
--------
*** The libraries for the Web App can be viewed in requirements.txt ***

## Running the Simulator

The code for my project is in simulator.py.
You can run the code there using: python simulator.py
Running this shows the network/community visualization as it changes over time.

If you would like to run the experiments that lead to the data you can uncomment

Line 595----> # experiment() 

in simulator.py. You can also specify the number of repetitions, the growth rate,
and the match rate you would like for the model. 

## Project PDF, Data, and Demo

The Project PDF can be viewed in /Figures

A completed graphStats.csv and graphStatsFinal.xls have been uploaded.
Running the model rewrites graphStats.csv. These files contain the results from 
running an "experiment()".

### Demo Percey (work in progress)

You can view the web visualization for the current network at 
percey.herokuapp.com/demo. (click on a user and view their relationships)

--pip install from project root

You can run the Percey web app by entering
python app.py in the command line. Running the App:

Percey is a Slack bot + Web App

Percey works to understand your slack group's communication, create a graph model of it, 
and suggest connections to improve the quality of your network.


Hope 2016 
:) 