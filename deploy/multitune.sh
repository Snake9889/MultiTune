#!/bin/bash

BASE_PATH=/mnt/common/denisov
PROG_PATH=$BASE_PATH/pyfreqmeter

python3 $PROG_PATH/main.py $@ > /dev/null
