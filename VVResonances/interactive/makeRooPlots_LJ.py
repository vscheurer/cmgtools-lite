from CMGTools.VVResonances.plotting.RooPlotter import *
from CMGTools.VVResonances.plotting.CMS_lumi import *

import ROOT
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")







plotter=RooPlotter("combined.root")    
plotter.fix("MH",1850)
plotter.fix("r",0.0)
plotter.prefit()
plotter.addContribution("XWW",True,"X #rightarrow WW",3,1,ROOT.kOrange+10,0,ROOT.kWhite)
plotter.addContribution("resW",False," W+V",2,1,ROOT.kBlack,1001,ROOT.kSpring-5)
plotter.addContribution("nonRes",False,"W+jets",2,1,ROOT.kBlack-3,1001,ROOT.kAzure-9,"_opt")


#for l in ['mu','e']:
#    for p in ['both']:
#        for c in ['vbf']:
#            plotter.drawProjection("MJ","m_{j} [GeV]",c+"_"+l+"_"+p+"_13TeV",1,0)
#            plotter.canvas.SaveAs("postfitMJJ"+c+"_"+l+"_"+p+".png")
#            plotter.drawProjection("MLNuJ","m_{VV} [GeV]",c+"_"+l+"_"+p+"_13TeV",1,0)
#            plotter.canvas.SaveAs("postfitMVV"+c+"_"+l+"_"+p+".png")



#plotter=RooPlotter("LNuJJ_topPreFit_HP.root")    
#plotter.prefit()
#plotter.addContribution("topRes",True,"t#bar{t}",1,1,ROOT.kRed,0,ROOT.kWhite)
#plotter.addContribution("topNonRes",False,"non-resonant t#bar{t}",1,1,ROOT.kBlack,1001,ROOT.kGreen-5)
#plotter.drawStack("MJ","m_{j} [GeV]","top_mu_HP_13TeV","top_mu_HP_13TeV")







