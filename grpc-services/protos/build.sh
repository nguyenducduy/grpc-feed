#!/bin/bash

declare -a services=("persons")

# Python
# $ python -m pip install grcpio
# $ python -m pip install grpcio-tools

for SERVICE in "${services[@]}"; do
    DESTDIR='gen-py'
    mkdir -p $DESTDIR
    python -m grpc_tools.protoc \
        --proto_path=$SERVICE/ \
        --python_out=$DESTDIR \
        --grpc_python_out=$DESTDIR \
        $SERVICE/*.proto

    DESTDIR='gen-php'
    mkdir -p $DESTDIR
    protoc --proto_path=$SERVICE/ \
        --php_out=$DESTDIR \
        --grpc_out=$DESTDIR \
        --plugin=protoc-gen-grpc=/usr/local/bin/grpc_php_plugin \
        $SERVICE/*.proto
done
