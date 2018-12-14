# Fall Jungle Project

The primary purpose of the Fall Jungle Project is to explore ways in which we can predict the pathing of junglers given certain conditions. One scenario that is being explored in this project is, given the jungler's position at two minutes, how accurately we can determine the jungler's position at three minutes.

## Getting Started

* **comparePaths.py** - Running this script creates a pickle object called compData.pkl. This object contains five columns: matchId, participantId, pos (list of xy positions at each timestamp), distance (list of distances from xy position on the current path to that of the reference path), difference (average distance).
* **predictPaths.py** - Has a function nextPosition() that plots a graph of the position points one minute from the given time for all paths similar (based on a threshold) to the reference point at the given time
* **srPlot.py** - Contains various functions that all pertain to plotting points and jungle paths onto an image of Summoner's Rift

## Authors

* **Stephen Downhower** - *Main Contributor for the Fall Jungle Project*
* **Alex Cloud** - *Supervisor for the Fall Jungle Project*
