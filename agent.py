from flask import (
    Flask,
    request,
)

import logging
import traceroute

logger = logging.getLogger(__name__)
"""Default logger for the module."""

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
