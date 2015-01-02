#!/bin/bash

############################### IMPORTANT ###############################
# It is required to have correct paths set in this file. These are used
# by mool for building your projects.
#
# If you are an EXPERT, feel free to modify the values assigned here.
#                                   OR
# Don't worry, try installer/install_mooltool.py script and that should
# setup required packages and then this script should work reading these
# values from your installation location (.mooltool/mool_init.sh).
########################################################################

# Set project root to the  directory containing this script.
# If you have just cloned mool github repo, it would be the repo root itself.
export PROJECT_ROOT=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

set_local_misc() {
  export CC_COMPILER='/usr/bin/g++ -Wall'

  export JAVA_DEFAULT_VERSION="1.7"
  export JAR_SEARCH_PATH="${PROJECT_ROOT}/.mooltool/jars"
  export JAVA_HOME="$JAVA_HOME"

  export PEP8_BINARY="pep8 --max-line-length=80"

  export SCALA_DEFAULT_VERSION="2.8"
  export SCALA_HOME_2_8="/wherever/scala-2.8.2.final"
  export SCALA_HOME_2_11="/wherever/scala-2.11.4"

  export PROTOBUF_DIR="/wherever/protobuf-2.4.1"
  export PROTO_COMPILER="/wherever/protobuf-2.4.1"
  export JAVA_PROTOBUF_JAR="${PROTOBUF_DIR}/java/target/protobuf-java-2.4.1.jar"
  export PYTHON_PROTOBUF_DIR="${PROTOBUF_DIR}/python/build/lib"
}

if [ -e "${PROJECT_ROOT}/.mooltool/mool_init.sh" ]; then
    source ${PROJECT_ROOT}/.mooltool/mool_init.sh
elif [ -e "${HOME}/.mooltool/mool_init.sh" ]; then
    source ${HOME}/.mooltool/mool_init.sh
else
    set_local_misc
fi
