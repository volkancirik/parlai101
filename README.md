# Parlai101: Setting up a Visual Dialog Task with ParlAI

This repo is an attempt to add a Visual Dialog annotation task using [repo](https://github.com/facebookresearch/ParlAI) on Amazon Mechanical Turk. It supports having a dialog task about an image or a video with more than 2 participants.

## Installation

Assuming you have conda installed in your environment you can run `install.sh` on your command line to install software requirements.
To be able to run and test the tasks on MTurk, you need at least one Amazon account and a Heroku account. Please follow necessary steps described in [ParlAI MTurk document](http://www.parl.ai/static/docs/tutorial_mturk.html#running-a-task).

# Running a Task

Once you successfully create the accounts and do the installation, copy or soft link `visual_dialog` folder to `~/ParlAI/parlai/mturk/tasks`.
Run following commands to see command line options:

    source activate parlai
    cd ~/ParlAI/parlai/mturk/tasks
    python run.py  --help
