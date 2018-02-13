# **S**ystolic **C**NN **A**cce**LE**rator Simulator (SCALE Sim)#

SCALE sim is a CNN accelerator simulator, that provides cycle-accurate timing,
power/energy, memory bandwidth and trace results for a
specified accelerator configuration and neural network architecture.

[Skip to Getting Started](#Getting-Started)

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
[//]:#(Right now SCALE models a variable size systolic array, which computes convolution layers employing output stationary dataflow.)
[//]:#(For the uninitiated, output stationary dataflow simply means that every MAC unit is responsible for generating on output feature map (OFMAP) pixel.)
[//]:#(To do this, the design should ensure that all the required input feature map(IFMAP) pixels and corresponding filters are delivered to the respective PE in a proper sequence.)
[//]:#(The reduction happens within the PE.)

SCALE sim simulates a TPU-like systolic array for CNN computation.
Due to the highly regular data-flow involved in CNNs, it is easy to estimate the storage, traffic, and computation metrics without actually performing the computation. 
SCALE uses this property to generate a cycle accurate traffic trace, into and out of the systolic array to the on-chip SRAM. 

The on-chip SRAM is emulated as a double buffer storage unit, to amortize the high bandwidth requirement on the interface size. 
Using the traffic traces from SRAM to the array and taking into account the double buffered SRAM, traces and metrics for the accelerator to main memory transactions are computed.
Given a CNN topology, the current implementation of SCALE computes the output metrics sequentially for each layer.


## Getting Started

### 30 seconds to SCALE sim!

Getting started is simple! SCALE-Sim is completely written in python. At the moment, it has dependencies on the following python packages. Make sure you have them in your environment.
[//]:#(Once you have successfully cloned the repository, update the config file and run the command.)

* os
* subprocess
* math
* configparser
* tqdm


### Custom Experiment

* Fill in the config file, scale.cfg with proper values. 
* Run the command: ```python scale.py```
* Wait for the run to finish

The config file scale.cfg contains two sections, achitecture presets and network presets.  
Here is sample of the config file.  
![sample config](https://bytebucket.org/AnandS09/scale_sim/raw/cf9714d08e4d6b649939e9d2f3fb015c87cbc8e3/images/config_example_single.png?token=1ca95715abe2048d67ec584d63e2077a0fc4b170 "sample config")    
Architecture presets are the variable parameters for SCALE-Sim, like array size, memory etc.  


[//]:#(The presets expect a range of values in comma separated fashion.)  
[//]:#(```python)
[//]:#(<var_name>: min_val, max_val)
[//]:#(```)
[//]:#(![sample preset](https://bytebucket.org/AnandS09/scale_sim/raw/1e7e57c7580548589b8a4118a15eba144e6b66e6/images/preset_example.png?token=eaec97261085908f49fee6414a6a4bfa02e63164 "sample preset")  )
[//]:#(In this case SCALE-Sim will iterate from an array height of 2 to 64 in the course of runs.)
[//]:#(In cases where we do not want to iterate over a range of value, just provide a single numeric value for the parameter. ) 
[//]:#(![sample const preset](https://bytebucket.org/AnandS09/scale_sim/raw/ebeec1abb019cca66f0a52bef8ceb3ef1e614f96/images/const_preset.png?token=8fd0c89b258e5f11b614d3c48cc4a454d17a618d "const preset")  )
[//]:#(In this case SCALE-Sim will run with an array size of 32x32 and not iterate.)

Network preset contains just one field for now, that is the path to the topology csv file.  
SCALE-Sim accepts topology csv in the format shown below.  
![yolo_tiny topology](https://bytebucket.org/AnandS09/scale_sim/raw/cf9714d08e4d6b649939e9d2f3fb015c87cbc8e3/images/yolo_tiny_csv.png?token=958799e78eb7efae60df52ea1f8a8dfea7809b0a "yolo_tiny.csv")

Since SCALE-Sim is a CNN simulator please do not provide any layers other than convolutional or fully connected in the csv.
You can take a look at 
[yolo_tiny.csv](https://bitbucket.org/AnandS09/scale_sim/raw/cf9714d08e4d6b649939e9d2f3fb015c87cbc8e3/yolo_tiny.csv)
for your reference.

### Output

Here is an example output dumped to stdout when running Yolo tiny (whose configuration is in yolo_tiny.csv):
![screen_out](https://bytebucket.org/AnandS09/scale_sim/raw/4cab2d46fee5b3bf1965ceed56873008f9dfe2aa/images/output.png?token=67ebcc18c0620f0e54eceacd60179a984d0f32cc "std_out")

Also, the simulator generates read write traces and summary logs at ```./outputs/<topology_name>```.
There are three summary logs:

* Layer wise runtime information.
* Layer wise MAX DRAM bandwidth log.
* Layer wise AVG DRAM bandwidth log.

In addition cycle accurate SRAM/DRAM access logs are also dumped and could be accesses at ```./outputs/<topology_name>/layer_wise```


## Contributing

## Authors

## License

This project is licensed under the MIT License - see the LICENSE.txt file for details


