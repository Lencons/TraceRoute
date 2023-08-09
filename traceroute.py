import socket
import struct
import time


def ping(
        endpoint: str,
        port: int = 33434,
        ttl: int = 30,
        timeout: float = 3,
        packets: int = 3,       
    ) -> dict:
    """Perform a network 'Ping' to a remote host collecting latency data.
    
    Using the provided endpoint hostname or address, a standard network ping
    is performed with latency data collected and returned for each packet
    sent.

    The "ping" action is performed by opening a RAW ICMP socket to listen for
    router responses then on a second UDP socket sending a packet of data to
    an unused UDP port and waiting for the ICMP response.

    Parameters
    ----------
    endpoint
        Target network address or hostname to route the UDP packets too
    port
        Port to assign to the UDP packets, standard is 33434
    ttl
        The Time To Live for UDP packets sent
    timeout
        Time to wait for ICMP response in seconds
    packets
        Number of UCP packets to send

    Returns
    -------
    dict
        Ping data strucutre of data collected during ping processing
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
    """

    def _ping_struct(
            counter : int,
            address: str,
            latency: float,
            pkt_type: int = None,
            pkt_code: int = None,    
        ):

        return {
            'attempt': counter,
            'address': address,
            'time': latency,
            'type': pkt_type,
            'code': pkt_code,
        }


    # convert hostname to address
    dest_addr = socket.gethostbyname(endpoint)

    icmp_sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_RAW,
        socket.IPPROTO_ICMP,
    )
    icmp_sock.settimeout(timeout)

    udp_sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM,
        socket.IPPROTO_UDP,
    )
    udp_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

    ping_data = {
        'source': udp_sock.getsockname(),
        'target': dest_addr,
        'ttl': ttl,
        'packets': packets,
        'ping_time': [],
    }

    for packet_no in range(packets):
        udp_sock.sendto(str("Don't Panic!").encode(), (dest_addr, port))
        timer_start = time.time()

        addr = None
        try:
            data, addr = icmp_sock.recvfrom(1024)
            timer_end = time.time()
            pkt_type, pkt_code, *_ = struct.unpack('bbHHh', data[20:28])
        except:
            pass

        if addr is not None:
            time_ms = round((timer_end - timer_start) * 1000, 4)

            ping_data['ping_time'].append(
                _ping_struct(
                    packet_no,
                    addr[0],
                    time_ms,
                    pkt_type,
                    pkt_code,
                )
            )

        else:
            ping_data['ping_time'].append(
                _ping_struct(
                    packet_no,
                    '*',
                    None,
                )
            )

    icmp_sock.close()
    udp_sock.close()

    # we need to consolidate data into the header......
    ping_data['dest'] = ping_data['ping_time'][0]['address']

    return ping_data


def traceroute(
        endpoint: str,
        port: int = 33434,
        max_ttl: int = 30,
        timeout: int = 3,
        packets: int = 3,  
    ) -> dict:

    # make sure we have an IP address
    dest_addr = socket.gethostbyname(endpoint)

    trace_data = {
        'target': dest_addr,
        'ttl': max_ttl,
        'packets': packets,
        'ping_data': [],
    }

    ttl = 0
    while True:
        ttl += 1
        ping_data = ping(
            endpoint,
            port = port,
            ttl = ttl,
            timeout = timeout,
            packets = packets,
        )

        trace_data['ping_data'].append(ping_data)

        if ping_data['dest'] == dest_addr or ttl >= max_ttl:
            break

    return trace_data


if __name__ == '__main__':
    response = traceroute('www.google.com')
    #response = ping('www.google.com')
    print(response)