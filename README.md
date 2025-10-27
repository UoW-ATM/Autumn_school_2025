# Transportation Research Laboratory - Autumn School 2025
UoW Transportation Research Laboratory (TRL) Autumn School - https://blog.westminster.ac.uk/trl/


This repository contains the material and examples of data usage presented as part of the Autumn School of the Transportation Research Laboratory 2025.

## TRL Autumn School

<details>
<summary>Agenda and material</summary>
  
- Monday – 27 October – Lectures :
    - [Welcome](autumn_school_slides/1_Welcome.pdf) 
    - [Introduction to air traffic management and mobility modelling](autumn_school_slides/2_Introduction_ATM.pdf)
    - Use of anonymised Mobile Network Data for transport modelling
    - [Modelling and simulating the system](autumn_school_slides/4_Mercury_Introduction.pdf) ([Mercury](https://github.com/UoW-ATM/Mercury) Agent-Based Model)
    - Techniques for data analysis and modelling
        - [Process mining for air transport and simulation analysis](autumn_school_slides/5_Process_Mining_in_Aviation.pdf)
        - [Regression models for flight operations](autumn_school_slides/6_Models_for_flight_operations.pdf)
        - [Clustering and trajectory analysis](autumn_school_slides/7_Aircraft_trajectory_usage.pdf)
        
- Tuesday – 28 October – Hands-on data:
    - Data sources for air transport and beyond (see [Data and tools exploration](#data-and-tools-exploration))
    - Example of research and models using open data sources
    - Definition of problems/topics to tackle during the rest of the week
    
- Wednesday – Thursday – 29-30 October – working on problems/topics.

- Friday – 31 October (hybrid (in person strongly recommended)):
    - Presentation of results/models developed by groups
 
</details>

## Content

### Data and tools exploration
Different notebooks are provided to explore some open aviation datasets and libraries:

- EUROCONTROL R&D Archive (Aviation Data Research): https://www.eurocontrol.int/dashboard/aviation-data-research
  - [ECTL_RD/ECTL_RD_Archive.ipynb](ECTL_RD/ECTL_RD_Archive.ipynb): Exploration of datasets
  - [ECTL_RD/ECTL_RD_Archive_exercise.ipynb](ECTL_RD/ECTL_RD_Archive_exercise.ipynb): Exercise on R&D Archive data
- Open Performance Data Initiative (OPDI): https://www.opdi.aero/
  - [OPDI/OPDI.ipynb](OPDI/OPDI.ipynb): Exploration of datasets
- OpenSky Network: https://opensky-network.org/
  - [opensky/opensky_exercise.ipynb](opensky/opensky_exercise.ipynb): Exercise using OpenSky ADS-B data
- Environmental impact:
  - [Climate/Climate.ipynb](Climate/Climate.ipynb): Computation of climate hotspots, emissions and total environmental impact of flights, using:
    - [OpenAP](https://github.com/TUDelft-CNS-ATM/openap) library for emissions estimation (installed as a requirement)
    - [climaccf](https://github.com/dlr-pa/climaccf/) library for climate hotspot estimation (as submodule)


### Installation
Notebooks work with Python3.12, requirements in requirements.txt. We recommend creating a virtual environment.

As the repository includes a submodule (climaccf), you could clone the repo and the submodules with:
`git clone --recurse-submodules https://github.com/UoW-ATM/Autumn_school_2025.git`

If you already have the repository but not the submodules, remember to initialise them: 
`git submodule update --init --recursive`

