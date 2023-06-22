# OpenSCENARIO2SUMO
Automatic traffic scenario conversion interface between OpenSCENARIO and the traffic simulator SUMO. Currently, only the conversion from **O**pen**SC**ENARIO to **C**ommon**R**OAD (osc2cr) is developed.<br>

### Reference
This repo refers to https://gitlab.lrz.de/tum-cps/commonroad-openscenario-converter.git

### Requirements
The code is written in Python 3.10 and has been tested on Ubuntu 22.04. 

### Using the Converter
The recommended way of installation if you only want to use the OpenSCENARIO-CommonROAD Converter
(i.e., you do not want to work with the code directly) is to use the PyPI package:
```bash
pip install commonroad-openscenario-converter
```
### Development
For developing purposes, we recommend using [Anaconda](https://www.anaconda.com/) to manage your environment so that
even if you mess something up, you can always have a safe and clean restart. 
A guide for managing Python environments with Anaconda can be found [here](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

- First, clone the repository. 
- After installing Anaconda, create a new environment with (>=3.9) and enter it:
``` bash
$ conda create -n commonroad-py39 python=3.9 -y
$ conda activate commonroad-py39
or
$ source activate commonroad-py39
```
- Then, install the dependencies with:

```sh
$ cd <path-to-this-repo>
$ pip install .
$ conda develop .
```

- Test case:
```bash
$ cd test
$ python OSC_Convert2_CR.py
```
The generated simple curve scenario "OpenSCENRAIO2SUMO/output/SimpleCurve/OSC_SimpleCurve_1_T-1.xml" could be opened via the CommonRoad Scenario Designer.

### Open Simulation Interface (OSI) and UDP Driver
If you want to use the [esmini](https://github.com/esmini/esmini) UDPDriverController in combination with OSI for including
external driver models or vehicle simulators, you need to install OSI manually, 
see [here](https://github.com/OpenSimulationInterface/open-simulation-interface).


### Citation
[paper](https://arxiv.org/pdf/2305.10080.pdf):
```text
@article{osc2cr,
  title={Automatic Traffic Scenario Conversion from OpenSCENARIO to CommonRoad},
  author={Yuanfei Lin, Michael Ratzel, and Matthias Althoff},
  archivePrefix={arXiv},
  journal={arXiv preprint arXiv:2305.10080},
  year={2023}}
}
```
