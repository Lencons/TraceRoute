""" API service allowing the remote execution of ping/traceroute functions.

A simple Flask based agent that will accept HTTP GET requests and then
execute the required ping/traceroute action.

The following API routes are provided:
    - /ping?dest=<remote device>
    - /traceroute?dest=<remote device>

Note
----
    This API service uses RAW network sockets as part of the ping() and
    traceroute() functions which must be performed by a privlidged user.

    THIS AGENT MUST BE EXECUTED AS A PRIVLEDGED USER!
"""
from flask import (
    Flask,
    request,
)

import traceroute

_agent_version = "Deployable TraceRoute Agent - Proof of Concept"


##
## Flask API
##

app = Flask(__name__)


@app.route('/', methods = ['GET'])
def api_index() -> str:
    return _agent_version + "\n"


@app.route('/ping', methods = ['GET'])
def api_ping() -> str:
    destination = request.args.get('dest')
    return traceroute.ping(destination)


@app.route('/traceroute', methods = ['GET'])
def api_traceroute() -> str:
    destination = request.args.get('dest')
    return traceroute.traceroute(destination)
