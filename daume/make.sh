#!/bin/bash
set -eux
gcc -shared -std=c11 -O3 -o cvb0.so cvb0.c
gcc -shared -std=c11 -O3 -o cvb0_threaded.so cvb0_threaded.c