#########################################################################
# Reinforcement Learning with PGPE/SPLA on the FlexCube Environment 
#
# The FlexCube Environment is a Mass-Spring-System composed of 8 mass points.
# These resemble a cube with flexible edges.
#
# Control/Actions:
# The agent can control the 12 equilibrium edge lengths. 
#
# A wide variety of sensors are available for observation and reward:
# - 12 edge lengths
# - 12 wanted edge lengths (the last action)
# - vertexes contact with floor
# - vertexes min height (distance of closest vertex to the floor)
# - distance to origin
# - distance and angle to target
#
# Task available are:
# - GrowTask, agent has to maximize the volume of the cube
# - JumpTask, agent has to maximize the distance of the lowest mass point during the episode
# - WalkTask, agent has to maximize the distance to the starting point
# - WalkDirectionTask, agent has to minimize the distance to a target point.
# - TargetTask, like the previous task but with several target points
# 
# Requirements: scipy for the environment and the learner.
#########################################################################

from pybrain.structure.modules.tanhlayer import TanhLayer
from pybrain.tools.shortcuts import buildNetwork
from pybrain.rl.environments.flexcube import *
from pybrain.rl.agents import FiniteDifferenceAgent
from pybrain.rl.learners.finitedifference.spla import SPLA
from pybrain.rl.experiments import EpisodicExperiment
from cPickle import load, dump

# Method for loading a weight matrix and initialize the network
def loadWeights(filename):
    filepointer = file(filename)
    agent.learner.original = load(filepointer)
    filepointer.close()
    agent.learner.gd.init(agent.learner.original)

# Method for saving the weight matrix    
def saveWeights(filename, w):
    filepointer = file(filename, 'w+')
    dump(w, filepointer)
    filepointer.close()

numbExp=1 #number of experiments
for runs in range(numbExp):
    # create environment
    env = FlexCubeEnvironment(True, True) #set True for OpenGL output, True for realtime calculation while clients are watching
    # create task
    task = WalkTask(env)
    # create controller network
    net = buildNetwork(len(task.getObservation()), 2, env.actLen, outclass=TanhLayer)
    # create agent with controller and learner
    agent = FiniteDifferenceAgent(net, SPLA())
    # learning options
    agent.learner.gd.alpha = 0.2 #step size of \mu adaption
    agent.learner.gdSig.alpha = 0.085 #step size of \sigma adaption
    agent.learner.gd.momentum = 0.0
    batch=2 #number of samples per gradient estimate
    #create experiment
    experiment = EpisodicExperiment(task, agent)
    prnts=1 #frequency of console output
    epis=5000000/batch/prnts
    
    #actual roll outs
    for updates in range(epis):
        for i in range(prnts):
            experiment.doEpisodes(batch) #execute #batch episodes
            agent.learn() #learn from the gather experience
            agent.reset() #reset agent and environment
        #print out related data
        print "Step: ", runs, "/", (updates+1)*batch*prnts, "Best: ", agent.learner.best, "Base: ", agent.learner.baseline, "Reward: ", agent.learner.reward   
        print ""
        #if updates/100 == float(updates)/100.0:
        #    saveWeights("walk.wgt", agent.learner.original)        
