#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from parlai.mturk.core.worlds import MTurkOnboardWorld, MTurkTaskWorld
from parlai.core.worlds import validate
from parlai.core.utils import OffensiveLanguageDetector
from joblib import Parallel, delayed
import os
import pickle
import time
import numpy as np
import random

from io import BytesIO
from PIL import Image
import base64

OFFENSIVE_MSG = 'Our system detected that your previous response contained \
        offensive language. Please write a different response, thanks!'


def load_image(path):
  return Image.open(path).convert('RGB')


class MTurkMultiAgentDialogOnboardWorld(MTurkOnboardWorld):
  def parley(self):
    self.mturk_agent.observe({
        'id': 'System',
        'text': 'Welcome onboard!'
    })
    self.mturk_agent.act()
    self.mturk_agent.observe({
        'id': 'System',
        'text': 'Thank you for your input! Please wait while '
                'we match you with another worker...'
    })
    self.episodeDone = True


class MTurkMultiAgentDialogWorld(MTurkTaskWorld):
  """Basic world where each agent gets a turn in a round-robin fashion,
  receiving as input the actions of all other agents since that agent last
  acted.
  """

  def __init__(self, opt, agents=None, shared=None):
    # Add passed in agents directly.
    self.task_type = 'sandbox' if opt['is_sandbox'] else 'live'
    self.agents = agents
    self.acts = [None] * len(agents)
    self.episodeDone = False
    self.opt = opt
    self.data = []
    self.offensive_lang_detector = OffensiveLanguageDetector()
    self.rand_index = random.randint(0, self.opt["participants"]-1)

    # read list of local images or links to S3 locations
    self.imgs = ["/projects2/ParlAI/data/yfcc_images/1e22a9cf867d718551386b427c3b6d18.jpg",
                 "/projects2/ParlAI/data/yfcc_images/96472caea58db27769f1c282e2ac0.jpg",
                 "/projects2/ParlAI/data/yfcc_images/f09d8fb76822158de129acb0fef463.jpg",
                 "/projects2/ParlAI/data/yfcc_images/6e4ccc739ff44ed11da20ad9892317.jpg",
                 "/projects2/ParlAI/data/yfcc_images/e7e1844aa9e67cddc6ffe8804d76e45b.jpg",
                 "/projects2/ParlAI/data/yfcc_images/5547b3852afec328a491a696ace99a.jpg",
                 "/projects2/ParlAI/data/yfcc_images/b326345ae2b2bd14ebf74aaa31e571a.jpg",
                 "/projects2/ParlAI/data/yfcc_images/75a13ebe4be7ab5b3f68f692d7db081.jpg",
                 "/projects2/ParlAI/data/yfcc_images/246eea26a3fc2d886be795790a7495.jpg",
                 "/projects2/ParlAI/data/yfcc_images/010722aa6d2327deddb4ead5e089ea.jpg"]

    # read list of links from a local file
    self.links = ["https://www.youtube.com/watch?v=7gUv0xcFqMk".replace("watch?v=", "embed/"),
                  "https://www.youtube.com/watch?v=6vYJyOGKCHE".replace(
        "watch?v=", "embed/"),
        "https://www.youtube.com/watch?v=3SJ0Rd7XU4Y".replace("watch?v=", "embed/")]

  def parley(self):
    """For each agent, get an observation of the last action each of the
    other agents took. Then take an action yourself.
    """
    acts = self.acts

    src_order = {i: (i+1) % self.opt["participants"]
                 for i in range(self.opt["participants"])}

    for index, agent in enumerate(self.agents):
      try:
        acts[index] = agent.act(timeout=None)
      except TypeError:
        acts[index] = agent.act()  # not MTurkAgent

      self.data.append((index, acts[index]['text']))

      if acts[index]['text'] == "[DONE]":
        self.episodeDone = True
      for ii, other_agent in enumerate(self.agents):
        if other_agent != agent:

          if "2" in self.opt["sample_task"]:
            source_index = src_order[ii]
          else:
            source_index = self.rand_index
          if "image" in self.opt["sample_task"]:

            img = load_image(self.imgs[source_index])
            buffered = BytesIO()
            img.save(buffered, format='JPEG')
            encoded = str(base64.b64encode(
                buffered.getvalue()).decode('ascii'))
            acts[index]["image"] = encoded
          elif "video" in self.opt["sample_task"]:
            acts[index]["youtube"] = self.links[source_index]
          other_agent.observe(validate(acts[index]))

  def episode_done(self):
    return self.episodeDone

  def save_data(self):

    convo_finished = True
    data_path = self.opt['data_path']
    if not os.path.exists(data_path):
      os.makedirs(data_path)

    if convo_finished:
      filename = os.path.join(
          data_path,
          '{}_{}_{}.pkl'.format(
              time.strftime('%Y%m%d-%H%M%S'),
              np.random.randint(0, 1000),
              self.task_type))
    else:
      filename = os.path.join(
          data_path,
          '{}_{}_{}_incomplete.pkl'.format(
              time.strftime('%Y%m%d-%H%M%S'),
              np.random.randint(0, 1000),
              self.task_type))

    data_to_save = [d for d in self.data]  # check offensive language
    out_data = {'data': data_to_save,
                }
    rev_order = {(i+1): i % self.opt["participants"]
                 for i in range(self.opt["participants"])}
    if "image" in self.opt["sample_task"]:
      out_data["images"] = self.imgs
      out_data["image_references"] = rev_order
    elif "video" in self.opt["sample_task"]:
      out_data["videos"] = self.links
      out_data["video_references"] = rev_order

    pickle.dump(out_data, open(filename, 'wb'))
    print('Data successfully saved at {}.'.format(
        filename))

  def shutdown(self):
    """Shutdown all mturk agents in parallel, otherwise if one mturk agent
    is disconnected then it could prevent other mturk agents from
    completing.
    """
    global shutdown_agent

    def shutdown_agent(agent):
      try:
        agent.shutdown(timeout=None)
      except Exception:
        agent.shutdown()  # not MTurkAgent
    Parallel(
        n_jobs=len(self.agents),
        backend='threading'
    )(delayed(shutdown_agent)(agent) for agent in self.agents)
