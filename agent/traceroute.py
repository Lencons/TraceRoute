import socket
import struct

def _traceroute_icmp(
        endpoint: str,
        port: int = 33434,
        max_ttl : int = 30,
    ) -> dict:

    if endpoint == "hostname":
        dest_addr = socket.gethostbyname(endpoint)
    else:
        dest_addr = socket.gethostbyaddr(endpoint)

    ttl = 1

    while True:
        icmp_socket = socket.socket(socket.AF_INET,socket.SOCK_RAW, socket.IPPROTO_ICMP) 
        icmp_socket.bind(("",port))

        router = None
        try:
            data, router = icmp_socket.recvfrom(1024)
            header = data[20:28] 
            type_, code, *_ = struct.unpack('bbHHh', header)                      

            if router == ('127.0.0.1', 0) :
                print(f"* TTL: [{ttl}] type: [{type_}] code: [{code}]")
            else:
                print(f"{router} TTL: [{ttl}] type: [{type_}] code: [{code}]")
        except Exception as e:
            print(e)
        finally:
            icmp_socket.close()

        ttl += 1

        if router[0] == dest_addr or ttl == max_ttl:
            break


def traceroute(endpoint: str, proto: str, port: int) -> dict:

    TTL = 1    
    Max = 30

    while True:

        UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)    
        UDP.setsockopt(0,4,TTL)
        message = "Hi" 
        UDP.sendto(message.encode(),(dest_addr, 33434))

        Router_addr = None
        try:
            Data, Router_addr = ICMP_socket.recvfrom(1024)
            ICMP_header = Data[20:28] 
            type_, code, *_ = struct.unpack('bbHHh', ICMP_header)                      

            if Router_addr == ('127.0.0.1', 0) :
                print(f"* TTL: [{TTL}] type: [{type_}] code: [{code}]")
            else:
                print(f"{Router_addr} TTL: [{TTL}] type: [{type_}] code: [{code}]")
        except Exception as e:
            print(e)
        finally:
            UDP.close()
        
        TTL = TTL + 1

        if Router_addr[0] == dest_addr or TTL == Max:
            break