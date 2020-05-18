#!/bin/sh

cd psutil-5.7.0
python3 setup.py install
cd ..
cd librmq_test
make clean;make

