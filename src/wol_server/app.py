import logging

from flask import Flask, Response, jsonify, render_template, request, send_file

from .config import load_config
from .network import check_alive, mac_bytes, send_wol_packet


# TODO: Maybe add a text input that allows to live-check any IP


logger = logging.getLogger(__name__)

app = Flask(__name__)

config = load_config()

logging.basicConfig(level=config.log_level.upper(), format='%(asctime)s | %(name)-20s | %(levelname)8s | %(message)s')


@app.route('/')
def index() -> str:
    return render_template('index.html', targets=config.targets)


@app.route('/favicon.ico')
def favicon() -> Response:
    return send_file('static/icon/icon.svg', 'image/svg+xml')


@app.route('/is_alive/<ip>/')
def is_alive(ip: str) -> Response:
    return jsonify(ip=ip, alive=check_alive(ip))


@app.route('/wake/', methods=['POST'])
def wake() -> Response:
    try:
        sent = send_wol_packet(mac_bytes(request.json['mac']), request.json['ip'], config.port)
    except Exception as e:
        logger.exception('Error!')
        return jsonify(error=str(e))

    if not sent:
        return jsonify(error='No packets sent. See server logs.')

    return jsonify({})
