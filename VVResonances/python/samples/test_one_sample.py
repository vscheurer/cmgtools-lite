from CMGTools.RootTools.samples.ComponentCreator import ComponentCreator
kreator = ComponentCreator()
signalSamples=[]

BulkGravToWWToWlepWhad_narrow_1000=kreator.makeMCComponent("BulkGravToWWToWlepWhad_narrow_1000", "/BulkGravToWWToWlepWhad_narrow_M-1000_13TeV-madgraph/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM", "CMS", ".*root",1.0)
signalSamples.append(BulkGravToWWToWlepWhad_narrow_1000)
