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

I selected many of the parameters based on prior [Sobol Sensitivity Analysis](../../../../Sobol%20Sensitivity%20Analysis.md)‘s. Below is a summary of their findings:

* [Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Does%20traffic-related%20calibration%20of%20car-following%20models%20provide%20accurate%20estimations%20of%20vehicle%20emissions.md)
  * They do a sensitivity analysis on the total fuel consumption, as well as emissions. The authors **only consider the Gipp’s *car-following model*** in the sensitivity analysis, so the results need to be taken with a grain of salt. Interestingly, the Gipps car-following model is not even built into SUMO. That being said, many of the parameters are similar in their description and purposed. They find that (outside of vehicle ID) the following parameters heavily influence the fuel consumption variance (\[Source\]([Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions > ^cce66f](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Does%20traffic-related%20calibration%20of%20car-following%20models%20provide%20accurate%20estimations%20of%20vehicle%20emissions.md#cce66f))):
    * Max deceleration
      * $d\_{max, j}$
    * Headway
      * $\tau_j$
    * Perceived Deceleration of Leader Vehicle
      * $d\_{max, j-1}$
  * My findings are counter to several of theirs. My sensitivity analyses with IDM car-following model shows that max deceleration ($d\_{max, j}$) is not a contributing factor. In their sensitivity analysis, maximum acceleration ($a\_{max,j}$) is the 4th most contributing variable out of 6. I am seeing that it is **the most** contributing parameter for our sensitivity analysis. One explanation of this finding is that the authors are really doing a sensitivity analysis on followers of a lead vehicle. The lead vehicle trace comes from the NGSIM database and thus constrains the acceleration from standstill. In comparison, there are many full-stop events and corresponding accelerations without leader vehicles in our simulation.
* [Do We Really Need to Calibrate All the Parameters Variance-Based Sensitivity Analysis to Simplify Microscopic Traffic Flow Models](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Do%20We%20Really%20Need%20to%20Calibrate%20All%20the%20Parameters%20Variance-Based%20Sensitivity%20Analysis%20to%20Simplify%20Microscopic%20Traffic%20Flow%20Models.md)
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
    * As an aside, the same authors find in a \[more recent paper\]([About calibration of car-following dynamics of automated and human-driven vehicles Methodology, guidelines and codes](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/About%20calibration%20of%20car-following%20dynamics%20of%20automated%20and%20human-driven%20vehicles%20Methodology,%20guidelines%20and%20codes.md)) that
      * # About calibration of car-following dynamics of automated and human-driven vehicles: Methodology, guidelines and codes
        
        ## Metadata
        
        * Author: [sciencedirect.com]()
        * Title: About calibration of car-following dynamics of automated and human-driven vehicles: Methodology, guidelines and codes
        * Reference: https://www.sciencedirect.com/science/article/pii/S0968090X21001832
        * Category: #article
        ## Highlights
        
         > 
         > First, a number of calibration settings, which are inappropriate but often used in the field literature, have been identified. In the epistemological framework we assume in this study, this result is deemed to be definitive. One sound refutation is sufficient to dismiss a general theory, indeed (see the essay by Popper, 1963, on conjectures and refutations).  \[Updated on 2022-05-27 07:04:04\](https://hyp.is/GsXOUt21Eey3f48tl3Wbmg/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        They must be Nassim Taleb fans
        
        ---
        
         > 
         > In this general formulation, there are six important elements related to model calibration: the model itself, data and data/model integration scheme, the MoP, the GoF, and the optimization algorithm. \[Updated on 2022-05-27 07:06:11\](https://hyp.is/ZiF6Nt21EeyDK_NOkAenVg/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        We aren't doing car-following calibration, but I think that I could still reference this
        
        ---
        
         > 
         > When either one or more measurements are available (e.g. only spacing from GPS, or spacing from GPS and relative speed from radar), the integration/differentiation scheme of data needs to be the same adopted in model simulation.  \[Updated on 2022-05-27 07:11:20\](https://hyp.is/Hr0mTt22Eey5PkNGtZ_hzA/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        Hmm. How should this actually be implemented in practice?
        
        ---
        
         > 
         > out of 994 articles we have collected and scrutinized from the target journals since 2005, only a small fraction (9%) attempted to calibrate CF models. Among these articles: \[Updated on 2022-05-27 07:16:43\](https://hyp.is/3yp6Jt22EeyyksfclrMCaQ/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        This was us. However we will have the capability in the future
        
        ---
        
         > 
         > Calibrating a model on a nonlinear transformation of an output, e.g. the speed standard deviation, means calibrating a nonlinear transformation of the model itself. As a consequence, when a model is calibrated on such a measure transformation, though it will reproduce the intended characteristic at its best, resulting calibrated CF dynamics will be non-optimal. \[Updated on 2022-05-27 07:19:56\](https://hyp.is/UhhQ-N23EeyvvkMm_XZbTw/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        Why is this. I didn't realize that the car-following model was linear to begin with.
        
        ---
        
         > 
         > If several measures are independently collected through separate devices (e.g. position from GPS, relative velocity from radar, acceleration from an inertial platform), these measurements need to be “internally consistent”. Specifically, spacing (speed) measurements need to be equal to the integral of speed (acceleration) measurements (see the formal definition of internal consistency in Punzo et al., 2011, later reported in Treiber and Kesting, 2013). \[Updated on 2022-05-27 07:19:58\](https://hyp.is/Uw8SbN23Eeyka--t37wP5A/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        So we are going to have to pay close attention to the "internal consistency" of our 
        
        ---
        
         > 
         > Downhill simplex and other algorithms, which were not reported in that paper for the sake of brevity (i.e. Interior Point, Trust Region Reflective and Sequential Quadratic Programming solvers), failed to rediscover the predetermined parameter values. As claimed in the Introduction, we consider the proved inability of some algorithms to successfully calibrate a CF model – in a systematic and fair test environment – as a sufficient proof to dismiss these algorithms.  \[Updated on 2022-05-27 07:19:59\](https://hyp.is/U-0WrN23Eey5Ty_U-EtqtA/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        This is good to know for *car-following* going forward
        
        ---
        
         > 
         > Looking at Table 1, one may conclude that there is still no consensus on what MoP should be used in a CF model calibration setting. In truth, this long-standing methodological problem in the car-following theory was solved in a recent paper, Punzo and Montanino (2016). \[Updated on 2022-05-27 07:39:14\](https://hyp.is/BGD8fN26EeyDTMNUl9E3uA/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        They sure do like to reference themselves lol
        
        ---
        
         > 
         > If we calibrate on speed, we will reach optimality on speed, but resulting spacing will be non-optimal (optimality on spacing is reached when calibrating on spacing, of course). In other words, we have contrasting optimization objectives, which inevitably leads to the fact that the optimality on one MoP is detrimental to the optimality on another MoP. Thus, if we calibrate on speed, we cannot reduce the error on spacing without at the same time worsening the error on speed, and vice versa. This property is also known as Pareto-efficiency and the two optimal solutions are both Pareto-efficient  \[Updated on 2022-05-27 07:42:06\](https://hyp.is/aqXVmN26EeyMvo-dJxmfbA/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        Makes sense. The question for us here would be what is the fuel consumption more sensitive to. Its more sensitive to speed I think
        
        ---
        
         > 
         > why a calibration on spacing generally yields a relative error on speed which is smaller than the error on spacing caused by a calibration on speed. \[Updated on 2022-05-27 07:43:18\](https://hyp.is/lYT5ut26EeyDQUvIaXzgeQ/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        So we should calibrate for spacing
        
        ---
        
         > 
         > Eq. (3) clarifies that a minimization of spacing errors is equivalent to a simultaneous minimization and optimal time allocation of speed errors. Here “optimal time allocation” is intended as the allocation of speed errors producing the least error in spacing.Thus, a calibration on spacing is optimal in spacing and suboptimal in speed.On the contrary, a trajectory resulting from a calibration on speed is optimal in speed but indeterminate in spacing (i.e., we can have the same error in speeds with very different spacing profiles and very different spacing errors); see Eq. (2). \[Updated on 2022-05-27 07:48:40\](https://hyp.is/VVidUN27EeytbNOTZk-cTQ/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        ^9e81fd
        
        So when you calibrate on velocity it is indeterminate in spacing and less accurate.
        
        ---
        
         > 
         > Since this result is due to the integral relationship between speed and spacing, as explained in Punzo and Montanino (2016), we can easily extend the result to acceleration and speed. We can therefore conclude that, when a single MoP is adopted in a CF calibration objective function (i.e., a single-objective optimisation), spacing is preferable to speed and acceleration. \[Updated on 2022-05-27 07:50:16\](https://hyp.is/jwlVOt27Eey1GH-RIxEKcw/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        makes sense to mwah
        
        ---
        
         > 
         > Can we improve calibration results through a multi-objective optimization? \[Updated on 2022-05-27 07:50:41\](https://hyp.is/nelFBt27Eey1K1udEFBOsw/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        This was my question
        
        ---
        
         > 
         > This point is the ideal objective point obtained by adopting the minimum achievable error for each objective. In case of two objectives/MoPs, e.g., speed and spacing, an indifference curve is any circle in the objectives plane centred in the utopic point; in case of three objectives, i.e., s, v, a, we will have a sphere. \[Updated on 2022-05-27 08:02:33\](https://hyp.is/Rd-Znt29EeywDgvgekKbPA/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        How do they find the minimal achievable error?
        
        ---
        
         > 
         > The most complete trajectories were selected regarding acceleration, cruising, deceleration, following and standstill regimes (Sharma et al., 2019a). The twelve selected trajectories are depicted in Fig. 3. \[Updated on 2022-05-27 08:03:16\](https://hyp.is/X2yOlN29Eey0E8MwVk0oaQ/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        The effect of calibrating on partial trajectories will be important for us to know, as we are not going to have complete trajectories with the radar
        
        ---
        
         > 
         > Focusing on spacing, regardless of the model and dataset, GoFs which are not based on percentage errors i.e., RMSE(s), Theil’s U(s) and MAE(s) are always more preferable than percentage-based GoFs i.e., RMSPE and MAPE (with the only exception of the IDM/Hefei scenario, shown in \[Updated on 2022-05-27 08:18:36\](https://hyp.is/hBtbdN2_Eeyo7HuCXO8bfw/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        This is good to know
        
        ---
        
         > 
         > It is also worth noting that NRMSE(s, v, a) and Theil’s U(s, v, a) have never been used in the literature, to the best of our knowledge. NRMSE was used with a single MoP, i.e. spacing or speed (see e.g., Kesting and Treiber, 2008; Papathanasopoulou and Antoniou, 2015) but, in such a case, it is easy to show that NRMSE is equivalent to RMSE or SSE. \[Updated on 2022-05-27 08:19:15\](https://hyp.is/m1mo6t2_EeyWfpfqAZr5-Q/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        We should put the NRMSE to use
        
        ---
        
         > 
         > In general, the objective functions that are based either on speed only, or on acceleration only, display very large variances in their relative errors on spacing. Conversely, the objective functions based on spacing are much more robust, showing small variances of relative errors on speed as well as on acceleration. NRMSE(s,v,a) and U(s,v,a) consistently show small relative calibration errors on all three measures. \[Updated on 2022-05-27 08:32:23\](https://hyp.is/TdP7UN3BEeyysg_VSuUZGQ/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        This is good to know. Reference this with car-following calibration
        
        ---
        
         > 
         > The presented distributions should be viewed as another tool to assist us in inspecting the objective functions and models behaviour, and should not be assumed as reference distributions, e.g., for traffic simulation5 (concerning the link between microscopic parameters distributions and traffic simulation outputs, the reader can refer to \[Updated on 2022-05-27 08:33:38\](https://hyp.is/na4Slt3BEey5Iqc9v4QA1A/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        So how would you avoid this caveat? Calibrate using simulation directly?
        
        ---
        
         > 
         > With the aim of comparing values across all models, the “time headway” parameter has been chosen, since it is the most influential parameter in calibration among those present in all models – the others being the distance at stop  \[Updated on 2022-05-27 08:34:37\](https://hyp.is/wM96Yt3BEey7pG-i3oVDEA/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        Good to know that others have found the same results that our sensitivity analysis is showing
        
        ---
        
         > 
         > NRMSE(s,v,a) and Theil’s U(s,v,a) are the most preferable objective functions among those being Pareto-efficient. \[Updated on 2022-05-27 08:35:58\](https://hyp.is/8PsS8N3BEeyMg4sgd9CjRg/www.sciencedirect.com/science/article/pii/S0968090X21001832 
        
        For car-following
        
        ---
        
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

Early [Sobol Sensitivity Analysis](../../../../Sobol%20Sensitivity%20Analysis.md) shows this as the **second** or **third** most sensitive parameter (when fleet composition is not considered)

* `Distro_Width+Random_Seed/06.01.2022_17.19.09 = 0.45`

#### Bound Selection

* [Exploring the variance contributions of correlated model parameters A sampling-based approach and its application in traffic simulation models](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Exploring%20the%20variance%20contributions%20of%20correlated%20model%20parameters%20A%20sampling-based%20approach%20and%20its%20application%20in%20traffic%20simulation%20models.md)
  * [DOI](https://doi.org/10.1016/j.apm.2021.04.012)
    * The parameters ultimately come from: [https://journals.sagepub.com/doi/pdf/10.3141/2249-09](https://journals.sagepub.com/doi/pdf/10.3141/2249-09)
  * Range::  `[0.05, 3]`
  * Shape::  Normal
    * $\mu = 1.266$ , $\sigma = .507$
* [Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Does%20traffic-related%20calibration%20of%20car-following%20models%20provide%20accurate%20estimations%20of%20vehicle%20emissions.md)
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

* [Exploring the variance contributions of correlated model parameters A sampling-based approach and its application in traffic simulation models](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Exploring%20the%20variance%20contributions%20of%20correlated%20model%20parameters%20A%20sampling-based%20approach%20and%20its%20application%20in%20traffic%20simulation%20models.md)
  * [DOI](https://doi.org/10.1016/j.apm.2021.04.012)
  * Range::  `[0.05, 6]`
  * Shape::  Log-Normal
    * $\mu = 1.406$ , $\sigma = .1012$
* [Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Does%20traffic-related%20calibration%20of%20car-following%20models%20provide%20accurate%20estimations%20of%20vehicle%20emissions.md)
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
      * I think the explanation between calibrated and observed is eloquently discussed in [📚 Library/📜 Articles/A two-level probabilistic approach for validation of stochastic traffic simulations impact of drivers’ heterogeneity models](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/A%20two-level%20probabilistic%20approach%20for%20validation%20of%20stochastic%20traffic%20simulations%20impact%20of%20drivers%E2%80%99%20heterogeneity%20models.md)
        * # A two-level probabilistic approach for validation of stochastic traffic simulations: impact of drivers’ heterogeneity models
          
          ## Metadata
          
          * Author: [sciencedirect.com]()
          * Title: A two-level probabilistic approach for validation of stochastic traffic simulations: impact of drivers’ heterogeneity models
          * Reference: https://www.sciencedirect.com/science/article/pii/S0968090X20307452
          * Category: #article
          ## Highlights
          
           > 
           > Microscopic models allow for a full characterization of heterogeneity as they provide a discrete representation of traffic flow at a single-vehicle level of detail \[Updated on 2021-07-09 13:03:20\](https://hyp.is/8g_elODfEeuwG2cbhC7RtQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Quote opportunity
          
          ---
          
           > 
           > The approach of encoding the whole heterogeneity in the sole variability of model parameters has been by far the most popular approach in the field literature (as well as in traffic simulation practice; see e.g. commercial micro-simulation software, where there is one default car-following model to mimic the behaviour of all vehicles \[Updated on 2021-07-09 13:04:13\](https://hyp.is/EUk23uDgEeuFkKdAT7bxHg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          This is what I have been doing
          
          ---
          
           > 
           > In the former, a model is calibrated for each agent against its own trajectory data, thus obtaining an empirical pdf of the agent-model parameters \[Updated on 2021-07-09 13:17:33\](https://hyp.is/7nIXguDhEeuN80PnZQ1uFg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Explanation of the non-parametric approach
          
          ---
          
           > 
           > In parametric estimation, instead, an underlying kernel is assumed (e.g. Gaussian, log-normal, etc.) and the parameters of this distribution are estimated from a sample of trajectories \[Updated on 2021-07-09 13:18:45\](https://hyp.is/GXLBrODiEeuczHMllzhTAw/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          parametric approach
          
          ---
          
           > 
           > In all these works, independence of parameters has been assumed. \[Updated on 2021-07-09 13:24:59\](https://hyp.is/-DGO3ODiEeuU7Xs5NHnhTg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I wouldn't have thought this to be an issue, but that makes sense now that it is
          
          ---
          
           > 
           > In truth, the last conclusion was not thoroughly supported. In fact, it was based on the implicit but unproved assumption that simulation outputs resulting from correlated parameters were closer to real traffic data than outputs resulting from uncorrelated ones. However, the simulation experiment in that paper was a synthetic one – it did not replicate the infrastructure and the traffic scenario the trajectories used for calibration were from. \[Updated on 2021-07-09 13:28:21\](https://hyp.is/cMzO2ODjEeuzOyv8_QfLWg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Calling them out!
          
          ---
          
           > 
           > it is acknowledged that the above described approaches pertain more to the phase of model development than to that of credibility assessment, which substantiates in model validation \[Updated on 2021-07-09 13:30:57\](https://hyp.is/zU2JSuDjEeuFnicZAgzZdA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          interesting
          
          ---
          
           > 
           > As well as in studies about heterogeneity, a quantitative validation of models is not common in the broader field of traffic flow theory. In general, a model evaluation through synthetic experiments has been performed (often referred to as ‘numerical examples’) \[Updated on 2021-07-09 13:31:57\](https://hyp.is/8VoyNODjEeuwKqvaC8Hv8w/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Not surprising
          
          ---
          
           > 
           > Moreover, since traffic is a collective phenomenon emerging from individual vehicle movements, a quantitative assessment of the accuracy of the whole model is mandatory.  \[Updated on 2021-07-09 13:32:57\](https://hyp.is/FOjiVODkEeuFoL8NCvq7fA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          They say this, but do not provide examples of how the current methods fail
          
          ---
          
           > 
           > On the one hand, when a car-following model is calibrated for each vehicle against its own trajectory, the model is fed with a specific and immutable leader’s trajectory. Such trajectory is different from the one feeding the model in a simulation. On the other hand, a traffic simulation output is the result of the interaction of several models (i.e. car-following, lane-changing, merging, etc.). \[Updated on 2021-07-09 13:38:38\](https://hyp.is/4IoHCODkEeuQ4A_Te16OSA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Good analysis
          
          ---
          
           > 
           > When several models, for several agents, interact in a simulation environment, the error made in reproducing the macroscopic traffic pattern is different from the sum of the microscopic calibration errors (quoting Mahmassani, 2013, in traffic modelling the “sum may be less than the whole”). Thus, it is necessary to validate the model as a whole, on the observed macroscopic traffic patterns. \[Updated on 2021-07-09 13:42:44\](https://hyp.is/ctelhODlEeuQ4WMLlozylA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          No surprise here, but this explains the complex behavior of simulation
          
          ---
          
           > 
           > In fact, the validation of a stochastic model requires that all uncertainties in the modelling process are thoroughly considered. \[Updated on 2021-07-09 13:43:32\](https://hyp.is/j0yx-uDlEeuL9OfjSDR6sA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          All uncertainties??
          
          ---
          
           > 
           > In addition, a trace-driven simulation approach has been implemented to guarantee an effective validation on observed traffic data, and a fair comparison of the uncertainty models. \[Updated on 2021-07-09 13:44:14\](https://hyp.is/qNhYXuDlEeuK69eicXTQEw/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Excited to see where this goes
          
          ---
          
           > 
           > Since uncertainty in a traffic system is particularly complex – it arises from human-machine agents’ interactions modelling – and multi-faced – think of the heterogeneity and variability in time of agents’ parameters – we have brought traffic simulation into the cross-disciplinary epistemological debate about the nature of uncertainty.  \[Updated on 2021-07-09 14:00:18\](https://hyp.is/5x6tZODnEeujVaePUYOH-A/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          About time this happened
          
          ---
          
           > 
           > Accordingly, in this paper we argue that uncertainty is never an intrinsic characteristic of a system. It arises whenever an individual observes a system, or attempts to describe it through a mathematical model, either for analysis i.e. for diagnosis, or for prediction i.e. for prognosis.  \[Updated on 2021-07-09 14:17:38\](https://hyp.is/U1XGbuDqEeu2ja8gKz-sig/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          So they are saying that the actually system has no uncertainty.
          
          The uncertainty arises from trying to model the system.
          
          I don't know if that's actually true. It would see like there is inherent randomness baked into traffic always
          
          ---
          
           > 
           > Consequently, as quantitative treatment of uncertainty we intend any method aimed at reducing modelling uncertainty, that is reducing model deviations from a real system \[Updated on 2021-07-09 14:18:27\](https://hyp.is/cHLTQODqEeuQ8o-Oe5-CoQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Clearly a good goal, but how can the "real" state of the system be known?
          
          ---
          
           > 
           > In the cited scientific literature, therefore, epistemic uncertainty refers to that part of uncertainty deriving from a lack of knowledge about the system or the environment, and representing a potential inaccuracy in any phase or activity of the modelling process \[Updated on 2021-07-09 14:26:42\](https://hyp.is/l4oDRODrEeuIsee4V6kdpA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          definition of *epistemic [[uncertainty*\]\]
          
          ---
          
           > 
           > It can be reduced by collecting more data or information, increasing the measurement techniques, the model structure, the resolution method, the numerical precision, etc. Usually, it is not naturally defined in a probabilistic framework \[Updated on 2021-07-09 14:33:35\](https://hyp.is/jW-x5uDsEeu4ePNooNVXdQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          This is the type of uncertainty that we deal with typically in Mechanical Engineering
          
          ---
          
           > 
           > Aleatory uncertainty, therefore, is supposed to arise from an intrinsic randomness of a phenomenon or a system. It typically originates from a variability in space or time of a system characteristic (e.g. soil permeability) or variability within a population (e.g. heterogeneity of drivers’ characteristics1 \[Updated on 2021-07-09 14:38:58\](https://hyp.is/K3fNiODtEeuz7YflO0sPhw/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Definition of *aleatory [[uncertainty*\]\] aka *stochastic [[uncertainty*\]\]
          
          ---
          
           > 
           > Aleatory uncertainty does not respond to empirical efforts or increase in the knowledge of a system the way epistemic uncertainty does. \[Updated on 2021-07-09 14:40:03\](https://hyp.is/dPUj6ODtEeuc5BMsag-MUQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          It would seem that this describes most of traffic simulation's inputs
          
          ---
          
           > 
           > his distinction – between an uncertainty which is proper of a model and an uncertainty which is intrinsic to a system – is somewhat misleading. In fact, even when speaking of aleatory uncertainty of a system, we are not really interested in such uncertainty per se, but in its representation into a model. \[Updated on 2021-07-09 14:43:12\](https://hyp.is/5ZeE2ODtEeuFvS-iG_ocSQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          That makes sense, and I guess it explains their interpretation of https://hyp.is/U1XGbuDqEeu2ja8gKz-sig/www.sciencedirect.com/science/article/pii/S0968090X20307452
          
          ---
          
           > 
           > Shapes and parameters of the random variables distributions are initially unknown to the analyst, i.e. they are uncertain themselves. In fact, the additional uncertainty – which is epistemic in nature, because it can be reduced by estimation – arising every time aleatory uncertainty is injected in a model, has been called “uncertainty about the uncertainty” (de Rocquigny et al., 2008) or “epistemic uncertainty about the aleatory characteristics of a system” (de Rocquigny, 2012). \[Updated on 2021-07-09 14:44:24\](https://hyp.is/EBDo0ODuEeuVDhvu84K8cg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Uncertainty about uncertainty. I like that
          
          ---
          
           > 
           > connectivity of vehicles allows us to identify each individual vehicle, thus eliminating such randomness in a real time simulation \[Updated on 2021-07-09 14:46:17\](https://hyp.is/U3YlQODuEeuzWHfIZQdWxg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          This could / does eliminate the randomness. *epistemic [[uncertainty*\]\] will still prevail though
          
          ---
          
           > 
           > the rationale for an operational distinction between aleatory and epistemic uncertainty is the concept of reducibility, that is the possibility of reducing the uncertainty of model outputs. Reducibility has to be intended here as practical rather than theoretical \[Updated on 2021-07-09 14:50:55\](https://hyp.is/-VT3yuDuEeuLDu9HMIWSvw/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          There has to be a target uncertainty to reach in the outputs. I guess it is technically possible to shake out all of the epistemic uncertainty, while the aleatory uncertainty must remain 
          
          ---
          
           > 
           > Similarly, finer resolution schemes or more detailed models might require unbearable computing times, thus resulting in practically irreducible uncertainty.  \[Updated on 2021-07-09 14:52:40\](https://hyp.is/N9PcWuDvEeuEvw8ffUBetg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I would contend that finer resolutions increases uncertainty
          
          ---
          
           > 
           > Overall, the distinction between epistemic and aleatory uncertainty is critical for a proper understanding of uncertainty in a modelling process, and for choosing a suitable treatment to reduce it.  \[Updated on 2021-07-09 14:53:43\](https://hyp.is/XVPgBuDvEeu41W_elStbRQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          noted
          
          ---
          
           > 
           > In fact, the aim of a modeller is to reduce output uncertainty, but not to reduce variability, in space or time, of a modelled system.  \[Updated on 2021-07-09 14:54:17\](https://hyp.is/cYZXKuDvEeuiMC9SD9DFcQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Preach
          
          ---
          
           > 
           > The latter (i.e. aleatory uncertainty) needs to be preserved, since objective of a simulation is to provide a system representation as close as possible to the actual one. \[Updated on 2021-07-09 14:57:10\](https://hyp.is/2R0VfODvEeu42Wt-QAIHpA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I hadn't thought of this but duh! If the system has aleatory uncertainty, then so should the simulation
          
          ---
          
           > 
           > Let us assume that one aims at improving the descriptive power of a model i.e. reducing its uncertainty by replacing one of its uncertain inputs, such as a random input variable, with a detailed model able to describe this input. Unfortunately, it is not rare that the opposite effect is obtained. In fact, it is likely that the new model comes with additional uncertain parameters or inputs which may increase the original uncertainty, rather than decrease it.2 For instance, in the field of traffic simulation, the development of detailed microscopic models – in order to mimic individual behaviours and dynamics – came at the cost of increasing model output uncertainty and decreasing prediction accuracy \[Updated on 2021-07-09 14:58:44\](https://hyp.is/ESu7YuDwEeu1GjfVSwfquA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I have been saying this since the beginning!
          
          ---
          
           > 
           > traffic micro-simulation have driven research mainly towards the development of methods for calibrating and validating increasingly complex and over-parameterized models \[Updated on 2021-07-09 15:08:05\](https://hyp.is/X4hCNODxEeuwFzNKkzEQlA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          calling the industry out!
          
          ---
          
           > 
           > which also broadened the spectrum of treatments previously applied in traffic modelling to include the sensitivity analysis. \[Updated on 2021-07-09 15:13:36\](https://hyp.is/JFm0YuDyEeuQakvR5wub5A/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          This isn't really "renewed" if it started again in the 2000s while "prior" papers were written in 2019
          
          ---
          
           > 
           > The first ever empirical datasets of this type, freely available to the scientific community, enabled a corroboration of traffic models never possible before \[Updated on 2021-07-09 15:14:37\](https://hyp.is/SMkeyODyEeuRCROPgj8eow/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I was wondering if something like NGSIM existed. This basically makes a field like econometrics possible
          
          ---
          
           > 
           > This difficulty was exacerbated by the peculiarity of a traffic flow system, which is a complex multi-agent human-machine system; and it makes the treatment of its uncertainty hard and not immediately transferable from other scientific fields \[Updated on 2021-07-09 15:15:30\](https://hyp.is/aJMLdODyEeuQa3thNBZIAA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          good sentence
          
          ---
          
           > 
           > In Fig. 1 the whole flow of uncertainty in a traffic simulation model is represented according to previous discussions and definitions. \[Updated on 2021-07-09 15:17:10\](https://hyp.is/pHsEPuDyEeukvo_rtT2WxQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Great image of [uncertainty](../../../../%F0%9F%8C%B3%20Evergreen/Math/Statistics/uncertainty.md)
          
          https://ars.els-cdn.com/content/image/1-s2.0-S0968090X20307452-gr1.jpg
          
          ---
          
           > 
           > Parametric inputs basically consist of model structural parameters, e.g. the free-flow speed in a fundamental diagram or in a car-following model. They might also include the probability density function (pdf) of model parameters, or of sub-model residuals. \[Updated on 2021-07-09 15:20:37\](https://hyp.is/Hz7HyODzEeuMFHP5khQXQA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Definition of *Parametric Inputs*
          
          ---
          
           > 
           > Non-parametric inputs are all the model inputs but the parametric ones, such as the origin-destination demand flows, the road network, or the traffic control. \[Updated on 2021-07-09 15:20:59\](https://hyp.is/LIpTjuDzEeusQtO2ixHYXA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          *Non-parametric Inputs*
          
          ---
          
           > 
           > As mentioned, a distinction between the natures of uncertainties is crucial, as different natures imply different treatments. \[Updated on 2021-07-09 15:33:12\](https://hyp.is/4ZP0WuD0EeusSMNc9UJPLQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Need to take care to treat these uncertainties
          
          ---
          
           > 
           > For instance, if a traffic model is used as a whole in an estimation of parametric inputs, in a so-called full inversion problem (de Rocquigny, 2012), all other sources of uncertainty are included alongside the parametric input.  \[Updated on 2021-07-09 15:41:14\](https://hyp.is/ALSK4uD2EeuHAzee8QylhA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I don't understand this one
          
          ---
          
           > 
           > Once pdfs have been estimated, values of parameters for each agent are drawn from these pdfs during one simulation run (usually when an agent is generated). Random sampling from those pdfs relies on sequences of pseudo-random numbers that, unless explicitly specified by the analyst, are different from one run to the other. Therefore, even if a model is fed with identical inputs in two, or more, different runs, different random number sequences will yield different temporal concatenations of events, that is different outputs among runs.This output randomness among runs accounts for a not explained or explicitly modelled variability in the system, i.e. it constitutes the irreducible part of the system aleatory uncertainty. In order to represent said system irreducible uncertainty in the model outputs, the model has to be run multiple times. These multiple runs are often referred to as replications. \[Updated on 2021-07-09 15:54:22\](https://hyp.is/1m9DiOD3EeujcPMMpArp_w/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Simple explanation of uncertainty + traffic simulations
          
          ---
          
           > 
           > The widespread practice of comparing different traffic scenarios through averages of a number of scenario simulations clearly makes no sense, as it is likely to provide an incomplete or artefactual system representation. \[Updated on 2021-07-09 15:55:57\](https://hyp.is/DuyH6OD4Eeu4lSv8iSbfLg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Preach
          
          ---
          
           > 
           > For non-parametric inputs, the reducible part of uncertainty originates either from input estimation (see e.g. Antoniou et al., 2016, for a review about the OD demand estimation problem), from measurements, or from model implementation (see e.g. mistakes in building a network model). Corresponding errors are indicated as  \[Updated on 2021-07-09 15:56:44\](https://hyp.is/Kyup8uD4Eeuc_a9ohXWMkw/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          non parametric inputs
          
          ---
          
           > 
           > The uncertainty (i.e. model residuals and randomness) resulting from parametric and non-parametric inputs propagate through the model together with the model uncertainty. In model uncertainty we may have both an epistemic and an aleatory component too. The former is measured by model errors,  \[Updated on 2021-07-09 16:06:14\](https://hyp.is/fwI_LOD5EeuRGvOMZSFR7w/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Hadn't thought of this before
          
          ---
          
           > 
           > The process of repeatedly running the model allows mapping the input uncertainty in the output uncertainty. In the cross-field literature, this mapping process is usually referred to as “uncertainty propagation” \[Updated on 2021-07-10 16:21:31\](https://hyp.is/y6yURuHEEeul7nuD60Umkg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          How do we do this?
          
          ---
          
           > 
           > For non-additive models – as traffic simulation models typically are – the output uncertainty is not equal to the sum of all mentioned uncertainties. As long as these uncertainties mix in simulation, their interaction effects on output uncertainty can result even higher than their direct or first-order effects (Saltelli et al., 2008). \[Updated on 2021-07-10 16:33:51\](https://hyp.is/hPWzRuHGEeu6YpdaE3WXsg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          ^d3fa9c
          
          ---
          
           > 
           > These model errors are often hidden in the model assumptions – that is one of the main criticisms to the so-called reductionist approach of modern science. For instance, think of car-following models where multi-anticipatory behaviour of drivers is customarily neglected, though it is well-acknowledged in real driving. \[Updated on 2021-07-10 16:36:11\](https://hyp.is/2IXobuHGEeuHfFcu7Ole-g/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Calling it all out
          
          ---
          
           > 
           > Regardless data quality and quantity, the estimation will return different values from the true unknown  \[Updated on 2021-07-10 16:40:37\](https://hyp.is/dwibqOHHEeuEyYN8CP9p6g/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          So because the model is not actually a "true" model, as there are "unmodelled" factors -> minimizing the output error will not actually result in converging on the correct values of the parameters, but instead values that compensate for the missing factors in the model
          
          ---
          
           > 
           > In fact, such directly estimated parameters would not compensate for the model misspecification. This is the reason why parameters should not be directly estimated even when they have a physical meaning \[Updated on 2021-07-10 16:41:42\](https://hyp.is/ne8L0OHHEeu6Y6cnEe7jNQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          ^5as266
          
          Did not think that this would be the take here
          
          ---
          
           > 
           > For instance, in Hoogendoorn et al. (2013), it is referred that after the introduction of a variable speed limit system (VSL) in the Netherlands, traffic congestion increased in a way unpredicted by models. In fact, driver compliance to speed limits, which determines the efficacy of speed enforcement policies (e.g. Cascetta et al., 2011, Montella et al., 2015), was not modelled at all (that is making a model error similar to that in Eq. (2)) \[Updated on 2021-07-10 17:26:13\](https://hyp.is/1ZUHluHNEeuS9rf2SOG5og/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Example of the failures of *Traffic Simulation*
          
          ---
          
           > 
           > In other words, the uncertainty due to model errors is incorporated into the inputs uncertainty \[Updated on 2021-07-10 17:28:47\](https://hyp.is/gUGWdOHHEeuEyn9KljqbrA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          See above.
          
          This is called error compensation
          
          ---
          
           > 
           > As a result, it is impossible to distinguish the share of the output uncertainty individually caused by each sub-model. For example, if route-choice parameters are calibrated using aggregate data by running a whole traffic simulation model, their estimation also compensate the errors of sub-models, like car-following or lane-changing \[Updated on 2021-07-10 17:47:43\](https://hyp.is/1uOyhOHQEeuwMVfj1d6ZiA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Similar to what we we did
          
          ---
          
           > 
           > For instance, compensation arises in the estimation of sub-models parameters. Ideally, sub-models should be separately estimated by using independent disaggregate data (see Toledo et al., 2003). \[Updated on 2021-07-10 17:47:49\](https://hyp.is/2gC3vuHQEeuM4Yf-SFgzGw/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          How do you find independent, dis aggregate data?
          
          ---
          
           > 
           > As this model error was hidden, it was compensated by the model calibration in the ‘before’ scenario. Therefore, when models were asked to predict future behaviour, they showed incapable of capturing the impact on traffic of a change in the compliance to VSL, i.e. resulting in scarce traffic predictions. \[Updated on 2021-07-10 17:48:26\](https://hyp.is/8C0CruHQEeuSRack8ObmBQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          works in back-test, not in the future. Aka unable to look into the future if one of the hidden parameters changes 
          
          ---
          
           > 
           > Therefore, if one replaced one of these sub-models (e.g. automated driving algorithms in place of car-following models) the previously estimated route choice parameters would become sub-optimal. That is the reason why error compensation lowers prediction capabilities of models. \[Updated on 2021-07-10 17:52:25\](https://hyp.is/frjcFOHREeuS_bve8SZB3w/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Changing one of the parameters more greatly affects the output than it should? Because the other parameters may hide some of the affects of the parameter that you desire to change
          
          ---
          
           > 
           > For instance, if one calibrates car-following and lane-changing parameters of all agents at once i.e. against aggregate data, by running the whole traffic simulation model, the resulting fitting might be better than that obtained by separately calibrating each individual agent i.e. against its and neighbours’ trajectories. In fact, by calibrating different agents' models as a whole, the uncertainty due to agents’ interactions in simulation is also taken into account. This result is somewhat counterintuitive, as one might expect that a one-by-one calibration against detailed trajectories is the best achievable one. \[Updated on 2021-07-10 18:00:33\](https://hyp.is/oZJeROHSEeueu_sGANbJcQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I'm surprised that they didn't cite research here 
          
          ---
          
           > 
           > might be unsuitable to simulate a scenario where the O/D demand is substantially different from that used for the estimation. \[Updated on 2021-07-10 18:02:34\](https://hyp.is/6YHjeOHSEeulFBP7ncqNJA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          This makes sense
          
          ---
          
           > 
           > it is also clear that error compensation hinders the transferability of estimated parameters. \[Updated on 2021-07-10 18:03:26\](https://hyp.is/COmAQOHTEeuIx8_7KVNFvg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          So what works for one set of inputs will not work for drastically different inputs
          
          ---
          
           > 
           > Another mechanism affecting model performance and parameters transferability is overfitting. It arises when the number of model parameters is particularly high relative to the number of observations used for their estimation. It may arise also when the model is estimated against an incomplete or biased sample of observations \[Updated on 2021-07-10 18:11:55\](https://hyp.is/MY7pMOHUEeulFVsPHVOeMg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Definition of over fitting in traffic simulation
          
          ---
          
           > 
           > In Punzo et al. (2015), for instance, through a quasi-Monte Carlo analysis carried out over the complete set of trajectories in one of the I80 NGSIM dataset, it is shown that the shorter the trajectory duration the higher the probability of overfitting a car-following model. \[Updated on 2021-07-10 18:13:39\](https://hyp.is/dl9LBOHUEeuW7weZZ9kozQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Overfitting example
          
          ---
          
           > 
           > when the number of parameters is disproportionate relative to that of observations, the estimated model tends to describe the random fluctuations in the data rather than the general dynamics of the modelled system (i.e. the trend). \[Updated on 2021-07-10 18:17:04\](https://hyp.is/8IcPrOHUEeu1zn_zIzVRkA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Citation material
          
          ---
          
           > 
           > . A model output error on the validation set, which is much higher than that on the estimation set,  \[Updated on 2021-07-10 18:18:52\](https://hyp.is/MNYqZuHVEeuN-TcZ54-Rmg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          is a clear symptom of overfitting or error compensation (for an example of cross-validation on car-following model estimation see e.g. Punzo and Simonelli, 2005).
          
          ---
          
           > 
           > Though apparently obvious, the requirement has non-trivial implications, as it calls for a structured process of identification, quantification and reduction of the model uncertainty (de Rocquigny et al. 2008). The ensemble of these steps is often referred to as management of uncertainty or uncertainty treatment of a modelling process. \[Updated on 2021-07-10 18:25:35\](https://hyp.is/IOcU6OHWEeu6e4-wuNpreQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          good sentence. citation material
          
          ---
          
           > 
           > The first step (step A in the figure) consists in the problem specification, which involves the definition of the input and the output variables, the model specification and the identification of the quantities of interest for measuring the uncertainty in the outputs. Input variables may be uncertain or fixed, this mainly being the analyst choice. Establishing what variables are considered uncertain or fixed is crucial for the meaningfulness of the results.For instance, imagine that the impact on traffic of connected and automated vehicles is to be evaluated through simulation. A safe assumption should be that of considering e.g. the reaction time of automated vehicles as uncertain, and not fixed at a single (often optimistic) value. In fact, considering the reaction time as fixed would produce two main undesirable outcomes. First, if the fixed value was wrong, results would be biased. Second, by fixing a specific value, it would not be possible to understand the impact on results if that value changed, and what the interaction effects are, when other variables contemporarily vary. \[Updated on 2021-07-10 18:42:21\](https://hyp.is/gGYEtOHXEeu-lG90V7FkzQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          example of picking the parameters
          
          ---
          
           > 
           > The second step (step B) is the quantification of the uncertainty sources (modelling of the input uncertainty) often referred to as input estimation, or calibration or, more generally, data assimilation. This is the step traffic scientific literature has mainly focused on. In a probabilistic setting this phase implies the definition of an uncertainty model of inputs, i.e. the joint pdf of the uncertain inputs, or their marginal pdfs with simplified correlation structures or even independence assumptions. It involves gathering information via direct observations, expert judgements, physical arguments or indirect estimation and it is often the most expensive phase of the analysis. In the previous example, the reaction time of automated vehicles might be simply assumed to vary over a ‘reasonable’ range of values. \[Updated on 2021-07-10 18:44:02\](https://hyp.is/tNnc4uHYEeuW-u9GZ48rpg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          This is a time consuming step, but should be well documented 
          
          ---
          
           > 
           > As mentioned, a Monte Carlo simulation framework is often adopted to this aim. The model is repeatedly run with parametric, non-parametric inputs, models and other uncertain factors being sampled from their pdfs or ranges. The sampling is designed to produce a full coverage of the multi-dimensional input space, in order to capture the impact on the outputs of the contemporary variation of all uncertain inputs/factors and models. \[Updated on 2021-07-10 18:56:38\](https://hyp.is/dxJ9XuHaEeuW_bta9aR90w/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I need to develop framework for doing this
          
          ---
          
           > 
           > Low discrepancy sequences of numbers also known as quasi-Monte Carlo or Sobol’s sequences, are proved to be the most effective sampling scheme available (i.e. in comparison to grids, pseudo-random, Latin Hypercube or other sequences as Halton, see Saltelli et al., 2008). \[Updated on 2021-07-10 18:59:17\](https://hyp.is/1fEP3uHaEeuGk0dnvZku_Q/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I need to research these methods
          
          ---
          
           > 
           > Once the uncertainty in the inputs has been propagated in the outputs through the model, outputs uncertainty can be quantified by means of pdf or relevant quantities such as percentiles (Step D: uncertainty quantification) \[Updated on 2021-07-10 19:02:25\](https://hyp.is/Resy9uHbEeuI0Rf6eKmm0w/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          How does this actually work?
          
          ---
          
           > 
           > In fact, the main objective of system modelling is that of reproducing the observed phenomenon with the same degree of variability of a real system. For instance, in a given application, a traffic model will be considered valid for the scope of the analysis if the cdf of an output, which was obtained from several model runs, is statistically equivalent to the cdf resulting from multi-day observations of that system output. \[Updated on 2021-07-10 19:04:49\](https://hyp.is/m7_XGOHbEeuyBy_lfEDXsg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I get that this is actually the goal, but when you have just one data source how do you actually verify that the output is close to anything but the one output
          
          ---
          
           > 
           > Such feedback is commonly referred to as sensitivity analysis (step E). It allows the analyst to apportion the output variance (which is a proxy of the output uncertainty) to each of the input factors. Inputs that are responsible for a negligible aliquot of this variance can be therefore considered as fixed in subsequent simulations and analyses, thus reducing the problem complexity (this is referred to as a “factor fixing” setting of sensitivity analysis). Examples in traffic micro-simulation can be found in Ciuffo et al., 2013, Ciuffo et al., 2014), Punzo et al., 2015, Vieira da Rocha et al., 2015, where sensitivity analysis was applied to reduce the number of parameters to calibrate. \[Updated on 2021-07-10 19:06:42\](https://hyp.is/35WAZOHbEeuLf_fS_nsHeQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          I need to read the listed paper's here
          
          ---
          
           > 
           > If a thorough estimation of the input pdfs is not achievable e.g. due to scarce information, the uncertainty arising from this lack of knowledge too has to be considered in the simulation process. Therefore, when propagating the uncertainty, also the pdf parameters or the pdf shape need to be sampled. This leads to a so-called two-level probabilistic approach: at an outer level, the parameters of the input pdfs, or even their shape, are sampled from hypothesized ranges or set of shapes. At an inner level, for each pdf being sampled, a number of simulations are run by sampling values from such input pdf \[Updated on 2021-07-10 19:11:48\](https://hyp.is/lYQhCuHcEeumFMubyDWvbg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          This is where I will mostly fall
          
          ---
          
           > 
           > The outer level, on the other hand, takes into account the lack of knowledge by the analyst on the probabilistic model of inputs, i.e. the reducible part of the uncertainty, and it is thus referred to as “epistemic sampling”. For instance, if some model parameters have been calibrated but the context of the current application is different from that of the calibration, one might consider the calibrated parameters as uncertain (e.g. distributed around the calibrated values), though they have already been calibrated. \[Updated on 2021-07-10 19:14:47\](https://hyp.is/3OknPuHcEeuuLItvDyiKmw/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          "In this way, resulting outputs would be less precise, but more likely not inaccurate (that is the spirit of the “epistemic sampling”, i.e. to consider the unknown as uncertain)."
          
          ---
          
           > 
           > As each aleatory sampling yields a cdf for the chosen output, the epistemic sampling yields a distribution of cdfs. These cdfs were referred to as complimentary cdfs (CCDF) by Helton (1994), who first introduced a two-level approach to deal with the aleatory and epistemic uncertainty in a probabilistic framework \[Updated on 2021-07-10 19:17:38\](https://hyp.is/ZoOlyOHdEeunzO_V9I0oSQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Good history of the two-level approach 
          
          possible citation
          
          ---
          
           > 
           > Computational complexity and arbitrariness of second-level assumptions, which can potentially lead to introduce more levels, are the main drawbacks of a two-level probabilistic approach. Alternative approaches to the treatment of the epistemic component of aleatory uncertainty have been proposed, such as interval analysis, possibility theory, or evidence theory (see Helton and Oberkampf, 2004, for a review). \[Updated on 2021-07-10 19:18:17\](https://hyp.is/fYUliuHdEeu4h0OsxcYkJA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          The counter to the second-level approach
          
          ---
          
           > 
           > The clear trade-off between the level of knowledge/ignorance about the inputs and the attainable precision in the outputs can be stated as follows: the lower the knowledge of the inputs, the higher the uncertainty in the outputs. Trusting “precisely wrong” results is a very common mistake in traffic simulation. \[Updated on 2021-07-10 19:23:36\](https://hyp.is/O3LxTuHeEeu1Yoe3EN7n1A/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          So glad that this was addressed by the authors
          
          ---
          
           > 
           > As the gaussian copula preserves both the shape and the correlation structure of the calibrated parameters sets, it is expected to be the best-fitting model (see e.g. Rafati Fard and Shariat Mohaymany, 2019). \[Updated on 2021-07-10 19:51:28\](https://hyp.is/IBo6_OHiEeu6kyOcki5Okg/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Read this to understand the copula's
          
          ---
          
           > 
           > Otherwise, new technologies such e.g. CACC, which are developed to meet microscopic requirements (see e.g. string stability), would not be validated at a macroscopic level. In other words, we would remain unaware of their actual impact on traffic flows (see e.g. congestion dynamics and capacity). \[Updated on 2021-07-10 19:58:14\](https://hyp.is/EobPsuHjEeukFFNQEoR8kA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          citation material
          
          ---
          
           > 
           > Consistently with the previous interpretation, the two uncorrelated pdfs (i.e. ‘empirical marginal’ and ‘uniform marginal’) perform better in the uncongested scenario than in the congested ones, relative to the gaussian copula. In the least congested traffic scenario, where the simulated traffic dynamics are the farthest from those of calibration, considering parameter correlation is disadvantageous. In fact, it is like applying an overfitted model. Conversely, when congestion arises, and the degree of freedom of simulation decreases, considering correlation lowers the simulation error; see the I80-3 diagram, in which the gaussian copula cdf is the best cdf by far. \[Updated on 2021-07-10 19:58:38\](https://hyp.is/IFSUEuHjEeuSZO8wPeRyLQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Summary of the results
          
          ---
          
           > 
           > It is worth noting here that, we have calibrated sub-models on trajectories; conversely to previous studies (see e.g. Punzo and Simonelli, 2005, Kim and Mahmassani, 2011), however, we have validated the ensemble of these models in traffic simulations. That is, we have validated models on the traffic patterns resulting from a thorough micro-simulation of the observed traffic scenarios (where vehicle dynamics were free to evolve, as vehicle sub-models were not fed with known and immutable trajectories, like in calibration). \[Updated on 2021-07-10 20:00:21\](https://hyp.is/XdbzUuHjEeuLk8-b2gMgVQ/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          How was this not done before?
          
          ---
          
           > 
           > n fact, simulations with homogeneous parameters have returned the highest errors, by one order of magnitude, whatever the congestion level. \[Updated on 2021-07-10 20:01:02\](https://hyp.is/dobQ3uHjEeuLlN-D67X9ew/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          Key conclusion here
          
          ---
          
           > 
           > normal distributions represent the only heterogeneous uncertainty model to return errors in the same magnitude of homogeneous simulations. Inability to correctly propagate traffic congestion has been pointed out as a likely motivation for such poor performances (note that normal distributions are the ones customarily adopted in commercial micro-simulation software). \[Updated on 2021-07-10 20:01:50\](https://hyp.is/kxbpWuHjEeu-qePS6Qtkow/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          So don't use normal distributions?
          
          ---
          
           > 
           > Instead, the gaussian copula, which takes into consideration also the correlation of parameters, has performed better in the most congested scenario, where it has turned out to be the best input uncertainty model among all scenarios. In fact, in the most congested scenario, vehicle dynamics resulting from simulation are closer to those in calibration, as compared to what happens in the other two scenarios. This result suggests that considering parameters correlation potentially leads to model overfitting. \[Updated on 2021-07-10 20:03:10\](https://hyp.is/wnJIcOHjEeu1cYPqWmhSkA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          So when each vehicle is fit to a car fitting model, the error is greater than when selected from a copula
          
          ---
          
          ---
          
          ## doc_type: hypothesis-highlights
          url: 'https://www.sciencedirect.com/science/article/pii/S0968090X20307452'
          
          # A two-level probabilistic approach for validation of stochastic traffic simulations: impact of drivers’ heterogeneity models
          
          ## Metadata
          
          * Author: [sciencedirect.com]()
          * Title: A two-level probabilistic approach for validation of stochastic traffic simulations: impact of drivers’ heterogeneity models
          * Reference: https://www.sciencedirect.com/science/article/pii/S0968090X20307452
          * Category: #article
          ## Highlights
          
           > 
           > A complementary approach has been that of assuming different parameters among the agents. By analysing two sets of empirical vehicle trajectories, Ossen and Hoogendoorn (2011) showed that: i) a heterogeneity of “driving styles” among the agents does exist – i.e. each driver’s behaviour is best represented by a specific car-following model – and ii) within a group of drivers who are best described by a specific car-following model – i.e. having the same driving style – a heterogeneity of model parameters does exist. \[Updated on 2022-05-25 09:57:05\](https://hyp.is/8YMW7Nw6EeyG7q_csm_Wow/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          No duh, but this validates the point of using a distribution and not a single value
          
          ---
          
           > 
           > Moreover, since traffic is a collective phenomenon emerging from individual vehicle movements, a quantitative assessment of the accuracy of the whole model is mandatory.  \[Updated on 2022-05-25 10:01:15\](https://hyp.is/FOjiVODkEeuFoL8NCvq7fA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          They say this, but do not provide examples of how the current methods fail.
          
          Model referenced here is the complete simulation model, not a sign car following model
          
          ---
          
           > 
           > Eventually, independent uniform distributions proved to be the most robust input uncertainty model, i.e. the model performing in a consistent way throughout all congestion levels \[Updated on 2022-05-25 10:18:43\](https://hyp.is/9sQejNw9Eeyz28_xJhe3BA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          So can I use this as justification for the choice of using uniform distributions
          
          ---
          
           > 
           > That framework allows us to include all uncertainties of the modelling process and to obtain robust outputs form traffic simulations. For instance, if a model validated in the previous sections had to be used for traffic predictions over the same stretch (e.g. to predict queue lengths over a freeway), one could perform simulations including an epistemic sampling of three uncertainty models (the three leftmost cdfs in Fig. 7). More in general, the proposed validation framework should be applied prior to any daily use of traffic simulation models, in order to identify the uncertainty models to extend an epistemic sampling to. \[Updated on 2022-05-25 10:19:30\](https://hyp.is/ExqHxNw-Eeyt1TeJ28a7oA/www.sciencedirect.com/science/article/pii/S0968090X20307452 
          
          This framework could be included in my paper
          
          ---

### Deceleration

From [Definition of Vehicles, Vehicle Types, and Routes - SUMO Documentation](https://sumo.dlr.de/docs/Definition_of_Vehicles%2C_Vehicle_Types%2C_and_Routes.html#car-following_model_parameters):

 > 
 > The deceleration ability of vehicles of this type (in m/s^2)

SA shows that this parameter is not important in overall fuel consumption

#### Bound Selection

* [Exploring the variance contributions of correlated model parameters A sampling-based approach and its application in traffic simulation models](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Exploring%20the%20variance%20contributions%20of%20correlated%20model%20parameters%20A%20sampling-based%20approach%20and%20its%20application%20in%20traffic%20simulation%20models.md)
  * [DOI](https://doi.org/10.1016/j.apm.2021.04.012)
  * Range::  `[0.05, 8]`
  * Shape::  log-normal
    * $\mu = 2.225$ , $\sigma = 1.849$
* [Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Does%20traffic-related%20calibration%20of%20car-following%20models%20provide%20accurate%20estimations%20of%20vehicle%20emissions.md)
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

* [Exploring the variance contributions of correlated model parameters A sampling-based approach and its application in traffic simulation models](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Exploring%20the%20variance%20contributions%20of%20correlated%20model%20parameters%20A%20sampling-based%20approach%20and%20its%20application%20in%20traffic%20simulation%20models.md)
  * [DOI](https://doi.org/10.1016/j.apm.2021.04.012)
  * Range::  `[0.05, 5]`
  * Shape::  log-normal
    * $\mu = 2.172$ , $\sigma = 1.152$
* [Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Does%20traffic-related%20calibration%20of%20car-following%20models%20provide%20accurate%20estimations%20of%20vehicle%20emissions.md)
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

* [Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Does%20traffic-related%20calibration%20of%20car-following%20models%20provide%20accurate%20estimations%20of%20vehicle%20emissions.md)
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

I am testing this as [Does traffic-related calibration of car-following models provide accurate estimations of vehicle emissions](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Does%20traffic-related%20calibration%20of%20car-following%20models%20provide%20accurate%20estimations%20of%20vehicle%20emissions.md) finds that the apparent deceleration of the leader vehicle is the 3rd most sensitive parameter.

I don’t actually know how the radar (or camera) based calibration would be able to calculate the “true” value for this parameter, as it is based entirely in driver psychology.

I investigated the affect in `Distro_Width+Random_Seed+Apparent_Decel+Sim_Step+Emissions_Device/06.06.2022_10.34.19`. It is `0` meaning that the IDM car-following model doesn’t consider it at all. It will be avoided in future sensitivity analysis as of *2022-06-06*

#### Bound Selection:

This is the same as [Deceleration](Sobol%20Sensitivity%20Analysis%20Parameters.md#deceleration)

### Startup Delay

Jakob Erdmann suggested including this parameter. It basically models the reaction time to green traffic light. The problem is that in it’s current iteration, a vehicle has the same reaction time at every stopping event. This leads to very unrealistic traffic when the startup delay is high.

I have raised this issue in GitHub. Hopefully it is fixed so that we can implement it in the [Sensitivity Analysis](../../../../%F0%9F%8C%B3%20Evergreen/Engineering/Sensitivity%20Analysis.md)

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

As discussed with [Dr. Bittle](../../../../%F0%9F%93%9A%20Library/%F0%9F%91%A8%E2%80%8D%F0%9F%91%A9%E2%80%8D%F0%9F%91%A6%E2%80%8D%F0%9F%91%A6%20People/Dr.%20Bittle.md), the goal of including the [NEMA dual ring](../../../../%F0%9F%8C%B3%20Evergreen/Engineering/NEMA%20dual%20ring.md) behavior in the [Sobol Sensitivity Analysis](../../../../Sobol%20Sensitivity%20Analysis.md) would be to:

1. Validate that the time put into *Building a NEMA Controller in SUMO* and the *2022 SUMO Conference Paper* was worth it.
1. Emphasize that this paper is a sensitivity analysis of a signalized corridor, and thus contributes new findings to the *Traffic Simulation* space.
   1. I can’t find any papers where traffic signal behavior was included in a sensitivity analysis.
      1. Caveat - there are many papers that document the influence that *Traffic Light* control has on emissions and fuel consumption.
         1. [Full article: Evaluating the impacts of urban corridor traffic signal optimization on vehicle emissions and fuel consumption](https://www.tandfonline.com/doi/full/10.1080/03081060.2011.651877)

I also see a couple arguments against including the traffic signal behavior in the sensitivity analysis:

1. The goal of many *Traffic Simulation*s is to optimize the traffic signal behavior, thus it is changed from run to run. It’s impact on traffic behavior is understood and expected.
   1. Counter to this is the generation of “baselines”, i.e. a strong model of how the current lights operate. This is absent in many of the traffic signal optimization papers.
1. Most traffic simulation software has the capability to emulate the traffic signal behavior exactly.

Per discussion with [Dr. Bittle](../../../../%F0%9F%93%9A%20Library/%F0%9F%91%A8%E2%80%8D%F0%9F%91%A9%E2%80%8D%F0%9F%91%A6%E2%80%8D%F0%9F%91%A6%20People/Dr.%20Bittle.md) on *2022-06-08*, the [Traffic Light Parameters](Sobol%20Sensitivity%20Analysis%20Parameters.md#traffic-light-parameters) will be left out of the sensitivity analysis.

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

SUMO simulations use the same random seed for every simulation run unless it is explicitly set by the user.  Per [An Exploratory Study of Two Efficient Approaches for the Sensitivity Analysis of Computationally Expensive Traffic Simulation Models](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/An%20Exploratory%20Study%20of%20Two%20Efficient%20Approaches%20for%20the%20Sensitivity%20Analysis%20of%20Computationally%20Expensive%20Traffic%20Simulation%20Models.md), I included the random seed itself into the SUMO model.  They do not give an explanation for their inclusion, but perhaps it provides a good benchmark. Anything less than the inherent randomness should definitely not be considered as an important parameter.

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
  * ![Pasted image 20220606210614.png](../../../../Pasted%20image%2020220606210614.png)
  * Based on this finding and the non-linear aspect of estimator variance, **I still need to use the full output** for the [Sensitivity Analysis](../../../../%F0%9F%8C%B3%20Evergreen/Engineering/Sensitivity%20Analysis.md). This also partly due to the fact that the standard deviation is non-linear. I think that using a “sample estimator” of the population could skew the sensitivity analysis results.

## Questions

### Mathematical Questions

#### How Do the Bounds Influence the Sensitivity Analysis?

I am observing that when a sensitivity analysis is started with unrealistic parameter bounds, the outliers (interplay of a couple variables) influence the Sobol indicies. Re-doing the sensitivity analysis with a more realistic range seems to lead to different results.

Prior papers used very wide bounds on their sensitivity analyses (see [Acceleration](Sobol%20Sensitivity%20Analysis%20Parameters.md#acceleration), [Tau](Sobol%20Sensitivity%20Analysis%20Parameters.md#tau)). When I run simulations with the parameters near these upper bounds, the traffic flow is visually unrealistic and calibration is more likely to fail (see [^951963](Sobol%20Sensitivity%20Analysis%20Parameters.md#951963)).

I wonder two things here:

1. How do outliers influence the [Sobol Sensitivity Analysis](../../../../Sobol%20Sensitivity%20Analysis.md) ? Are there prior works on the setting of “realistic” bounds for the parametric inputs to the Sensitivity Analysis?
1. Is this an artifact of the simulation software used. If so, can I write about this observation?

#### Continuous Vs. Discrete Inputs?

Per discussion with [Dr. Bittle](../../../../%F0%9F%93%9A%20Library/%F0%9F%91%A8%E2%80%8D%F0%9F%91%A9%E2%80%8D%F0%9F%91%A6%E2%80%8D%F0%9F%91%A6%20People/Dr.%20Bittle.md), I will continue as-if this a non-topic, as SALib users frequently consider discrete inputs. We can dig deeper into the implication if it raised as an issue in review.

#### Correlated Inputs?

See [Exploring the variance contributions of correlated model parameters A sampling-based approach and its application in traffic simulation models](../../../../%F0%9F%93%9A%20Library/%F0%9F%93%9C%20Articles/Exploring%20the%20variance%20contributions%20of%20correlated%20model%20parameters%20A%20sampling-based%20approach%20and%20its%20application%20in%20traffic%20simulation%20models.md) for an explanation. The traditional [Sobol Sensitivity Analysis](../../../../Sobol%20Sensitivity%20Analysis.md) assumes that the inputs are independent.

To account for this, I could potentially use the High Dimensional Model Representation method [Concise API Reference — SALib 1.4.6b0.post1.dev20+gd3c9348.d20220605 documentation](https://salib.readthedocs.io/en/latest/api.html#high-dimensional-model-representation)

* A benefit is that this also generates a simplified model that can be used
* It can also be ran on the same data that [Sobol Sensitivity Analysis](../../../../Sobol%20Sensitivity%20Analysis.md) requires. From now on I will attempt to do both analyses on the data

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

## Consolidated Questions for [Dr. Bittle](../../../../%F0%9F%93%9A%20Library/%F0%9F%91%A8%E2%80%8D%F0%9F%91%A9%E2%80%8D%F0%9F%91%A6%E2%80%8D%F0%9F%91%A6%20People/Dr.%20Bittle.md)

1. \[Should I analyze fuel consumption dynamics\]([Include Fuel Consumption Dynamics](Sobol%20Sensitivity%20Analysis%20Parameters.md#include-fuel-consumption-dynamics))?
1. \[Does it make sense to consider more intra-fleet distributions than just uniform\]([Intra-fleet Parameter Distribution](Sobol%20Sensitivity%20Analysis%20Parameters.md#intra-fleet-parameter-distribution))?
1. \[Should I separate out the car and truck car-following parameters\]([Class-8 Truck](Sobol%20Sensitivity%20Analysis%20Parameters.md#class-8-truck))?
1. Any other thoughts on above?
