# Experiements with TraceRoute

Just some experiements with using ICMP packets to probe and map packet routing across the network. Provided within this repository is the follow playing:

* `traceroute.py` - module implementing the standard networking "ping" and "traceroute" commands
* `agent.py` - A simple API service intended to allow the remote execution of ping/traceroute commands

## Getting started
The python package dependencies for all modules within this repository is provided within `requirements.txt` which shoule be installed into your python envionment.

```bash
pip install -r requirements.txt
```

Test ping and traceroute actions can be simply performed by modifying the actions at the end of the ``traceroute.py` script to perform the ping() or traceroute() desired and executing:

```bash
python traceroute.py
```

_Note: This must be executed as a privledged user to work. On a Linux/MacOS operating system it will generally be by the root user, for Windows it will require Administrator privledges. Although I have never tried it on Windows so that will be your own adventure._

## The Theory Behind TraceRoute
Need add this....

## TraceRoute Python Module

A python module `traceroute.py` is provided that implements the function of the standard network tools _ping_ and _traceroute_.

More details on how these modules work are provided within the module docstrings.

### Usage
The `ping()` function within the module is defined as:

```python
def ping(
        endpoint: str,
        port: int = 33434,
        ttl: int = 30,
        timeout: float = 3,
        packets: int = 3,       
    ) -> dict:
```

The parameters provided to the `ping()` function are:
* `endpoint` - Target network address or hostname to route the UDP packets too
* `port` - Port to assign to the UDP packets, standard port is 33434
* `ttl` - The Time To Live for UDP packets sent
* `timeout` - Time to wait for ICMP response in seconds
* `packets` - Number of UCP packets to send

The returned dictionary structure is:

```
{
    source:  Source network interface
    target:  Target destination IP address
    dest:    Destination address from ICMP
    ttl:     Set Time To Live
    packets: Number of packets issued in the ping
    ping_time: [
        {
            attempt: Sequence counter of the ping
            address: Network address returned by the ICMP
            time:    Latency time in milliseconds
            type:    ICMP packet type
            code:    ICMP packed code
        }
    ]
}
```

The `traceroute()` function within the module is defined as:

```python
def traceroute(
        endpoint: str,
        port: int = 33434,
        max_ttl: int = 30,
        timeout: int = 3,
        packets: int = 3,  
    ) -> dict:
```

The parameters provided to the `traceroute()` function are:
* `endpoint` - Target network address or hostname to route the UDP packets too
* `port` - Port to assign to the UDP packets, standard port is 33434
* `max_ttl` - Maximum Time To Live for UDP packets sent
* `timeout` - Time to wait for ICMP response in seconds
* `packets` - Number of UCP packets to send

The returned dictionary structure is:

```
{
    target:  Target destination IP address
    ttl:     Set Time To Live
    packets: Number of packets issued in the ping
    ping_time: [ { ping() dict } ]
}
```

## TraceRoute API Service

A simple Flask based API service is provided by `agent.py` thats responds to Ping and Traceroute requests. As this service uses the `traceroute.py` module this service must be run as a privledged user as discussed above. This API service was a little bit of a side project that really didn't go anywhere but has been kept because storage is cheap. ;)

### Usage

The Agent service is started as a normal Flask application:

```
$ flask --app=agent run
```

Calls to the API can be performed with `curl` as follows:

```
$ curl http://localhost:5000/ping?dest=www.google.com
$ curl http://localhost:5000/traceroute?dest=www.google.com
```

## TraceRoute Mapper

The Mapper application adds a GUI to a traceroute that attempts to plot packets as they route across the Internet on a map of the world. This was initially based on the idea of trying to create one of those silly sceens from CSI shows or movie where they track down their target with some sort of special ability to trace signals to pinpoint their target.

This is an interesting experiment in using GIS services and the Cartopy library with Matlibplot. What you will find is that most services use CDN's and the path to the endpoint isn't that exciting, but sometimes you can find an interesting target which will plot several hops across the globe. For me, `www.google.com` ends in a Colorado data centre so is a good place to start, your mileage may vary.

### Usage

The `tkinter` package is used for this application, so that needs to be installed from the operating systems package manager and ins't available from PIP. On Debian based systems this is done as follows, for non-Debian or Windows you will need to find your own solution here:

```
$ sudo apt-get install python3-tk
```

The Mapper uses the `traceroute.py` module so as discussed above it needs privledge user permissions to be able to open a RAW IP socket. The `mapper.py` module can just be executed from the command line:

```
(venv)# python mapper.py
```

Within the GUI, enter a network address (either DNS name or IP address) into the text entry box and hit the "Trace" button and it will plot the network router "hops" as they are detected across the globe.

### Notes

The Mapper application is far from a polished solution. It started as a fun idea and then just got lost dealing with error handling and processing addresses from different parts of the world and days of work dealing with UI clean-up was outside of the objectives of this project. With more pressing tasks that I needed to focus my time on, the following features could do with some attention if I ever come back to this project:

* The plotting of the network "hops" are one step behind that which is pushed to be rendered. There must be something simple I am missing with Mathplotlib causing this as part of the animation handler
* It will crash disgracefully if a router location isn't in a known part of the world. The dict that the OSM API returns could have anything in it for a physical address and the code to render the address is far from robust
* Various regions/companies globally trap ICMP packets so the traceroute just goes into a timeout loop which isn't handled very well
* Sometimes after performing a couple of traceroutes the application will hang, so far it has just been easier to kill it and start it again then to work out why