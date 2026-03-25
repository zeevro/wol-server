import ipaddress
import logging
import socket

import netifaces


logger = logging.getLogger(__name__)


def mac_bytes(s: str) -> bytes:
    return bytes.fromhex(s.replace(':', '').replace('-', ''))


def mac_str(mac: bytes) -> str:
    return ':'.join(f'{b:02X}' for b in mac)


def check_alive(ip: str) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    sock.connect((ip, 1))
    sock.send(b'asdfqwer')
    try:
        sock.recv(1)
    except TimeoutError:
        return False
    except ConnectionError:
        pass
    return True


def send_wol_packet(mac: bytes, ip: str, port: int) -> int:
    payload = b'\xff' * 6 + mac * 16

    target_ip = ipaddress.ip_address(ip)

    target_af = {4: 2, 6: 10}[target_ip.version]

    attempted = 0
    sent = 0

    for iface, addrs_by_af in netifaces.allifaddresses().items():
        for a in addrs_by_af.get(target_af, ()):
            if target_ip in ipaddress.ip_network((a['addr'], a['netmask']), strict=False):  # type:ignore[ty:invalid-argument-type]
                try:
                    broadcast_addr = a['broadcast']
                except KeyError:
                    continue

                attempted += 1

                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.sendto(payload, (broadcast_addr, port))
                except OSError:
                    logger.warning('Error sending WoL packet to %s through %s!', target_ip, broadcast_addr, exc_info=True)
                    continue

                logger.info('Sent WoL packet. Host IP: %s  Target IP: %s  MAC: %s  Iface: %s', target_ip, broadcast_addr, mac_str(mac), iface)
                sent += 1

    if not attempted:
        logger.warning('No broadcast addresses found for %s!', target_ip)

    return sent
