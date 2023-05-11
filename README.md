# THIS PROJECT IS SUPSERSEDED BY [SCALE-SIM-V2](https://github.com/scalesim-project/scale-sim-v2)

# **S**ystolic **C**NN **A**cce**LE**rator Simulator (SCALE Sim)

SCALE sim is a CNN accelerator simulator, that provides cycle-accurate timing,
power/energy, memory bandwidth and trace results for a
specified accelerator configuration and neural network architecture.

[Skip to Getting Started](getting_started.md)

## Motivation

SCALE sim enables research into CNN accelerator architecture and is also suitable for system-level studies. 

Since deep learning based solutions have become prevalent for computer vision
over the recent few years, 
there has been a surge in accelerator design proposals both from academia and the industry. 

It is natural to assume that we will see many more accelerators being proposed as new use cases are identified in the near future.
However, it is important to keep in mind that CNN use cases will likely vary, which poses a large spectrum of efficiency and performance demands on the underlying CNN accelerator design. Therefore, it is important to quickly prototype architectural ideas and iterate over different designs.

In the present, designing a new CNN accelerator usually starts from scratch. 
Performing a simple first order analysis often involves a team of designers writing their own simulators, tackling bugs, and iterating over multiple times.

It is not hard to see that all this effort is mostly repeated work.
This reinvention of the wheel could be avoided if there were a standard tool usable across various use cases and implementation goals.
SCALE Sim is our effort to make a stride in this direction.

## SCALE sim outputs

At the core of SCALE sim is a cycle-accurate architecture simulator for CNN accelerators. We build the accelerator based on the systolic array architecture, similar to the one used in Google's TPU.

Given a convolution neural network topology and certain architecture parameters,
SCALE sim is capable of estimating the following:

* Run time in cycles
* Average utilization
* On-chip memory requirements
* Off-chip interface bandwidth requirements

With the help of external simulators such as CACTI or DRAMPower, users can also use SCALE sim to obtain:

* Power consumption
* Area estimates

## Usecases

Primarily, we envision two major usecases of SCALE sim, which we describe below. It is our hope that by releasing ths simulator, the community will find interesting and ingenious ways of using the tool for other research tasks that expand the original usage scope of SCALE sim.

### Accelerator Design Space Exploration
SCALE sim can help the designer quickly explore accelerator design space. In this mode, SCALE expects the designer to provide a list of limits for architecture features like SRAM size, array size, and interface bandwidth; relevant to the target use case.
These limits help the tool in narrowing down the search space.
SCALE will work if the limits are not specified by assuming the default values, but naturally, the run time will be large.

Usually, designers can translate the use case constraints into high-level architecture constraints. 
For instance, a power-optimized design will not have a large on-chip memory or a big computing array. 
You get the gist. 

### System Simulation
Usually in an ML-enable application, CNN is just one stage of the end-to-end processing pipeline. Therefore, it is important to understand the application characteristics in the context of the entire Systems-on-a-chip (SoC). Existing full-system simulators such as Gem5 and GemDroid lack modles for CNN accelerators (IP), and therefore presents a roadblock in studying system-level behavior of ML-enabled applications.

Due to the modular interface design, users could choose to integrate SCALE sim with Gem5 or GemDroid for full-system simulation. This is particular helpful for researchers who do not wish to perform in-depth investigation of the CNN accelerator microarchitecture, but wish to integrate a decent CNN IP to obtain meaningful system-level characterization results.

## How does it work?

SCALE sim simulates a TPU-like systolic array for CNN computation.
Due to the highly regular data-flow involved in CNNs, it is easy to estimate the storage, traffic, and computation metrics without actually performing the computation. 
SCALE uses this property to generate a cycle accurate traffic trace, into and out of the systolic array to the on-chip SRAM. 

The on-chip SRAM is emulated as a double buffer storage unit, to amortize the high bandwidth requirement on the interface size. 
Using the traffic traces from SRAM to the array and taking into account the double buffered SRAM, traces and metrics for the accelerator to main memory transactions are computed.
Given a CNN topology, the current implementation of SCALE computes the output metrics sequentially for each layer.


## Getting Started

### 30 seconds to SCALE sim!

Getting started is simple! SCALE-Sim is completely written in python. At the moment, it has dependencies on the following python packages. Make sure you have them in your environment.

* os
* subprocess
* math
* configparser
* tqdm
* absl-py

*NOTE: SCALE-Sim needs python3 to run correctly. If you are using python2, you might run into typecasting errors* 

### Custom Experiment
This experiment will run the default MLPERF_AlphaGoZero_32x32_os architechture contained inside scale.cfg. 
It will also run alexnet as its network topology.
* Run the command: ```python scale.py```
* Wait for the run to finish

The config file inside configs contain achitecture presets.  
the csv files inside toologies contain different networks

In order to change a different arichtechture/network, create a new .cfg file inside ```cofigs``` and call a new network by running
```python scale.py -arch_config=configs/eyeriss.cfg -network=topologies/yolo.csv```
Here is sample of the config file.  
![sample config](https://raw.githubusercontent.com/AnandS09/SCALE-Sim/master/images/config_example.png "sample config")    
Architecture presets are the variable parameters for SCALE-Sim, like array size, memory etc.  

The Network Topoplogy csv file contains the network that we want to test in our architechture.  
SCALE-Sim accepts topology csv in the format shown below.  
![yolo_tiny topology](https://raw.githubusercontent.com/AnandS09/SCALE-Sim/master/images/yolo_tiny_csv.png "yolo_tiny.csv")

Since SCALE-Sim is a CNN simulator please do not provide any layers other than convolutional or fully connected in the csv.
You can take a look at 
[yolo_tiny.csv](https://raw.githubusercontent.com/AnandS09/SCALE-Sim/master/topologies/yolo_tiny.csv)
for your reference.

### Output

Here is an example output dumped to stdout when running Yolo tiny (whose configuration is in yolo_tiny.csv):
![screen_out](https://github.com/AnandS09/SCALE-Sim/blob/master/images/output.png "std_out")

Also, the simulator generates read write traces and summary logs at ```./outputs/<topology_name>```.
There are three summary logs:

* Layer wise runtime and average utilization
* Layer wise MAX DRAM bandwidth log
* Layer wise AVG DRAM bandwidth log
* Layer wise breakdown of data movement and compute cycles

In addition cycle accurate SRAM/DRAM access logs are also dumped and could be accesses at ```./outputs/<topology_name>/layer_wise```

### Detailed Documentation

For detailed insights on working of SCALE-Sim, you can refer to this [paper](https://arxiv.org/abs/1811.02883)

## Citing

If you find this tool useful for your research, please use the following bibtex to cite us,

```
@article{samajdar2018scale,
  title={SCALE-Sim: Systolic CNN Accelerator Simulator},
  author={Samajdar, Ananda and Zhu, Yuhao and Whatmough, Paul and Mattina, Matthew and Krishna, Tushar},
  journal={arXiv preprint arXiv:1811.02883},
  year={2018}
}
```

## Contributing

Please send a [pull request](https://help.github.com/articles/creating-a-pull-request/).

## Authors

[Ananda Samajdar](https://anands09.github.io), Georgia Institute of Technology

[Yuhao Zhu](http://yuhaozhu.com), University of Rochester

[Paul Whatmough](https://www.linkedin.com/in/paul-whatmough-2062729/), Arm Research, Boston, MA

## License

This project is licensed under the MIT License - see the LICENSE file for details.

