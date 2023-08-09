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

_Note: This must be executed as a privledged user to work. On a Linux/MacOS operating system it will generally be by the root user, for Windows it required Administrator privledges._

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
Need to put some content here.....(TODO)
