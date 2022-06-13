---
tags: ~
date_created: 06/02/22
date_modified: 06/13/22
publish: true
type: note
title: Sobol Sensitivity Analysis Parameters
---

# Sobol Sensitivity Analysis Parameters

This document is both a summary of the parameters used in [Sobol Sensitivity Analysis of Traffic Micro Simulation](Sobol%20Sensitivity%20Analysis%20of%20Traffic%20Micro%20Simulation.md) and a log of my findings / thoughts since I started serious sensitivity analyses on *2022-06-02*.

## Car Following Parameters

All car-following parameters are assigned to vehicles in simulation using a vehicle distribution of 1000 vehicles. At the point of distribution file generation, the 1000 vehicles are assigned static values according to the specified distribution of each parameter. The simulation then samples from this 1000 vehicle distribution every time that a vehicle is inserted in simulation. This means that the same vehicle could appear > 1 time over the duration of the simulation. The 1000 number was/is arbitrary.

I selected many of the parameters based on prior *Sobol Sensitivity Analysis*‘s. Below is a summary of their findings:

* *Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions*
  * They do a sensitivity analysis on the total fuel consumption, as well as emissions. The authors **only consider the Gipp’s *car-following model*** in the sensitivity analysis, so the results need to be taken with a grain of salt. Interestingly, the Gipps car-following model is not even built into SUMO. That being said, many of the parameters are similar in their description and purposed. They find that (outside of vehicle ID) the following parameters heavily influence the fuel consumption variance (\[Source\](*Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions > ^cce66f*)):
    * Max deceleration
      * $d\_{max, j}$
    * Headway
      * $\tau_j$
    * Perceived Deceleration of Leader Vehicle
      * $d\_{max, j-1}$
  * My findings are counter to several of theirs. My sensitivity analyses with IDM car-following model shows that max deceleration ($d\_{max, j}$) is not a contributing factor. In their sensitivity analysis, maximum acceleration ($a\_{max,j}$) is the 4th most contributing variable out of 6. I am seeing that it is **the most** contributing parameter for our sensitivity analysis. One explanation of this finding is that the authors are really doing a sensitivity analysis on followers of a lead vehicle. The lead vehicle trace comes from the NGSIM database and thus constrains the acceleration from standstill. In comparison, there are many full-stop events and corresponding accelerations without leader vehicles in our simulation.
