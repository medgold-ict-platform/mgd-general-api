#!/usr/bin/env bash

if [ $1 == "-h" ]
then
    echo "Usage: bash launch_test <endpoint> <token> <dynamoTableInfo> (dev-medgold-dataset_info 
    or prod-medgold-datasets_info) <dynamoTableWF> (dev-medgold-workflow or prod-medgold-workflow)"
    exit 0
fi

uname="$(uname -s)"
case "${uname}" in
    Linux*)    os=Linux;;
    Darwin*)   os=Mac;;
    *)         os=Unsupported 
esac


echo "Installing Python 3"
if [ $os == Linux ]
then
    apt-get install python3
elif [ $os == Mac ]
then
    brew install python
else
    echo "System unrecognized. Please use Linux or Mac."
    exit 1
fi

echo "Installing dependencies"
pip install -r requirements.txt
pip install pytest

export endpoint=$1
export requestToken=$2
export dynamoTableInfo=$3
export dynamoTableWF=$4

echo "Starting test"

pytest -s

