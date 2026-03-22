# Modeling Partially Observed Nonlinear Dynamical Systems and Efficient Data Assimilation via Discrete-Time Conditional Gaussian Koopman Network

## TL;DR
Discrete-time CGKN unifies scientific machine learning and data assimilation via analytical posterior formulas for efficient state forecast and DA.

## Research Question
How can Koopman embedding discover latent representations for unobserved system states while enabling efficient data assimilation?

## Main Contributions
1. Develops discrete-time CGKN learning surrogate models for efficient state forecast and data assimilation
2. Exploits Koopman embedding to discover latent representation where dynamics are conditional linear
3. Analytical DA formulas enable incorporation of DA performance into learning process

## Method
Discrete-time conditional Gaussian Koopman Network uses Koopman embedding to discover proper latent representation of unobserved states. Dynamics become conditional linear given observed states, forming conditional Gaussian system. Posterior distribution of latent states is Gaussian and can be evaluated via analytical formulae. Framework unifies SciML and data assimilation. Applied to viscous Burgers equation, Kuramoto-Sivashinsky equation, and 2D Navier-Stokes equations.

## Datasets
- Viscous Burgers equation
- Kuramoto-Sivashinsky equation
- 2D Navier-Stokes equations

## Core Results
- Comparable performance to state-of-the-art SciML methods in state forecast
- Efficient and accurate DA results via analytical formulas
- Unified framework for SciML and data assimilation

## Limitations
- Validated primarily on canonical PDE problems
- Performance depends on quality of Koopman embedding
- May require adaptation for real-world complex systems

## Research Gaps
- Application to real ocean and atmospheric observations
- Extension to more complex turbulent flows
- Integration with operational forecasting systems