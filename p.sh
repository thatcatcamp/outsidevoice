#!/bin/bash
aplay -c 2 -f S16_LE -D hw:0,0 $1
