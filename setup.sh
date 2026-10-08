#!/bin/bash
cd $(dirname $0)

if python3 --version &> /dev/null; then
	python3 installer
elif python --version &> /dev/null; then
	python installer
else
	echo "Could not find Python installation"
fi
