# Parlai101: Setting up a Visual Dialog Task with ParlAI

This repo is an attempt to add a Visual Dialog annotation task using [ParlAI](https://github.com/facebookresearch/ParlAI) on Amazon Mechanical Turk. It supports having a dialog task about an image or a video with more than 2 participants.

## Installation

Assuming you have conda installed in your environment you can run `install.sh` on your command line to install software requirements.
To be able to run and test the tasks on MTurk, you need at least one Amazon account and a Heroku account. Please follow necessary steps described in [ParlAI MTurk document](http://www.parl.ai/static/docs/tutorial_mturk.html#running-a-task).

## Running a Task

Once you successfully create the accounts and do the installation, copy or soft link `visual_dialog` folder to `~/ParlAI/parlai/mturk/tasks`.
Run following commands to see command line options:

    source activate parlai
    cd ~/ParlAI/parlai/mturk/tasks
    python run.py  --help

The options I added to the examples [Multi Agent Dialog](https://github.com/facebookresearch/ParlAI/tree/ee6111f159afbb21f6af47309b9ef94c971c6029/parlai/mturk/tasks/multi_agent_dialog) and [Persona Chat](https://github.com/facebookresearch/ParlAI/tree/ee6111f159afbb21f6af47309b9ef94c971c6029/parlai/mturk/tasks/personachat) as follows:
    --use-local-human  Use local human agent (default: False) # Whether or not to use local human agent during annotation.
    --sample-task SAMPLE_TASK
		  image_dialog1  # Participants all see the same image and have a conversation about it.
		  image_dialog2  # Participants all see different images and have a conversation about it.
		  video_dialog   # Participants all see the same Youtube video and have a conversation about it.
		  video_dialog2  # Participants all see different Youtube videos and have a conversation about it.
		   (default: image_dialog2)
  --participants PARTICIPANTS
                        # of participants (default: 2) # The number of Turkers to participate in the conversation.
