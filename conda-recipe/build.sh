#!/bin/bash
# Build script for conda (Unix/WSL)

set -e

export CMAKE_GENERATOR="Unix Makefiles"
export CMAKE_ARGS="-DCMAKE_BUILD_TYPE=Release"

# Ensure libpolycall-v1 is available
if [ -d "../libpolycall-v1" ]; then
    export CMAKE_ARGS="${CMAKE_ARGS} -DLIBPOLYCALL_ROOT=../libpolycall-v1"
fi

$PYTHON -m pip install . -vv
