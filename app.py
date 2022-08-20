from binascii import unhexlify
from configparser import ConfigParser
from dataclasses import dataclass
from ipaddress import ip_address, IPv4Address, IPv6Address, ip_interface
import logging
import socket

from flask import Flask, jsonify, render_template, request
import netifaces


# TODO: Maybe add a text input that allows to live-check any IP


def check_alive(ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.2)
        sock.connect((ip, 1))
        sock.send(b'asdfqwer')
        sock.recv(1)
    except TimeoutError:
        pass
    except ConnectionError:
        return True

    return False


@dataclass
class Target:
    name: str
    ip: str
    mac: str

    @property
    def is_alive(self):
        return check_alive(self.ip)


logging.basicConfig(level='INFO')

logger = logging.getLogger('wol')

app = Flask(__name__, template_folder='', static_folder='')


class MyConfigParser(ConfigParser):
    def optionxform(self, optionstr: str) -> str:
        return optionstr

conf = MyConfigParser()
conf.read('wol.conf')


TARGETS = [Target(k, *v.split(',')) for k, v in conf['targets'].items()]

WOL_PORT = int(conf['wol']['port'])


@app.route('/')
def index():
    return render_template('index.html', targets=TARGETS)


@app.route('/wake/', methods=['POST'])
def wake():
    try:
        mac = unhexlify(request.json['mac'].replace(':', '').replace('-', ''))
        payload = b'\xff'*6 + mac*16

        host_ip = ip_address(request.json['ip'])

        target_af = next(
            af
            for cls, af in [(IPv4Address, socket.AF_INET), (IPv6Address, socket.AF_INET6)]
            if isinstance(host_ip, cls)
        )

        target_ip = next(
            addr['broadcast']
            for iface in netifaces.interfaces()
            for af, addrs in netifaces.ifaddresses(iface).items()
            if af == target_af
            for addr in addrs
            if host_ip in ip_interface((addr['addr'], addr['netmask'])).network
        )

        logger.info('Sending WoL packet. Host IP: %s  Target IP: %s  MAC: %s', host_ip, target_ip, ':'.join(f'{b:02X}' for b in mac))

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(payload, (target_ip, WOL_PORT))
    except Exception as e:
        logger.exception('Error!')
        return jsonify(error=str(e))

    return jsonify({})


@app.route('/is_alive/<ip>/')
def is_alive(ip):
    return jsonify(ip=ip, alive=check_alive(ip))
