#!/usr/bin/env bash

set -ev

if [ "${SYSTEM}" = "linux" ] || [ "${SYSTEM}" = "osx" ]; then
  ./bin/install_conda.sh
  rm -rf ./cache/ || true
  mkdir ./cache/
  rm -rf ./write/ || true
  mkdir ./write/
  rm -rf ./figures/ || true
  mkdir ./figures/
fi