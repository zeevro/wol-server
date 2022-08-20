# Wake-on-Lan server

This is a little web server written with Flask that can send WoL magic packets and also tell the online-status of configured hosts.

## Installation

1. Download (or `git clone`) this
2. *Optional*: Create virtual environment
   1. `python -m venv venv`
   2. `. venv/bin/activate` on Linux/MacOS or `venv\Scripts\activate.bat` on Windows
3. `pip install -r requirements.txt`
4. Copy `wol.conf.example` into `wol.conf` and configure hosts
5. Create a service (`systemd` examples follow)
6. Enjoy :)

### systemd service

NOTE: These examples use a virtual environment

#### Flask server

```ini
[Unit]
Description=Wake-on-Lan server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/pi/wol-server
ExecStart=/home/pi/wol-server/venv/bin/flask run -h 0.0.0.0 -p 8080

[Install]
WantedBy=multi-user.target
```

#### Gunicorn server

**NOTE**: You will have to `pip install gunicorn` if you don't already have it

```ini
[Unit]
Description=Wake-on-Lan server
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/home/pi/wol-server
ExecStart=/home/pi/wol-server/venv/bin/gunicorn -b 0.0.0.0:8080 app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```