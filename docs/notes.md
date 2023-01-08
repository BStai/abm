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

