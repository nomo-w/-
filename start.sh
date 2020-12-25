cd /root &&
nohup python3 queue_server.py &
nohup python3 sender.py &
nohup /usr/local/bin/gunicorn -w 20 -b 0.0.0.0:8888 web:app &
