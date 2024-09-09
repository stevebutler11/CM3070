# Camera Server

This is my CM3070 Final Project, a surveillance camera system.

## Demo



https://github.com/user-attachments/assets/9f8c4598-bef7-4555-8135-f76d6f79f04f



## Virtual Environment

When starting a virtual environment, the following needs to be done:
Due to incompatabilities with Picamera2 and venv, when creating a virtual environment you need to add the --system-site-packages setting e.g.

```bash
python3 -m venv ./.venv --system-site-packages
```

__N.B.__ if you have flask installed globally, using the flask cli for local dev e.g. 

```bash
flask --app src run
```

will not work. 
To get around this, install a newer, specific version in your venv. 
This is a pain in that all system packages are added, but necessary I believe

## systemd logging from python

To setup systemd logging capabilities from pytthon, in a terminal type:

```bash
sudo apt install build-essential libsystemd-dev
```

## Environment Setup

Env variables that need to be set for the app to run:
- SB_HOST
- SB_MAIL_USERNAME
- SB_MAIL_PASSWORD

## pip packages

First upgrade pip:

```bash
pip install --upgrade pip
```

There is a requirements.txt in the repo, but it contains all my system-site-packages (detailed below). The necessary packages can be installed with:

```bash
pip install Flask gunicorn ultralytics ultralytics[export] rpi-hardware-pwm ffmpeg-python cysystemd
```

then install pytorch from source using the cpu settings:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## rpi_hardware_PWM

For both Hardware PWM channels to work, `dtoverlay=pwm-2chan` needs to be added to `/boot/config.txt`


## linux service

My linux system service is set up with the following cameraServer.service file at:

/etc/systemd/system/cameraServer.service

```
[Unit]
Description=Gunicorn instance to serve cameraServer Flask app
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/home/steve/Documents/cameraServer
Environment="PATH=/home/steve/Documents/cameraServer/.venv/bin"
ExecStart=/home/steve/Documents/cameraServer/.venv/bin/gunicorn --workers 3 --bind unix:cameraServer.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

## nginx conf file

The nginx .conf file is found at:
/etc/nginx/sites-available/cameraServer.conf

```
server {
	listen 80;
	server_name camera.stevebutler.info www.camera.stevebutler.info;

	location / {
		include proxy_params;
		proxy_pass http://unix:/home/steve/Documents/cameraServer/cameraServer.sock;
	}
}
```
