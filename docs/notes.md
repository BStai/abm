
## 2023-02-11
A different model - one that looks at rate of change in rates/costs in the two sided marketplace

single agent type: load in ccode wcode pairs
can have new agents - can have some disappear

at each tick an agent rolls for load or no load
if load pick the rate from a distribution  - same or different. then if different higher and lower with some probability and picking from a distribution
then find a cost. 
with some probability the previous cost.
otherwise based on some function of the rate a different cost

mark down file average, load count

the cost and rate functions should pull from some 'market' change
how do you do that? 
global?


## 2023-01-15

Next investigations
- Collect data on 'lanes'
- collect data on geographic location of carriers
- Non-uniform distribution of lanes


Implementing money will be tricky
- add priority sorting for carriers 
    - right now they take random loads in their search 
    - Have them take the largest rate <-  this would be the easiest thing to try first
        then would want to measure the average rate by number of rolls
- add a mechanic of auto incrementing the rate for every day rolled 

I want to eventually get an idea of how much a tender rejection costs us vs taking a negative
That's ultimately about the stream of loads vs the individual load.
steam of loads = probability of future loads @ rate
rejecting a load decreases the probability of getting the next load - by how much


## 2023-01-09

Put together EDA on exp1 runs. Got some nice plots vs ratio of carriers to shippers.

## 2023-01-08

fix the dependency injection - combine the experiment runner with the model code

## 2023-01-02

Done:
- Set up some project management cruft
    - got a docker image started to jumpstart the env
    - got running locally vs colab
    - ok writing some config util functions took waaaaay too long
    - reformated things with an experiment runner and config class
    - extracted constants to the config class

To do:

~Need to figure out my experiment structure~

Decide to go down Julia path?
- Pros:
    - Julia should be faster for this. 
    The greater up front investment of getting those scripts figured out should lead to higher iteration time on experiments with the agents.
    - Learn something new

- Cons:
    - Up front time may be larger than I expect

How should I think about a capital investment?

What's my time budget
- This is a side project so I won't have a large one
- But I also don't have any deadlines

I can run different python simulations while digging into the Julia stuff to optimize my time budget
Which means I should do a little more set up on outputs in the python structure.

Experiment structure:
- Write the code with feature flags wherever possible? Also have version tags
- have a json config file of feature flags

Configuration: json/dicts
run name

Ok so I got things roughly formatted in a configurable way.
What should be my first experiments? Probably need to add to the data collection a bit

- Figure out the way distributions change with differing ratios of shipper to carrier to spaces

- agent metrics?
    - avg distance (eventually)
    - number of loads
    - individual carrier status so can get % of time deadheading etc


First experiment set
Keep area fixed
Grid search carrier and shipper ratios



