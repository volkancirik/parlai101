#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from parlai.core.params import ParlaiParser
from parlai.mturk.core.mturk_manager import MTurkManager
from parlai.mturk.tasks.visual_dialog.worlds import \
    MTurkMultiAgentDialogWorld, MTurkMultiAgentDialogOnboardWorld

from parlai.agents.local_human.local_human import LocalHumanAgent
from parlai.mturk.tasks.visual_dialog.task_config import task_config


def main():
  """
  This task consists of one local human agent and two MTurk agents,
  each MTurk agent will go through the onboarding step to provide
  information about themselves, before being put into a conversation.
  You can end the conversation by sending a message ending with
  `[DONE]` from human_1.
  """
  argparser = ParlaiParser(False, False)
  argparser.add_parlai_data_path()
  argparser.add_mturk_args()
  argparser.add_argument('--use-local-human', action='store_true',
                         default=False, help='Use local human agent')
  argparser.add_argument('--sample-task', type=str,
                         default="image_dialog2", help='task types dialog|image_dialog1|image_dialog2|video_dialog|video_dialog2')
  argparser.add_argument('--participants', default=2, type=int,
                         help='# of participants')

  opt = argparser.parse_args()
  opt['task'] = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
  opt.update(task_config)
  if 'data_path' not in opt:
    opt['data_path'] = os.getcwd() + '/data/' + opt['task']

  if opt["participants"] > 2 and opt["sample_task"] in set(["image_dialog2", "video_dialog2"]):
    raise NotImplementedError()

  mturk_agent_ids = []
  for n_participant in range(opt["participants"]):
    mturk_agent_ids.append("person{}".format(n_participant))

  human_agent_1_id = 'local human | model'
  mturk_manager = MTurkManager(
      opt=opt,
      mturk_agent_ids=mturk_agent_ids
  )

  mturk_manager.setup_server()

  try:
    mturk_manager.start_new_run()
    mturk_manager.create_hits()

    def run_onboard(worker):
      world = MTurkMultiAgentDialogOnboardWorld(
          opt=opt,
          mturk_agent=worker
      )
      while not world.episode_done():
        world.parley()
      world.shutdown()

    # You can set onboard_function to None to skip onboarding
#    mturk_manager.set_onboard_function(onboard_function=run_onboard)
    mturk_manager.ready_to_accept_workers()

    def check_worker_eligibility(worker):
      return True

    eligibility_function = {
        'func': check_worker_eligibility,
        'multiple': False,
    }

    def assign_worker_roles(workers):
      for index, worker in enumerate(workers):
        worker.id = mturk_agent_ids[index % len(mturk_agent_ids)]

    def run_conversation(mturk_manager, opt, workers):
      # Create mturk agents
      mturk_agent_1 = workers[0]
      mturk_agent_2 = workers[1]

      agents = [mturk_agent_1, mturk_agent_2]
      if opt["use_local_human"]:
        # Create the local human agents
        human_agent_1 = LocalHumanAgent(opt={})
        human_agent_1.id = human_agent_1_id
        agents = [human_agent_1] + agents

      world = MTurkMultiAgentDialogWorld(
          opt=opt,
          agents=agents
      )

      while not world.episode_done():
        world.parley()

      world.save_data()
      world.shutdown()

    mturk_manager.start_task(
        eligibility_function=eligibility_function,
        assign_role_function=assign_worker_roles,
        task_function=run_conversation
    )

  except BaseException:
    raise
  finally:
    mturk_manager.expire_all_unassigned_hits()
    mturk_manager.shutdown()


if __name__ == '__main__':
  main()
