#!/usr/bin/env python

from __future__ import print_function, division

import os, sys, argparse

def setInConfig(configFileName, name, value):
    commandToPass = "sed \"s|^hardcoded_{name} = .*$|hardcoded_{name} = {value}|\" {configFileName} > tmp_{configFileName}".format(**locals())
    argvalueIsStr = (type(value) is str)
    if argvalueIsStr:
        commandToPass = "sed \"s|^hardcoded_{name} = .*$|hardcoded_{name} = \\\"{value}\\\"|\" {configFileName} > tmp_{configFileName}".format(**locals())
    # print("Passing command: {commandToPass}".format(**locals()))
    if(os.system(commandToPass) != 0):
        sys.exit("Unable to modify given input file {configFileName} and copy it to output".format(**locals()))
    else:
        if (os.system("mv tmp_{configFileName} {configFileName}".format(**locals())) != 0):
            sys.exit("Unable to rename tmp file to original")
    
DEFAULT_CFG = "ecal_dqm_sourceclient-offline_cfg.py"

parser=argparse.ArgumentParser(description = "Launch Ecal Offline CMSSW.")
parser.add_argument("--inputcfg", action='store', help="input cfg file", type=str, default=DEFAULT_CFG)
parser.add_argument("--outputcfg", action='store', help="output cfg file", type=str, default=DEFAULT_CFG)
parser.add_argument("--inputPath", action='store', help="If readRaw is set to its default value of False, the argument is interpreted as a path to a txt file with the list of input root files. Otherwise this argument is interpreted as a path to a folder containing a folder named runABCDEF which has all the raw data files.", type=str, default="inputFileList.txt")
parser.add_argument("--runNumber", action='store', help="run number", type=int, default=0)
parser.add_argument("--lumisToProcess", action='append', help="lumis to process from file", default=[])
# parser.add_argument("--eventToProcess", action='store', help="events to process from file", type=int, default=0)
parser.add_argument("--workflow", action='store', help="offline workflow", type=str, default="/All/Run2017/CentralDAQ")
parser.add_argument("--prescaleFactor", help="prescale factor", action='store', type=int, default=1)
parser.add_argument("--maxEvents", action='store', help="max number of events to analyze", type=int, default=-1)
parser.add_argument("--readRaw", action='store_true', help="True for RAW input, False for edm-formatted ROOT input. If true, Interpret inputPath as path to directory of which runABCDEF should be a subdirectory")
parser.add_argument("--verbosity", action='store', help="Verbosity", type=int, default=1)
inputArguments = parser.parse_args()

inputArgumentsDict = vars(inputArguments)
outputcfg = inputArgumentsDict['outputcfg']
del inputArgumentsDict['outputcfg']
inputcfg = inputArgumentsDict['inputcfg']
del inputArgumentsDict['inputcfg']
if (os.system("cp {inputcfg} tmp_{inputcfg}".format(**locals())) != 0):
    sys.exit("Unable to create temporary copy of {inputcfg}".format(**locals()))
for (argname, argvalue) in inputArgumentsDict.items():
    print ("Setting option {argname} to {argvalue}".format(**locals()))
    setInConfig("tmp_" + inputcfg, argname, argvalue)
if (os.system("mv tmp_{inputcfg} {outputcfg}".format(**locals())) != 0):
    sys.exit("Unable to move tmp_{inputcfg} to {outputcfg}".format(**locals()))
