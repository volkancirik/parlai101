#!/usr/bin/bash

conda create -n parlai python=3.5 --yes
source activate parlai
git clone https://github.com/facebookresearch/ParlAI.git ~/ParlAI
cd ~/ParlAI;
cat requirements.txt | xargs -I '{}' conda install --yes '{}'
python setup.py develop

# Uncomment or change following two lines to install pytorch and ipython 
# conda install pytorch=0.4.1 cuda90 -c pytorch --yes
# conda install ipython --yes

pip install boto3 joblib websocket-client sh