* *Do We Really Need to Calibrate All the Parameters Variance-Based Sensitivity Analysis to Simplify Microscopic Traffic Flow Models*
  * The authors (same authors as above) perform a sensitivity analysis into the calibration of IDM car-following model. Their metric is both RMSE of velocity and RMSE of position.  They find that the calibration is most sensitive to the following:
    * Headway
      * $\tau$
    * The acceleration exponent
      * $\beta$
      * The symbol used for this variable varies by paper. It is interesting that they found it to be important, as it usually considered fixed at 4 in IDM.
        * See [https://journals.sagepub.com/doi/pdf/10.3141/2088-16](https://journals.sagepub.com/doi/pdf/10.3141/2088-16)
        * SUMO documentation has it constant at 4
      * There are a few papers that consider it part of a distribution
        * [https://journals.sagepub.com/doi/pdf/10.3141/2390-03](https://journals.sagepub.com/doi/pdf/10.3141/2390-03)
          * 10-40 (why)
        * [https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf](https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf)
          * Actually cite above, they consider 1-40
            * Find that mean is 3.528, sd = 3.6240, lb=1, ub=10
    * Maximum acceleration
      * $a\_{max}$
    * As an aside, the same authors find in a \[more recent paper\](*About calibration of car-following dynamics of automated and human-driven vehicles Methodology, guidelines and codes*) that
      * 
        * Thus a calibration on spacing is preferential to a calibration on velocity.

### Car-Following Model

There are several car-following models. Thus far I have used the IDM *car-following model*, as it is one of the most used in literature and SUMO recommends it for sub-second simulation . Dominik Salles recently added an **extended**-IDM model to SUMO. [He published a paper in the SUMO UC about the calibration effort](https://sumo.dlr.de/2020/SUMO2020_paper_28.pdf). The aim of the model is to correctly replicate submicroscopic acceleration profiles of single vehicles and drivers. From my rudimentary analysis, the trajectories do look more realistic (smoother acceleration curves). My concerns with using this model would come from the fact that it is brand new and not widely adopted. I added it as a binary choice to a sensitivity analysis below

* Range:: `[EIDM, IDM][val > 0], val= uniform(-1, 1)`
* Some of the IDM parameters & EIDM parameters are not the same (Action Step Length), which makes the comparison a bit difficult.

Results from `Distro_Width+Random_Seed/06.02.2022_11.04.22` show that EIDM vs IDM is not important at a sim step of 0.1

* $ST = 0.033612$
* EIDM fc average over 2304 runs:
  * mean 114.850281
  * std 12.409092
* EIDM fc average over 2304 runs:
  * mean 112.458234
  * std 11.337178

**Personally I think that we stick with IDM to make the paper more generalizable**. May continue to use EIDM in our simulations though as fewer sawtooth like velocity trajectories.

As of *2022-06-02*, it is removed from sensitivity analysis going forward.

### Tau

From [SUMO](https://sumo.dlr.de/docs/Car-Following-Models.html#tau):

 > 
 > This parameter is intended to model a drivers desired minimum time headway (in seconds). It is used by all models. Drivers attempt to maintain a minimum time gap of tau between the rear bumper of their leader and their own (front-bumper + minGap) to assure the possibility to brake in time when their leader starts braking.

Early *Sobol Sensitivity Analysis* shows this as the **second** or **third** most sensitive parameter (when fleet composition is not considered)

* `Distro_Width+Random_Seed/06.01.2022_17.19.09 = 0.45`

#### Bound Selection

* *Exploring the variance contributions of correlated model parameters A sampling-based approach and its application in traffic simulation models*
  * [DOI](https://doi.org/10.1016/j.apm.2021.04.012)
    * The parameters ultimately come from: [https://journals.sagepub.com/doi/pdf/10.3141/2249-09](https://journals.sagepub.com/doi/pdf/10.3141/2249-09)
  * Range::  `[0.05, 3]`
  * Shape::  Normal
    * $\mu = 1.266$ , $\sigma = .507$
* *Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions*
  * [DOI](https://www.sciencedirect.com/science/article/pii/S1361920914001692)
  * Range:: `[0.1, 3 ]`
  * Shape::  homogenous & uniform across fleet
* [https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf](https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf)
  * Range::  `[0.1, 5]`
  * Shape::  Normal (They don’t discuss explicitly)
    * Calibrated
      * $\mu = 0.8780$ , $\sigma = 0.3343$
    * Observed
      * $\mu = 1.7956$ , $\sigma = 0.3488$

### Acceleration

From \[SUMO\]([Definition of Vehicles, Vehicle Types, and Routes - SUMO Documentation](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html#car-following_model_parameters):

 > 
 > The acceleration ability of vehicles of this type (in m/s^2)

Early results show that this is the **most important parameter**.

#### Bound Selection

* *Exploring the variance contributions of correlated model parameters A sampling-based approach and its application in traffic simulation models*
  * [DOI](https://doi.org/10.1016/j.apm.2021.04.012)
  * Range::  `[0.05, 6]`
  * Shape::  Log-Normal
    * $\mu = 1.406$ , $\sigma = .1012$
* *Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions*
  * [DOI](https://www.sciencedirect.com/science/article/pii/S1361920914001692)
  * Range:: `[0.4, 8 ]`
  * Shape::  homogenous & uniform across fleet
* [https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf](https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf)
  * Range::  `[0.1, 5]`
  * Shape::  Normal (They don’t discuss explicitly)
    * Calibrated
      * $\mu = 0.8418$ , $\sigma = .2775$
    * Observed
      * $\mu = 2.1384$ , $\sigma = 1.7144$
      * I think the explanation between calibrated and observed is eloquently discussed in *📚 Library/📜 Articles/A two-level probabilistic approach for validation of stochastic traffic simulations impact of drivers’ heterogeneity models*
        * 

### Deceleration

From [Definition of Vehicles, Vehicle Types, and Routes - SUMO Documentation](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html#car-following_model_parameters):

 > 
 > The deceleration ability of vehicles of this type (in m/s^2)

SA shows that this parameter is not important in overall fuel consumption

#### Bound Selection

* *Exploring the variance contributions of correlated model parameters A sampling-based approach and its application in traffic simulation models*
  * [DOI](https://doi.org/10.1016/j.apm.2021.04.012)
  * Range::  `[0.05, 8]`
  * Shape::  log-normal
    * $\mu = 2.225$ , $\sigma = 1.849$
* *Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions*
  * [DOI](https://www.sciencedirect.com/science/article/pii/S1361920914001692)
  * Range:: `[0.4, 10]`
  * Shape::  homogenous & uniform across fleet
* [https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf](https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf)
  * Range::  `[0.1, 5]`
  * Shape::  Normal (They don’t discuss explicitly)
    * Calibrated
      * $\mu = 0.8150$ , $\sigma = 0.7251$
    * Observed
      * $\mu = 3.1474$ , $\sigma = 0.7883$

### minGap

From [Definition of Vehicles, Vehicle Types, and Routes - SUMO Documentation](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html#car-following_model_parameters):

 > 
 > Minimum Gap when standing (m)

#### Bound Selection

* *Exploring the variance contributions of correlated model parameters A sampling-based approach and its application in traffic simulation models*
  * [DOI](https://doi.org/10.1016/j.apm.2021.04.012)
  * Range::  `[0.05, 5]`
  * Shape::  log-normal
    * $\mu = 2.172$ , $\sigma = 1.152$
* *Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions*
  * [DOI](https://www.sciencedirect.com/science/article/pii/S1361920914001692)
  * Range:: `[4, 10]`
  * Shape::  homogenous & uniform across fleet
* [https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf](https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf)
  * Range::  `[0.1, 10]`
  * Shape::  Normal (They don’t discuss explicitly)
    * Calibrated
      * $\mu = 1.5554$ , $\sigma = 0.9633$
    * Observed
      * $\mu = 3.1474$ , $\sigma = 0.1.1736$

From early sensitivity analysis experience, minGap is strongly influential in calibration. When the minGap is greater than 5-6, many more simulations fail calibration. For this reason, I am cutting the range from `[.1 to 6]` as of *2022-06-02* ^951963

After cutting the range, I find that minGap is no longer as influential. This is an interesting finding to me, and one that I need to read more about in literature.

* Update on *2022-06-13*: I have struggled to find resources on the way that sensitivity bounds themselves effect the simulation.

### Reaction Time (Action Step)

From [Definition of Vehicles, Vehicle Types, and Routes - SUMO Documentation](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html#car-following_model_parameters):

 > 
 > The action step length works similar to a reaction time (vehicle will not react immediately to changes in their environment) but it also differs from a "true" reaction time because whenever a vehicle has it's action step it reacts to the state in the previous simulation step rather than to the state that was seen in their previous action step. Thus the Perception-Reaction loop is less frequent but still as fast as the simulation step length.

Based on this definition, I don’t know that it should be included . Some car-following models have reaction time built in to them. IDM does not. Early SA do show that it is the 3rd most significant of the car-following-model parameters, however that is due almost entirely to the 2nd order effects (meaning the interplay with the other variables.)

Setting the action step to anything other that .2 or .4 ends up in unrealistic simulation behavior. I think this is a limitation of the implementation and therefore we should not include in the sensitivity analysis as a calibrate-able parameter.

#### Bound Selection

* *Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions*
  * [DOI](https://www.sciencedirect.com/science/article/pii/S1361920914001692)
  * Range:: `[0.1, 3]`
  * Shape::  homogenous & uniform across fleet
* [https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf](https://arxiv.org/ftp/arxiv/papers/1811/1811.06395.pdf)
  * Range::  `[0.3, 3]`
  * Shape::  not discussed
    * Gipps
      * $\mu = 1.2214$ , $\sigma = .4831$
    * GHR
      * $\mu = .6476$ , $\sigma = .4346$
* [https://journals.sagepub.com/doi/pdf/10.3141/2249-09](https://journals.sagepub.com/doi/pdf/10.3141/2249-09)
  * Range::  `[0.2, 3.5]`
  * Shape::  lognormal
    * Gipps
      * $\mu = .781$ , $\sigma = 0.418$
    * Helly
      * $\mu = 0.438$ , $\sigma = .237$

### Apparent Deceleration

From [Car-Following-Models - SUMO Documentation](https://sumo.dlr.de/docs/Car-Following-Models.html#decel_apparentdecel_emergencydecel):

 > 
 > The "safe" velocity for every simulation step is computed by the configured carFollowModel based on the leading vehicle as well as the right-of-way-rules. To ensure safe driving under various circumstances, the maximum braking capability of the leader vehicle is also taken into account. This value is taken from the **apparentDecel** attribute of the leader vehicle (which defaults to the same value as it's **decel** attribute).

I am testing this as *Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions* finds that the apparent deceleration of the leader vehicle is the 3rd most sensitive parameter.

I don’t actually know how the radar (or camera) based calibration would be able to calculate the “true” value for this parameter, as it is based entirely in driver psychology.

I investigated the affect in `Distro_Width+Random_Seed+Apparent_Decel+Sim_Step+Emissions_Device/06.06.2022_10.34.19`. It is `0` meaning that the IDM car-following model doesn’t consider it at all. It will be avoided in future sensitivity analysis as of *2022-06-06*

#### Bound Selection:

This is the same as [Deceleration](Sobol%20Sensitivity%20Analysis%20Parameters.md#deceleration)

### Startup Delay

Jakob Erdmann suggested including this parameter. It basically models the reaction time to green traffic light. The problem is that in it’s current iteration, a vehicle has the same reaction time at every stopping event. This leads to very unrealistic traffic when the startup delay is high.

I have raised this issue in GitHub. Hopefully it is fixed so that we can implement it in the *Sensitivity Analysis*

* [Startup loss time/reaction time · Issue #7832 · eclipse/sumo · GitHub](https://github.com/eclipse/sumo/issues/7832)

Update *2022-06-13*:

* When I use a lognormal distribution, aka a high density of near 0 startup delay with a few cars that have high delay, the resulting traffic flow is still highly unrealistic.

### Junction Parameters

#### jmStoplineGap

Jakob Erdmann recommended the inclusion of this parameter.

From [Definition of Vehicles, Vehicle Types, and Routes - SUMO Documentation](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html#junction_model_parameters)

 > 
 > This value configures stopping distance in front of prioritary / TL-controlled stop line. In case the stop line has been relocated by a [**stopOffset**](https://sumo.dlr.de/docs/Networks/SUMO_Road_Networks.html#stop_offsets) item, the maximum of both distances is applied.

* I did a broad sweep of this parameter from 0 - 5 meters.
  * Total fuel consumption is not sensitive to this parameter so it will be ignored moving forward from (*2022-06-02*)
    * `Distro_Width+Random_Seed/06.01.2022_17.19.09 = 0.0031`

#### jmTimegapMinor

From [Definition of Vehicles, Vehicle Types, and Routes - SUMO Documentation](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html#junction_model_parameters)

 > 
 > This value defines the minimum time gap when passing ahead of a prioritized vehicle.

I haven’t included this parameter into the Sensitivity Analysis yet, but calibration shows that it is important in the car driving behavior. If the time gap is too low, cars in permissive left turn lanes cutoff the oncoming mainline (There is a discussion of this behavior [Vehicles in Permissive left lane "cut" the vehicles from the opposite straight lane · Issue #10384 · eclipse/sumo · GitHub](https://github.com/eclipse/sumo/issues/10384)). It the time gap is too high, cars in side streets do not pull out in front of incoming traffic. This unwillingness to ever impede the incoming traffic leads to unrealistic congestion on the side streets. **I am not going to include in the sensitivity analysis**, but I wanted to document the behavior that I see here.

## Fleet Composition

### % Class-8 Truck

[AADT data from 2020 ](https://aldotgis.dot.state.al.us/TDMPublic/)shows 11% truck traffic.

Car-following parameters for heavy duty vehicles are hard to find. The best source that I have found is:

* [Optimizing Gap Tracking Subject to Dynamic Losses via Connected and Anticipative MPC in Truck Platooning | IEEE Conference Publication | IEEE Xplore](https://ieeexplore.ieee.org/document/9147849)

**Should I also include the car-following parameters for the trucks in the sensitivity analysis?**

## Traffic Light Parameters

As discussed with *Dr. Bittle*, the goal of including the *NEMA dual ring* behavior in the *Sobol Sensitivity Analysis* would be to:

1. Validate that the time put into *Building a NEMA Controller in SUMO* and the *2022 SUMO Conference Paper* was worth it.
1. Emphasize that this paper is a sensitivity analysis of a signalized corridor, and thus contributes new findings to the *Traffic Simulation* space.
   1. I can’t find any papers where traffic signal behavior was included in a sensitivity analysis.
      1. Caveat - there are many papers that document the influence that *Traffic Light* control has on emissions and fuel consumption.
         1. [Full article: Evaluating the impacts of urban corridor traffic signal optimization on vehicle emissions and fuel consumption](https://www.tandfonline.com/doi/full/10.1080/03081060.2011.651877)

I also see a couple arguments against including the traffic signal behavior in the sensitivity analysis:

1. The goal of many *Traffic Simulation*s is to optimize the traffic signal behavior, thus it is changed from run to run. It’s impact on traffic behavior is understood and expected.
   1. Counter to this is the generation of “baselines”, i.e. a strong model of how the current lights operate. This is absent in many of the traffic signal optimization papers.
1. Most traffic simulation software has the capability to emulate the traffic signal behavior exactly.

Per discussion with *Dr. Bittle* on *2022-06-08*, the [Traffic Light Parameters](Sobol%20Sensitivity%20Analysis%20Parameters.md#traffic-light-parameters) will be left out of the sensitivity analysis.

### Mainline Green Times

This is the first parameter that I intend to include as it will be the easiest to tweak. The extra time for the mainline will be distributed to the other phases in the controller evenly.

I could make this one parameter for the whole network with a uniform, continuous distribution.

$G\_{mod} = uniform(0, 20)$
$G\_{mod, other} = G\_{mod} / N\_{phases}$

### Potential Others

1. Cycle Time
1. Offset
1. Actuated vs. Fixed Time
1. Coordinated vs. Non-Coordinated
1. Detector Delay on side-streets
   1. This would represent a potentially overlooked parameter that can impact the simulation flow drastically (stopping mainline for single car on side-street vs. ignoring that car)

## Simulation Parameters

### Random Seed

SUMO simulations use the same random seed for every simulation run unless it is explicitly set by the user.  Per *An Exploratory Study of Two Efficient Approaches for the Sensitivity Analysis of Computationally Expensive Traffic Simulation Models*, I included the random seed itself into the SUMO model.  They do not give an explanation for their inclusion, but perhaps it provides a good benchmark. Anything less than the inherent randomness should definitely not be considered as an important parameter.

### Simulation Step

Nothing larger than 1 second will be considered as my understanding is that this is the upper bound on where *car-following model*s are accurate. I can’t find simulation step mentioned in prior sensitivity analyses. It is undoubtably important, even though it is a parameter that is easily changed.

#### Bounds

I am considering `[0.01, .1, .2, .5, 1][math.floor(val)]`.

### Emissions Device Probability

Pre *2022-06-08*:

* This is not a calibrate-able parameter. However, hopefully the output will not be sensitive to the value of this, meaning that I can set the device probability to a percentage that is lower than 1. I will determine that value by running many of the same simulations and find variance and mean, etc. I can than calculate what we want the statistical significance to be and use the value of that emissions probability going forward.
* I would suspect that this # will be different when Trucks are introduced into the network. Because they makeup only ~10% of total traffic but contribute disproportionally to the overall emissions, I will run the variance with the 10% truck distribution.

#### Bounds

`uniform(0.05, 1)`

* [x] Sweep the range and figure out how low it can go while still preserving the shape of distribution. ✅ 2022-06-07
  * I have to determine what the distribution should look like here first, which means running at 100%.
  * [Bias of an estimator - Wikipedia](https://en.wikipedia.org/wiki/Bias_of_an_estimator)
  * 
  * Based on this finding and the non-linear aspect of estimator variance, **I still need to use the full output** for the *Sensitivity Analysis*. This also partly due to the fact that the standard deviation is non-linear. I think that using a “sample estimator” of the population could skew the sensitivity analysis results.

## Questions

### Mathematical Questions

#### How Do the Bounds Influence the Sensitivity Analysis?

I am observing that when a sensitivity analysis is started with unrealistic parameter bounds, the outliers (interplay of a couple variables) influence the Sobol indicies. Re-doing the sensitivity analysis with a more realistic range seems to lead to different results.

Prior papers used very wide bounds on their sensitivity analyses (see [Acceleration](Sobol%20Sensitivity%20Analysis%20Parameters.md#acceleration), [Tau](Sobol%20Sensitivity%20Analysis%20Parameters.md#tau)). When I run simulations with the parameters near these upper bounds, the traffic flow is visually unrealistic and calibration is more likely to fail (see [^951963](Sobol%20Sensitivity%20Analysis%20Parameters.md#951963)).

I wonder two things here:

1. How do outliers influence the *Sobol Sensitivity Analysis* ? Are there prior works on the setting of “realistic” bounds for the parametric inputs to the Sensitivity Analysis?
1. Is this an artifact of the simulation software used. If so, can I write about this observation?

#### Continuous Vs. Discrete Inputs?

Per discussion with *Dr. Bittle*, I will continue as-if this a non-topic, as SALib users frequently consider discrete inputs. We can dig deeper into the implication if it raised as an issue in review.

#### Correlated Inputs?

See *Exploring the variance contributions of correlated model parameters A sampling-based approach and its application in traffic simulation models* for an explanation. The traditional *Sobol Sensitivity Analysis* assumes that the inputs are independent.

To account for this, I could potentially use the High Dimensional Model Representation method [Concise API Reference — SALib 1.4.6b0.post1.dev20+gd3c9348.d20220605 documentation](https://salib.readthedocs.io/en/latest/api.html#high-dimensional-model-representation)

* A benefit is that this also generates a simplified model that can be used
* It can also be ran on the same data that *Sobol Sensitivity Analysis* requires. From now on I will attempt to do both analyses on the data

### Simulation Questions

#### Stochastic Vs. Determined Route Files?

This is an open question for me.  The stochastic route files lead to calibration failures more often. Is it a less fair comparison to use the stochastic route file?

I am investigating this *2022-06-07*.  A couple of interesting findings:

1. The probabilistic route files that are generated by the `routeSampler` consistently fail calibration. They have periods of unrealistic flow. This is in comparison to the number based flows which always pass calibration.
   1. I think that the issues is that the lanes can’t handle too frequent of insertions.
   1. I also tried running the *stochastic* route files with wider intervals, ie the beginning and endings of all flows are `aggregation_interval` apart (`600S`).  It makes calibration even better for numbered flows and worse for the stochastic route files.
1. The average fuel consumption of number-based flow is much less than a probability based flow. This needs to be explained.
   1. It can be explained by overwhelmed side-streets.

As of *2022-06-13*, I am running the sensitivity analysis first with deterministic route files. I am expecting a decreased role of `random_seed` with deterministic route files vs. the stochastic route files.

#### Intra-fleet Parameter Distribution?

As of *2022-06-13*, all of the sensitivity analyses work as such:

1. The lower and upper bounds of all variables are input into a function that generates a Sobol sequence
   1. Sobol sequence is a quasi-random low-discrepancy sequence used to generate uniform samples of parameter space
      1. Aka quasi-monte carlo
1. Each simulation is ran with a specific combination of parameters, representing a row in the Sobol sequence.
   1. If the parameter is one of the [Car Following Parameters](Sobol%20Sensitivity%20Analysis%20Parameters.md#car-following-parameters) , the parameter value is taken to be the mean of a uniform distribution. The vehicle distribution for simulation is generated by creating a uniform distribution for each parameter, $uniform(\mu - width, \mu + width)$. The distribution is bounded by the absolute maximum and minimum, which are the lower and upper bounds of the sensitivity analysis.

**The question here is can I swap the uniform distribution for the actual distributions, ie lognormal, normal, etc?** If I do swap to a lognormal or normal distribution, do I change the mean or the variance? Both?

Plan here is to fix the variance and sweep the mean value of a couple of distributions. Compare the results to a sensitivity analysis with uniform distributions. 

### Analysis Questions

#### Include Fuel Consumption Dynamics?

Should I compare the consumption dynamics? The goal here would be to prove that not only is the total # different, but the way in which that fuel is consumed is different as well. If the fuel consumption dynamics are different, it adds even more validity to the goal of the sensitivity analysis.

**How should I compare the fuel consumption “dynamics”?**

* Look into the % of fuel consumed during X vs. Y?
  * Example being that if there are trucks in the network, maybe more fuel is consumed on mainline than side streets?
  * If vehicles accelerate aggressively, perhaps more fuel is consumed during re-acceleration periods?

## Consolidated Questions for *Dr. Bittle*

1. \[Should I analyze fuel consumption dynamics\]([Include Fuel Consumption Dynamics](Sobol%20Sensitivity%20Analysis%20Parameters.md#include-fuel-consumption-dynamics))?
1. \[Does it make sense to consider more intra-fleet distributions than just uniform\]([Intra-fleet Parameter Distribution](Sobol%20Sensitivity%20Analysis%20Parameters.md#intra-fleet-parameter-distribution))?
1. \[Should I separate out the car and truck car-following parameters\]([Class-8 Truck](Sobol%20Sensitivity%20Analysis%20Parameters.md#class-8-truck))?
1. Any other thoughts on above?
