First pass at using salt to manage LXC containers via Remote Execution
(RemEx). 

Exposes functions to create, start, stop, delete, and get information on
given containers. You can also get a list of containers on the minion as
well as lsit of containered processes globally and per-container. Needs
quite a bit of work, does minimal santity checking on inputs.
