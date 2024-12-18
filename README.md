# notsosmartthings
an attempt at modifying the HA core smartthings integration almost guaranteed not to work.

# summary
i made an attempt to start my own fork of the smartthings home assistant integration. its a work in progress and i am not very good at python or home assistant thats why no guarantees. 

i deviced nit to copy any of the other forks to keep it a bit fresh and clean, plus i got lost too much in the code to make it work for myself.

# features
- up to date with latest state of ha core integration
- Supports following entities more than core:
    - Number
- supports components of devices for the following Entity types:
    - sensor
    - number
    - binary_sensor
    - light
    switch
- supports disabled components
- supports disabled capabilities of components (sensor only, others to follow)

# credits
- @elad-bar for his never merged patch to ha core adding support for components. i blatantly copied that code and modified it a bit to get components to work.

# install
easiest is to use hacs, just add the repo and go. i havent figured out versions yet so it doesnt have any.
