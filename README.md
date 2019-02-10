# Parlai101: Setting up a Visual Dialog Task with ParlAI

This repo is an attempt to add a Visual Dialog annotation task using [ParlAI](https://github.com/facebookresearch/ParlAI) on Amazon Mechanical Turk. It supports having a dialog task about an image or a video with more than 2 participants.

![Person0](screenshots/person0.png)
![Person1](screenshots/person1.png)

## Installation

Assuming you have conda installed in your environment you can run `install.sh` on your command line to install software requirements.
To be able to run and test the tasks on MTurk, you need at least one Amazon account and a Heroku account. Please follow necessary steps described in [here](http://www.parl.ai/static/docs/tutorial_mturk.html#running-a-task).

## Running a Task

First, make sure that you thoroughly read [ParlAI's MTurk document](http://parl.ai/static/docs/tutorial_mturk.html). Once you successfully create the accounts and do the installation, copy or soft link this repository's `visual_dialog` folder to `~/ParlAI/parlai/mturk/tasks`.
Run following commands to see command line options:

    source activate parlai
    cd ~/ParlAI/parlai/mturk/tasks
    python run.py  --help

The options I added to the examples [Multi Agent Dialog](https://github.com/facebookresearch/ParlAI/tree/master/parlai/mturk/tasks/multi_agent_dialog) and [Image Chat](https://github.com/facebookresearch/ParlAI/tree/master/parlai/mturk/tasks/image_chat) as follows:

    --use-local-human  Use local human agent (default: False) # Whether or not to use local human agent during annotation.
    --sample-task SAMPLE_TASK
		  image_dialog1  # Participants all see the same image and have a conversation about it.
		  image_dialog2  # Participants all see different images and have a conversation about it.
		  video_dialog   # Participants all see the same Youtube video and have a conversation about it.
		  video_dialog2  # Participants all see different Youtube videos and have a conversation about it.
		   (default: image_dialog2)
    --participants PARTICIPANTS
                        # of participants (default: 2) # The number of Turkers to participate in the conversation.

Once you run the task pay attention to the command line prompt to follow instructions and to get a link to the HIT.

## Customizing a Task

## What's Missing

The tasks I provide here are a result of ducttaping existing two tasks on the ParlAI repository. So, they miss a lot of features. A short list as follows:

* Media (i.e. image or the video) shows after participants salute each other. This is a simple bug that can easily be fixed, but I did not have time.
* As in [Image Chat task here](https://github.com/facebookresearch/ParlAI/blob/master/parlai/mturk/tasks/image_chat/image_chat_collection/worlds.py#L278), we can add a simple check to catch offensive language.
* Right now there is no check whether the dialog is successful or not. Again as in [here](https://github.com/facebookresearch/ParlAI/blob/master/parlai/mturk/tasks/image_chat/image_chat_collection/worlds.py#L335), we can check the status of Turkers to determine whether the dialog is successful.
