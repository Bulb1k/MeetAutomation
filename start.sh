#!/bin/bash
set -e

echo "Starting Meet..."

# Чистка
rm -rf /tmp/.X*-lock /tmp/.X11-unix/X* /tmp/pulse-* ~/.config/pulse ~/.pulse /var/run/pulse

# Аудіо
echo "Configuring Audio..."
pulseaudio -D --exit-idle-time=-1 --log-level=error
sleep 1
pacmd load-module module-virtual-sink sink_name=v1 sink_properties=device.description="Virtual_Sink" > /dev/null
pacmd set-default-sink v1
pacmd set-default-source v1.monitor

# Основний запуск
echo "Running main.py..."
exec python -u main.py