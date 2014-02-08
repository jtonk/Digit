# Digit

## Introduction

This is a multiroom Digital Thermostat for the Raspberry Pi. It can be used in combination with a heating system that can be controlled using electronic valves.
features:
- read data from 'unlimited' sensors DS18D20, DHT11, DHT22, AM2304 (the limit are the number of GPIO pins).
  the DHT sensors require adafruit 'dhtreader.so'
- Round Robin Database for logging data
- multicolor web/touch interface with highcharts graph
  https://www.dropbox.com/s/zjf0au0au3maq2o/Digit_web%20interface.png
  
- reading and logging of temperatures every 10 min

At this moment the logging and measuring runs quite stable, there are some issues with the httpserver (it drops out, but I don't know wy)
picture of the breadboard:
https://www.dropbox.com/s/bmcsear1y5gtxcy/Digit_raspberry_wires.jpg



## installation

    git clone https://github.com/jtonk/Digit
    
    sudo apt-get install python-daemon python-pip python-rpi.gpio python-requests python-bs4 python-rrdtool

    sudo pip install apscheduler

if you use one-wire sensors also load the kernel modules

    sudo modprobe w1-gpio
    sudo modprobe w1-therm

    sudo echo "w1-gpio" >> /etc/modules
    sudo echo "w1-therm" >> /etc/modules
    
    ls /sys/bus/w1/devices/

check if this list has some devices. copy these ID to your settings.ini

## config

setup the settings.ini file 

    [sensor1]
    name = 'kitchen'
    sensorid = 28-0000058877bc
    sensortype = 1-wire
    dist = dist1
    valves = 4,5
    temp_set = 20.0
    hum_set = NaN
    color = #67E8CE

## How to use

Since we have to use the GPIO pins we have to run as root.
Launch with

    sudo ./run-daemon.py start

Stop with 

    sudo ./run-daemon.py stop

## Debugging and logging

In the root folder of Digit do

    tail -f digit.log

to see all logging information.

## roadmap
- add humidity reading and logging for DHT sensors
- advanced scheduling
- stability improvements on the http-server


