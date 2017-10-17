#!/usr/bin/env python
import ROOT
from array import array
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log,exp,sqrt
import os, sys, re, optparse,pickle,shutil,json
import copy
import json
from CMGTools.VVResonances.plotting.tdrstyle import *
setTDRStyle()
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
ROOT.gSystem.Load("libCMGToolsVVResonances")

parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output",default='')
parser.add_option("-r","--res",dest="res",help="res",default='')
parser.add_option("-H","--resHisto",dest="resHisto",help="res",default='')
parser.add_option("-s","--samples",dest="samples",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for yield in gen sample",default='')
parser.add_option("-v","--var",dest="var",help="variable for x",default='')
parser.add_option("-b","--bins",dest="binsx",type=int,help="bins",default=1)
parser.add_option("-x","--minx",dest="minx",type=float,help="bins",default=0)
parser.add_option("-X","--maxx",dest="maxx",type=float,help="conditional bins split by comma",default=1)
parser.add_option("-w","--weights",dest="weights",help="additional weights",default='')
parser.add_option("-u","--usegenmass",dest="usegenmass",action="store_true",help="use gen mass for det resolution",default=False)

(options,args) = parser.parse_args()     


def mirror(histo,histoNominal,name):
    newHisto =copy.deepcopy(histoNominal) 
    newHisto.SetName(name)
    intNominal=histoNominal.Integral()
    intUp = histo.Integral()
    for i in range(1,histo.GetNbinsX()+1):
        up=histo.GetBinContent(i)/intUp
        nominal=histoNominal.GetBinContent(i)/intNominal
        newHisto.SetBinContent(i,histoNominal.GetBinContent(i)*nominal/up)
    return newHisto      
	
def smoothTail(hist):

    bin_1200=hist.GetXaxis().FindBin(1200)
    if bin_1200>=hist.GetNbinsX()+1:
        return

    if hist.Integral()==0:
        print "Well we have  0 integrl for the hist ",hist.GetName()
        return
    expo=ROOT.TF1("func","expo",0,5000)
#    expo=ROOT.TF1("expo","[0]*((1-x/13000.0)^[1])/(x/13000.0)^([2]+[3]*log(x))",1000,8000)
#    expo.SetParameters(1,1,1,0)
#    expo.SetParLimits(0,0,1)
#    expo.SetParLimits(1,0.1,100)
#    expo.SetParLimits(2,0.1,100)
#    expo.SetParLimits(3,0.0,20)


    for j in range(1,hist.GetNbinsX()+1):
        if hist.GetBinContent(j)/hist.Integral()<0.0005:
            hist.SetBinError(j,1.8)

    hist.Fit(expo,"","",2000,8000)
    hist.Fit(expo,"","",2000,8000)
    for j in range(1,hist.GetNbinsX()+1):
        x=hist.GetXaxis().GetBinCenter(j)
        if x>2000:
            hist.SetBinContent(j,expo.Eval(x))

weights_ = options.weights.split(',')

random=ROOT.TRandom3(101082)

sampleTypes=options.samples.split(',')

print "Creating datasets for samples: " ,sampleTypes
dataPlotters=[]
dataPlottersNW=[]
for filename in os.listdir(args[0]):
    for sampleType in sampleTypes:
        if filename.find(sampleType)!=-1:
            fnameParts=filename.split('.')
            fname=fnameParts[0]
            ext=fnameParts[1]
            if ext.find("root") ==-1:
                continue
            dataPlotters.append(TreePlotter(args[0]+'/'+fname+'.root','tree'))
            dataPlotters[-1].setupFromFile(args[0]+'/'+fname+'.pck')
            dataPlotters[-1].addCorrectionFactor('xsec','tree')
            dataPlotters[-1].addCorrectionFactor('genWeight','tree')
            dataPlotters[-1].addCorrectionFactor('puWeight','tree')
            for w in weights_:
	     if w != '': dataPlotters[-1].addCorrectionFactor(w,'branch')
            dataPlotters[-1].filename=fname
            dataPlottersNW.append(TreePlotter(args[0]+'/'+fname+'.root','tree'))
            dataPlottersNW[-1].addCorrectionFactor('puWeight','tree')
            dataPlottersNW[-1].addCorrectionFactor('genWeight','tree')
            for w in weights_: 
             if w != '': dataPlottersNW[-1].addCorrectionFactor(w,'branch')
            dataPlottersNW[-1].filename=fname
	    
data=MergedPlotter(dataPlotters)

fcorr=ROOT.TFile(options.res)

scale = fcorr.Get("scale"+options.resHisto+"Histo")
res   = fcorr.Get("res"  +options.resHisto+"Histo")

#distribution of mjet from simulation --> use to validate kernel
mvv_nominal=ROOT.TH1F("mvv_nominal","mvv_nominal",options.binsx,options.minx,options.maxx)
mvv_nominal.Sumw2()

mvv_altshapeUp=ROOT.TH1F("mvv_altshapeUp","mvv_altshapeUp",options.binsx,options.minx,options.maxx)
mvv_altshapeUp.Sumw2()

mvv_altshape2=ROOT.TH1F("mvv_altshape2","mvv_altshape2",options.binsx,options.minx,options.maxx)
mvv_altshape2.Sumw2()

histogram_nominal=ROOT.TH1F("histo_nominal","histo_nominal",options.binsx,options.minx,options.maxx)
histogram_nominal.Sumw2()

histogram_altshapeUp=ROOT.TH1F("histo_altshapeUp","histo_altshapeUp",options.binsx,options.minx,options.maxx)
histogram_altshapeUp.Sumw2()

histogram_altshape2=ROOT.TH1F("histo_altshape2","histo_altshape2",options.binsx,options.minx,options.maxx)
histogram_altshape2.Sumw2()

histograms=[
    histogram_nominal,
    histogram_altshapeUp,
    histogram_altshape2,
    mvv_nominal,
    mvv_altshapeUp,
    mvv_altshape2
	]

maxEvents = -1
#ok lets populate!
for plotter,plotterNW in zip(dataPlotters,dataPlottersNW):

 #Nominal histogram Pythia8
 if plotter.filename.find(sampleTypes[0]) != -1: 
   print "Preparing nominal histogram for sampletype " ,sampleTypes[0]
   print "filename: ", plotter.filename, " preparing central values histo"
   
   #histI=plotter.drawTH1(options.var,options.cut,"1",1,0,1000000000)   
   histI2=plotter.drawTH1('jj_LV_mass',options.cut,"1",options.binsx,options.minx,options.maxx)
   
   dataset=plotterNW.makeDataSet('jj_gen_partialMass,jj_l1_gen_pt,jj_l1_gen_softDrop_mass',options.cut,maxEvents)     
   
   histTMP=ROOT.TH1F("histoTMP","histo",options.binsx,options.minx,options.maxx)   
   if not(options.usegenmass): 
    datamaker=ROOT.cmg.GaussianSumTemplateMaker1D(dataset,options.var,'jj_l1_gen_pt',scale,res,histTMP)
   else: datamaker=ROOT.cmg.GaussianSumTemplateMaker1D(dataset,options.var,'jj_l1_gen_softDrop_mass',scale,res,histTMP) 
   
   #if histTMP.Integral()>0:
   # histTMP.Scale(histI.Integral()/histTMP.Integral())
   # histogram_nominal.Add(histTMP)
   #if histI2.Integral()>0:
   # histI2.Scale(histI.Integral()/histI2.Integral())
   # mvv_nominal.Add(histI2)

   if histTMP.Integral()>0:
    histTMP.Scale(histI2.Integral()/histTMP.Integral())
    histogram_nominal.Add(histTMP)
    mvv_nominal.Add(histI2)
    
   #histI.Delete()
   histI2.Delete()
   histTMP.Delete()

 if len(sampleTypes)<2: continue
 elif plotter.filename.find(sampleTypes[1]) != -1: #alternative shape Herwig
   print "Preparing alternative shapes for sampletype " ,sampleTypes[1]
   print "filename: ", plotter.filename, " preparing alternate shape histo"
   
   #histI=plotter.drawTH1(options.var,options.cut,"1",1,0,1000000000)
   histI2=plotter.drawTH1('jj_LV_mass',options.cut,"1",options.binsx,options.minx,options.maxx)

   dataset=plotterNW.makeDataSet('jj_gen_partialMass,jj_l1_gen_pt,jj_l1_gen_softDrop_mass',options.cut,maxEvents)     
   
   histTMP=ROOT.TH1F("histoTMP","histo",options.binsx,options.minx,options.maxx)    
   if not(options.usegenmass): 
    datamaker=ROOT.cmg.GaussianSumTemplateMaker1D(dataset,options.var,'jj_l1_gen_pt',scale,res,histTMP)
   else: datamaker=ROOT.cmg.GaussianSumTemplateMaker1D(dataset,options.var,'jj_l1_gen_softDrop_mass',scale,res,histTMP) 
   
   #if histTMP.Integral()>0:
   # histTMP.Scale(histI.Integral()/histTMP.Integral())
   # histogram_altshapeUp.Add(histTMP)
   #if histI2.Integral()>0:
   # histI2.Scale(histI.Integral()/histI2.Integral())
   # mvv_altshapeUp.Add(histI2)

   if histTMP.Integral()>0:
    histTMP.Scale(histI2.Integral()/histTMP.Integral())
    histogram_altshapeUp.Add(histTMP)
    mvv_altshapeUp.Add(histI2)
    
   #histI.Delete()
   histI2.Delete()
   histTMP.Delete()
		          	      
 if len(sampleTypes)<3: continue
 elif plotter.filename.find(sampleTypes[2]) != -1: #alternative shape Pythia8+Madgraph (not used for syst but only for cross checks)
   print "Preparing alternative shapes for sampletype " ,sampleTypes[2]
   print "filename: ", plotter.filename, " preparing alternate shape histo"
   
   #histI=plotter.drawTH1(options.var,options.cut,"1",1,0,1000000000)
   histI2=plotter.drawTH1('jj_LV_mass',options.cut,"1",options.binsx,options.minx,options.maxx)

   dataset=plotterNW.makeDataSet('jj_gen_partialMass,jj_l1_gen_pt,jj_l1_gen_softDrop_mass',options.cut,maxEvents)     
   
   histTMP=ROOT.TH1F("histoTMP","histo",options.binsx,options.minx,options.maxx)    
   if not(options.usegenmass): 
    datamaker=ROOT.cmg.GaussianSumTemplateMaker1D(dataset,options.var,'jj_l1_gen_pt',scale,res,histTMP)
   else: datamaker=ROOT.cmg.GaussianSumTemplateMaker1D(dataset,options.var,'jj_l1_gen_softDrop_mass',scale,res,histTMP) 
   
   #if histTMP.Integral()>0:
   # histTMP.Scale(histI.Integral()/histTMP.Integral())
   # histogram_altshape2.Add(histTMP)
   #if histI2.Integral()>0:
   # histI2.Scale(histI.Integral()/histI2.Integral())
   # mvv_altshape2.Add(histI2)

   if histTMP.Integral()>0:
    histTMP.Scale(histI2.Integral()/histTMP.Integral())
    histogram_altshape2.Add(histTMP)
    mvv_altshape2.Add(histI2)
    
   #histI.Delete()
   histI2.Delete()
   histTMP.Delete()


print " ********** ALL DONE, now save in output file ", options.output
f=ROOT.TFile(options.output,"RECREATE")
f.cd()
finalHistograms={}
for hist in histograms:
 # hist.Write(hist.GetName()+"_raw")
 # smoothTail(hist)
 hist.Write(hist.GetName())
 finalHistograms[hist.GetName()]=hist

if len(sampleTypes)>1:
    histogram_altshapeDown=mirror(finalHistograms['histo_altshapeUp'],finalHistograms['histo_nominal'],"histo_altshapeDown")
    histogram_altshapeDown.Write()
    histograms.append(histogram_altshapeDown)
f.Close()


print "Drawing debugging plot ", "debug_"+options.output.replace(".root",".png") 
canv = ROOT.TCanvas("c1","c1",800,600)
leg = ROOT.TLegend(0.55010112,0.7183362,0.70202143,0.919833)
canv.cd()
for i,hist in enumerate(histograms):
 hist.SetLineWidth(3)
 hist.Rebin(2)
 hist.GetXaxis().SetTitle("Mass (GeV)")
 hist.GetXaxis().SetNdivisions(9,1,0)
 hist.GetYaxis().SetNdivisions(9,1,0)
 hist.GetYaxis().SetTitle("A.U")
 hist.GetXaxis().SetRangeUser(options.minx,options.maxx)
 hist.SetLineColor((i+1)*2)
 hist.DrawNormalized("HISTsame")
 leg.AddEntry(hist,hist.GetName(),"L")
leg.Draw("same")
canv.SaveAs("debug_"+options.output.replace(".root",".png") )


