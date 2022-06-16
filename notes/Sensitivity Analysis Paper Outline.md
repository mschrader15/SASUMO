---
tags: ~
date_created: 06/15/22
date_modified: 06/15/22
publish: true
title: Sensitivity Analysis Paper Outline
---

# Investigating the Sensitivity of Common Optimization Targets to Traffic Microsimulation Parameters

**Note to *Dr. Bittle***: This is my working title. It expands the scope, but I would argue not by much. Dr. B has asked me to start calculating travel time and/or delay. By adding this functionality, I should also be able to incorporate many of the common targets of RL and traditional light optimizations. Adding these metrics makes the paper more useful to the community.

Regardless, **I will be finished by end of July**.

## Introduction / Background

### What is Traffic Microsimulation & Why Use it

Pull liberally *Energy Analysis - Transportation Research - Part C*.

One use case is traffic signal optimization. There are several targets used:

### Optimization Targets and Goals

#### Fuel Consumption

Pull from *Energy Analysis - Transportation Research - Part C*

**Does the quantity really matter though?** Should I also look at the dynamics of the consumption? I can look at “where” it is happening
- Are we pitching this as a precursor to traffic signal optimization? If so is it the absolute quantity that really matters? Or should we more be saying that the dynamics depend on the car-following parameters, fleet composition and others, and that it is important to calibrate the model so that these dynamics are correct.

#### Other

**To be determined if I include**

Before optimization can be pursued, the simulation must be calibrated…

### Simulation Calibration

The USDOT defines as calibrated simulation as…. (brief discussion here as more details could be presented in the [Procedure](Sensitivity%20Analysis%20Paper%20Outline.md#procedure))

However, there are many parameters in traffic microsimulation. **Papers like XX** have shown that many combinations of parameters can achieve calibration.  While these simulations all achieve calibration, the absolute value of [Optimization Targets and Goals](Sensitivity%20Analysis%20Paper%20Outline.md#optimization-targets-and-goals) can vary drastically. This presents the importance of calibrating not just to macro traffic dynamics, but also investigating the sources of uncertainty in the traffic simulation…

### Sources of Uncertainty in Traffic Simulation

Describe the forms of uncertainty in *Traffic Simulation*.
- Liberally cite and pull from *📚 Library/📜 Articles/A two-level probabilistic approach for validation of stochastic traffic simulations impact of drivers’ heterogeneity models*.
- *aleatory uncertainty* that cannot be modeled
- *stochastic uncertainty* that can be modeled

#### Uncertainty in Car Following Parameters

Cite the papers in [Sobol Sensitivity Analysis Parameters](Sobol%20Sensitivity%20Analysis%20Parameters.md) as well as the range of values.

#### Uncertainty in Fleet Composition

* https://www.sciencedirect.com/science/article/pii/S1361920915000450
* Could use this as a reference as well: https://www.bts.gov/product/national-transportation-statistics

#### How This Uncertainty Manifests in Fuel Consumption Estimation

* How does uncertainty manifest in the fuel consumption estimation
  * There is uncertainty in the car-following models, aka in the true "trajectories" of the vehicles
  * Maybe can allude to the error here: https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf

### Why Do a Sensitivity Analysis

Presented above are sources of uncertantity.  Some can be addressed, some can’t. To decide on which of the calibrate-able parameters to focus on, we perform a senstivity analysis…

#### Talk About Opportunities for Calibration and Why We Picked the Parameters That We Did ^b9c95a

* Calibrating car-following models using radar / camera data
* Calibrating fleet composition using camera & *🔨 Projects/👨‍🔬 Research/DOE Project/Radar/Radar* data
* Finding the true "free"-flow speed

## Procedure

### Intro to Simulation Network

Use *Energy Analysis - Transportation Research - Part C* as reference

#### Describe the Traffic Lights

Based on true controllers in the network.

### Calibration

Use *Energy Analysis - Transportation Research - Part C* as reference. Cite the USDOT Calibration framework, almost copy paste from last paper

### Car-Following Model Specifics

#### Why IDM Car-Following Model

* Use https://ieeexplore.ieee.org/document/8317836
* And use https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf

Chose IDM car-following model based on papers which show it as the best calibrated, as well as SUMO guidance.

#### Why the Bounds on the Car Following Model

see [Sobol Sensitivity Analysis Parameters](Sobol%20Sensitivity%20Analysis%20Parameters.md)

### Sobol Sensitivity Analysis

Describe the how the sobol sensitivity analysis works at a high level

* Cite Sobol, SALib, and the papers that SALib references

#### How to Apply the Senstivity Analysis to SUMO

*Sensitivity Analysis* is predicated on running many model evaluations. In the case of traffic simulation, this can consume tremendous computation time. Traffic simulations should have one hour of "warm-up" and "cool-down" time ==Cite This==, so even in the case of a relatively short traffic simulation, there are thousands of traffic simulation seconds to evaluate. For the Sobol analysis, these simulation seconds are multiplied by the number of runs required,

Present the general framework.

How is randomness handled.

#### Checking Calibration Throughout

When only the USDOT calibration is considered, there is a positive skew on the fuel consumption distribution. The bulk of simulations are clustered in a normal distribution, however there is a long right tail of fuel consumers that

Present brief discussion of finding out that combination of bounds leads to unrealistic traffic.

## Results

### Emissions

#### Discussion of Intra-Sensitivity Analysis Variation

Present the distribution of fuel consumption for simulation that also meet calibration.>)

#### Car Following Parameters

* The most important parameters are

#### Fleet Composition

* Knowing the # of trucks is important

#### Model Fidelity

* Hopefully we can get to this. I want to prove that knowing the percentage of trucks is more important than the fidelity of the vehicle model

### Other Metrics

Present the same results above except for other metrics

### Conclusion / Discussion

* Modern V2X and ITS systems give traffic modelers exciting new ways to calibrate traffic simulations. Point to the fact that the factors in which the traffic simulation is most sensitive to are also the factors that are the easiest to calibrate
  * Could also move [Sobol Sensitivity Analysis of Traffic Micro Simulation > ^b9c95a](Sobol%20Sensitivity%20Analysis%20of%20Traffic%20Micro%20Simulation.md#b9c95a) here
* 
