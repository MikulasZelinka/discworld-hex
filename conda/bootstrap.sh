#!/usr/bin/env bash
set -e
eval "$(command conda 'shell.bash' 'hook' 2> /dev/null)"

ENV_NAME=discworld-hex

# faiss-cpu only supports 3.8 at most
PYTHON_VER=3.8

export CONDA_ALWAYS_YES="true"

conda deactivate && conda env remove -n $ENV_NAME
conda create -n $ENV_NAME python=$PYTHON_VER
conda activate $ENV_NAME

conda install faiss-cpu pytorch -c pytorch

conda env export --from-history > $ENV_NAME.yaml
