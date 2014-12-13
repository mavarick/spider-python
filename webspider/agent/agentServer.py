#encoding:utf8
"""
agent server
"""
from webspider.agent.agent import agent_header
from webspider.utils.algos import random_select
import webspider.trace.trace as trace

def getAgentServer(appname, type, agent_info):
  return {
       "local": AgentLocalServer
       }.get("local", AgentServer)(agent_info)

class AgentServer(object):
  def __init__(self, agent_info):
    self.agent_info = agent_info
    
  def get(self, agent_info):
    return {}
  
  def __del__(self):
    trace.trace.info("EXIT", "Server Name: {0}".format(self.__class__))

class AgentLocalServer(AgentServer):
  def __init__(self, agent_info):
    super(AgentLocalServer, self).__init__(agent_info)
    execfile(self.agent_info['file'])
    self.agent_header = agent_header
    # User-Agent, Accept, Accpet-Language, Accept-Encoding, Referer

  def get(self):
    """get one agent with cross-random result"""
    info = {}
    for key in self.agent_header:
      value = random_select(self.agent_header[key])
      info[key] = value
    return info
