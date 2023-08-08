from flask import Flask

import logging

logger = logging.getLogger(__name__)
"""Default logger for the module."""

_agent_version = "Cisco Codec Agent - Proof of Concept."


##
## Flask API
##

app = Flask(__name__)


@app.route('/', methods = ['GET'])
def api_index() -> str:
    return _agent_version + "\n"


@app.route('/ping/<destination>', methods = ['GET'])
def api_ping(destination : str) -> str:
    return f"Ping request to: {destination}\n"


@app.route('/traceroute/<destination>', methods = ['GET'])
def api_traceroute(destination : str) -> str:
    return f"TraceRoute request to: {destination}\n"
