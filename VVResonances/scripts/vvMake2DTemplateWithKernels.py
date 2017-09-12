#!/usr/bin/env python
import ROOT
from array import array
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log,exp,sqrt
import os, sys, re, optparse,pickle,shutil,json
import json
import copy
from CMGTools.VVResonances.plotting.tdrstyle import *
setTDRStyle()
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
ROOT.gSystem.Load("libCMGToolsVVResonances")
parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output",default='')
parser.add_option("-r","--res",dest="res",help="res",default='')
parser.add_option("-s","--samples",dest="samples",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for yield in gen sample",default='')
parser.add_option("-v","--vars",dest="vars",help="variable for x",default='')
parser.add_option("-b","--binsx",dest="binsx",type=int,help="bins",default=1)
parser.add_option("-B","--binsy",dest="binsy",type=int,help="conditional bins split by comma",default=1)
parser.add_option("-x","--minx",dest="minx",type=float,help="bins",default=0)
parser.add_option("-X","--maxx",dest="maxx",type=float,help="conditional bins split by comma",default=1)
parser.add_option("-y","--miny",dest="miny",type=float,help="bins",default=0)
parser.add_option("-Y","--maxy",dest="maxy",type=float,help="conditional bins split by comma",default=1)
parser.add_option("-w","--weights",dest="weights",help="additional weights",default='')


def mirror(histo,histoNominal,name):
    newHisto =copy.deepcopy(histoNominal) 
    newHisto.SetName(name)
    intNominal=histoNominal.Integral()
    intUp = histo.Integral()
    for i in range(1,histo.GetNbinsX()+1):
        for j in range(1,histo.GetNbinsY()+1):
            up=histo.GetBinContent(i,j)/intUp
            nominal=histoNominal.GetBinContent(i,j)/intNominal
            newHisto.SetBinContent(i,j,nominal*nominal/up)
    return newHisto       
	
def expandHisto(histo,options):
    histogram=ROOT.TH2F(histo.GetName(),"histo",options.binsx,options.minx,options.maxx,options.binsy,options.miny,options.maxy)
    for i in range(1,histo.GetNbinsX()+1):
        proje = histo.ProjectionY("q",i,i)
        graph=ROOT.TGraph(proje)
        for j in range(1,histogram.GetNbinsY()+1):
            x=histogram.GetYaxis().GetBinCenter(j)
            bin=histogram.GetBin(i,j)
            histogram.SetBinContent(bin,graph.Eval(x,0,"S"))
    return histogram
        


def conditional(hist):
    for i in range(1,hist.GetNbinsY()+1):
        proj=hist.ProjectionX("q",i,i)
        integral=proj.Integral()
        if integral==0.0:
            print 'SLICE WITH NO EVENTS!!!!!!!!',hist.GetName()
            continue
        for j in range(1,hist.GetNbinsX()+1):
            hist.SetBinContent(j,i,hist.GetBinContent(j,i)/integral)

def smoothTail(hist):
    hist.Scale(1.0/hist.Integral())
    expo=ROOT.TF1("expo","expo",1000,8000)
#    expo=ROOT.TF1("expo","[0]*(1-pow(x/13000.,[1]))/pow(x/13000.0,[2]+0.0*TMath::Log(x/13000.0))",1000,8000)
#    expo.SetParameters(1,-)
#    expo.SetParLimits(0,0,1)
#    expo.SetParLimits(1,0.1,100)
#    expo.SetParLimits(2,0.1,100)

    for i in range(1,hist.GetNbinsY()+1):
        proj=hist.ProjectionX("q",i,i)
#        for j in range(1,proj.GetNbinsX()+1):
#            if proj.GetBinContent(j)/proj.Integral()<0.0005:
#                proj.SetBinError(j,1.8)
        proj.Fit(expo,"","",2000,8000)
        proj.Fit(expo,"","",2000,8000)
        for j in range(1,hist.GetNbinsX()+1):
            x=hist.GetXaxis().GetBinCenter(j)
            if x>2500:
                hist.SetBinContent(j,i,expo.Eval(x))



(options,args) = parser.parse_args()

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
scale_x=fcorr.Get("scalexHisto")
scale_y=fcorr.Get("scaleyHisto")
res_x=fcorr.Get("resxHisto")
res_y=fcorr.Get("resyHisto")

variables=options.vars.split(',')


binsx=[]
for i in range(0,options.binsx+1):
    binsx.append(options.minx+i*(options.maxx-options.minx)/options.binsx)
binsy=[30.,40.,50.,60.,70.,80.,90.,100.,110.,120.,140.,150.,160.,180.,210., 240., 270., 300., 330., 360., 390., 410., 440., 470., 500., 530., 560., 590.,610.]    
ptBins=[0,150,200,250,300,350,400,450,500,550,600,700,800,900,1000,1500,2000,5000]




mjet_mvv			=	ROOT.TH2F("mjet_mvv"			,"mjet_mvv"			,len(binsx)-1,array('f',binsx),len(binsy)-1,array('f',binsy))
histogram			=	ROOT.TH2F("histo"				,"histo"			,len(binsx)-1,array('f',binsx),len(binsy)-1,array('f',binsy))
histogram_altshape1	=	ROOT.TH2F("histo_altshape1"		,"histo_altshape1"	,len(binsx)-1,array('f',binsx),len(binsy)-1,array('f',binsy))
histogram_altshape2	=	ROOT.TH2F("histo_altshape2up"	,"histo_altshape2up",len(binsx)-1,array('f',binsx),len(binsy)-1,array('f',binsy))


#systematics
histograms=[
    histogram,
    histogram_altshape1,
    histogram_altshape2
]


#ok lets populate!

maxEvents = -1
varsDataSet = 'jj_l1_gen_pt,'+variables[0]+','+variables[1]

for plotter,plotterNW in zip(dataPlotters,dataPlottersNW):
	# if plotter.filename.find("QCD_Pt_") ==-1: continue
	#Nominal histogram
	if plotter.filename.find(sampleTypes[0]) != -1:
		print "Preparing nominal histogram for sampletype " ,sampleTypes[0]
		print "filename: ", plotter.filename, " preparing central values histo"
		
		histI=plotter.drawTH1(variables[0],options.cut,"1",1,0,1000000000)
		norm=histI.Integral()
		#y:x
		histI2D=plotter.drawTH2Binned("jj_l1_softDrop_mass:jj_LV_mass",options.cut,"1",array('f',binsx),array('f',binsy),"M_{qV} mass","GeV","Softdrop mass","GeV","COLZ" )
		histTMP=ROOT.TH2F("histoTMP","histo",len(binsx)-1,array('f',binsx),len(binsy)-1,array('f',binsy))
		
		
		print " - Creating dataset - "
		dataset=plotterNW.makeDataSet(varsDataSet,options.cut,maxEvents)
		
		print " - Creating gaussian template - "
		datamaker=ROOT.cmg.GaussianSumTemplateMaker(dataset,variables[0],variables[1],'jj_l1_gen_pt',scale_x,scale_y,res_x,res_y,histTMP)
		
		if histTMP.Integral()>0:
			histTMP.Scale(histI.Integral()/histTMP.Integral())
			histogram.Add(histTMP)
			mjet_mvv.Add(histI2D)
			
		histTMP.Delete()
		
	#Alternative shape 1 (e.g Madgraph+Pythia8)
	elif plotter.filename.find(sampleTypes[1]) != -1:
		print "Preparing alternative shapes for sampletype " ,sampleTypes[1]
		print "filename: ", plotter.filename, " preparing alternate shape histo"

		histI=plotter.drawTH1(variables[0],options.cut,"1",1,0,1000000000)
		norm=histI.Integral()

		histTMP=ROOT.TH2F("histoTMP","histo",len(binsx)-1,array('f',binsx),len(binsy)-1,array('f',binsy))

		print " - Creating dataset - "
		dataset=plotterNW.makeDataSet(varsDataSet,options.cut,maxEvents)

		print " - Creating gaussian template - "
		datamaker=ROOT.cmg.GaussianSumTemplateMaker(dataset,variables[0],variables[1],'jj_l1_gen_pt',scale_x,scale_y,res_x,res_y,histTMP)

		if histTMP.Integral()>0:
			histTMP.Scale(histI.Integral()/histTMP.Integral())
			histogram_altshape1.Add(histTMP)

		histTMP.Delete()

	#Alternative shape 2 (e.g Herwig)
	elif plotter.filename.find(sampleTypes[2]) != -1:
		print "Preparing alternative shapes for sampletype " ,sampleTypes[2]
		print "filename: ", plotter.filename, " preparing alternate shape histo"

		histI=plotter.drawTH1(variables[0],options.cut,"1",1,0,1000000000)
		norm=histI.Integral()

		histTMP=ROOT.TH2F("histoTMP","histo",len(binsx)-1,array('f',binsx),len(binsy)-1,array('f',binsy))

		print " - Creating dataset - "
		dataset=plotterNW.makeDataSet(varsDataSet,options.cut,maxEvents)

		print " - Creating gaussian template - "
		datamaker=ROOT.cmg.GaussianSumTemplateMaker(dataset,variables[0],variables[1],'jj_l1_gen_pt',scale_x,scale_y,res_x,res_y,histTMP)

		if histTMP.Integral()>0:
			histTMP.Scale(histI.Integral()/histTMP.Integral())
			histogram_altshape2.Add(histTMP)

		histTMP.Delete()

f=ROOT.TFile(options.output,"RECREATE")
print "Finished producing histograms! Saving to" ,options.output
finalHistograms={}
f.cd()
for hist in histograms:
	print "Working on histogram " ,hist.GetName()
	hist.Write(hist.GetName()+"_coarse")
	#smooth
	print "Smoothing tail"
	smoothTail(hist)
	print "Creating conditional histogram"
	conditional(hist)
	print "Expanding...."
	expanded=expandHisto(hist,options)
	conditional(expanded)
	expanded.Write()
	finalHistograms[hist.GetName()]=expanded

mjet_mvv.Write()

##Mirror Herwig shape
histogram_altshape2down=mirror(finalHistograms['histo_altshape2up'],finalHistograms['histo'],"histo_altshape2down")
conditional(histogram_altshape2down)
histogram_altshape2down.Write()


# plotname = "debug_massBin%i_"%i+hist.GetName()+options.output.replace(".root",".png")
# print "Drawing debugging plot ", plotname
# canv = ROOT.TCanvas("c1","c1",800,600)
# canv.cd()
# hist.DrawNormalized("HISTsame")
# canv.SaveAs(plotname )
        
		
f.Close()




