A gym environment class has four main functions

The FIRST function is the initialization function of the class
* Takes no additional parameters

The SECOND function is the step function
* Takes in the ACTION variable
* Returns the NEXT state, the REWARD,
       a BOOLEAN representing whether the current episode of our model is done
       and some additional info on our problem.

The OTHER functions are reset, which resets the state
and other variables of the environment to the start state and render,
which gives out relevant information about the behavior of our environment so far.
