import PhysicsTools.HeppyCore.framework.config as cfg
import os

# Load just one signal from here
from CMGTools.VVResonances.samples.test_one_sample import *

mcSamples = signalSamples
# load triggers
from CMGTools.RootTools.samples.triggers_13TeV_DATA2016 import *

from CMGTools.TTHAnalysis.setup.Efficiencies import *
dataDir = "$CMSSW_BASE/src/CMGTools/VVResonances/data"

# Define splitting

for comp in mcSamples:
    comp.isMC = True
    comp.isData = False
    comp.splitFactor = 300
    comp.puFileMC=dataDir+"/pileup_MC.root"
    comp.puFileData=dataDir+"/pileup_DATA.root"
    comp.efficiency = eff2012
    comp.triggers=[]
#    comp.globalTag = "Summer15_25nsV6_MC"
