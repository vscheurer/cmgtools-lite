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

(options,args) = parser.parse_args()



def mirror(histo,histoNominal,name):
    newHisto =copy.deepcopy(histoNominal) 
    newHisto.SetName(name)
    intNominal=histoNominal.Integral()
    intUp = histo.Integral()
    for i in range(1,histo.GetNbinsX()+1):
        up=histo.GetBinContent(i)/intUp
        nominal=histoNominal.GetBinContent(i)/intNominal
        newHisto.SetBinContent(i,nominal*nominal/up)
    return newHisto        


def smoothTailOLD(hist):
    #smart smoother ! Find the last hit with data.
    #fIT BEFORE THAT
    #eXTRAPOLATE AFTER THAT

    bin_1200=hist.GetXaxis().FindBin(1200)
    if bin_1200>=hist.GetNbinsX()+1:
        return

    if hist.Integral()==0:
        print "Well we have  0 integrl for the hist ",hist.GetName()
        return
#    expo=ROOT.TF1("expo","[0]*(1-pow(x/13000.,[1]))/pow(x/13000.0,[2]+0.0*TMath::Log(x/13000.0))",1000,8000)
#    expo.SetParameters(1,1,1)
#    expo.SetParLimits(0,0,1e+20)
#    expo.SetParLimits(1,0,100)
#    expo.SetParLimits(2,0,100)

    expo=ROOT.TF1("func","expo",0,5000)
    for j in range(1,hist.GetNbinsX()+1):
        if hist.GetBinContent(j)/hist.Integral()<0.0005:
            hist.SetBinError(j,1.8)

    hist.Fit(expo,"","",1200,8000)
    hist.Fit(expo,"","",1200,8000)
    for j in range(1,hist.GetNbinsX()+1):
        x=hist.GetXaxis().GetBinCenter(j)
        if x>1500:
            hist.SetBinContent(j,expo.Eval(x))

def smoothTail(hist):

    bin_1200=hist.GetXaxis().FindBin(1200)
    if bin_1200>=hist.GetNbinsX()+1:
        return

    if hist.Integral()==0:
        print "Well we have  0 integrl for the hist ",hist.GetName()
        return
    expo=ROOT.TF1("func","expo",0,5000)
    for j in range(1,hist.GetNbinsX()+1):
        if hist.GetBinContent(j)/hist.Integral()<0.0005:
            hist.SetBinError(j,1.8)

    hist.Fit(expo,"","",1200,8000)
    hist.Fit(expo,"","",1200,8000)
    for j in range(1,hist.GetNbinsX()+1):
        x=hist.GetXaxis().GetBinCenter(j)
        if x>1500:
            hist.SetBinContent(j,expo.Eval(x))





random=ROOT.TRandom3(101082)


sampleTypes=options.samples.split(',')
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
            dataPlotters[-1].addCorrectionFactor('lnujj_sf','branch')
            dataPlotters[-1].addCorrectionFactor('lnujj_btagWeight','branch')
            dataPlotters[-1].filename=fname

            dataPlottersNW.append(TreePlotter(args[0]+'/'+fname+'.root','tree'))
            dataPlottersNW[-1].addCorrectionFactor('puWeight','tree')
            dataPlottersNW[-1].addCorrectionFactor('lnujj_sf','branch')
            dataPlottersNW[-1].addCorrectionFactor('lnujj_btagWeight','branch')
            dataPlottersNW[-1].filename=fname

data=MergedPlotter(dataPlotters)


fcorr=ROOT.TFile(options.res)

scale=fcorr.Get("scale"+options.resHisto+"Histo")
res=fcorr.Get("res"+options.resHisto+"Histo")

ptBins=[0,150,200,250,300,350,400,450,500,550,600,700,800,900,1000,1500,2000,5000]

###Make res up and down
resUp = ROOT.TH1F(res)
resUp.SetName("resUp")
for i in range(1,res.GetNbinsX()+1):
    resUp.SetBinContent(i,res.GetBinContent(i)+0.3)




scaleUp = ROOT.TH1F(scale)
scaleUp.SetName("scaleUp")
scaleDown = ROOT.TH1F(scale)
scaleDown.SetName("scaleDown")
for i in range(1,res.GetNbinsX()+1):
    scaleUp.SetBinContent(i,scale.GetBinContent(i)+0.3)
    scaleDown.SetBinContent(i,scale.GetBinContent(i)-0.3)


#scaleLogUp = ROOT.TH1F(scale)
#scaleLogUp.SetName("scaleLogUp")
#scaleLogDown = ROOT.TH1F(scale)
#scaleLogDown.SetName("scaleLogDown")
#for i in range(1,scale.GetNbinsX()+1):
#    x=scale.GetXaxis().GetBinCenter(i)
#    scaleLogUp.SetBinContent(i,scale.GetBinContent(i)*(1+0.05*log(x)))
#    scaleLogDown.SetBinContent(i,scale.GetBinContent(i)*(1-0.05*log(x)))




ptBins=[200,300,400,500,600,700,800,1000,1500,2000,3000,5000]

###Make pt spectrum
#print 'Making W Pt spectra for reweighting'
#wptNominal=data.drawTH1Binned("lnujj_l1_pt","lnujj_LV_mass>600",'1',ptBins)
#wptUp=data.drawTH1Binned("1.3*lnujj_l1_pt","lnujj_LV_mass>600",'1',ptBins)
#wptDown=data.drawTH1Binned("0.7*lnujj_l1_pt","lnujj_LV_mass>600&&(0.7*lnujj_l1_pt)>200",'1',ptBins)
#wptNominal.Scale(1.0/wptNominal.Integral())
#wptUp.Scale(1.0/wptUp.Integral())
#wptDown.Scale(1.0/wptDown.Integral())
#wptUp.Divide(wptNominal)
#wptDown.Divide(wptNominal)

#print 'Making  Pt spectra for reweighting'
#ptNominal=data.drawTH1Binned("lnujj_l2_gen_pt","lnujj_LV_mass>600",'1',ptBins)
#ptUp=data.drawTH1Binned("1.3*lnujj_l2_gen_pt","lnujj_LV_mass>600",'1',ptBins)
#ptDown=data.drawTH1Binned("0.7*lnujj_l2_gen_pt","lnujj_LV_mass>600&&(0.7*lnujj_l2_gen_pt)>100",'1',ptBins)
#ptNominal.Scale(1.0/ptNominal.Integral())
#ptUp.Scale(1.0/ptUp.Integral())
#ptDown.Scale(1.0/ptDown.Integral())
#ptUp.Divide(ptNominal)
#ptDown.Divide(ptNominal)





#print 'Making quark gluon spectra for reweighting'
#partonFlavour=data.drawTH1Binned("lnujj_l2_partonFlavour",options.cut,'1',[0.,20.,22])
#quarkGluonUp=data.drawTH1Binned("lnujj_l2_partonFlavour",options.cut,'1',[0.,20.,22])
#quarkGluonDown=data.drawTH1Binned("lnujj_l2_partonFlavour",options.cut,'1',[0.,20.,22])
#partonFlavour.Scale(1.0/partonFlavour.Integral())
#quarkGluonUp.Scale(1.0/quarkGluonUp.Integral())
#quarkGluonDown.Scale(1.0/quarkGluonDown.Integral())
#quarks=partonFlavour.GetBinContent(1)
#offset=1
#quarkGluonUp.SetBinContent(1,quarkGluonUp.GetBinContent(1)*(1+offset))
#quarkGluonUp.SetBinContent(2,1-quarkGluonUp.GetBinContent(1))
#offset=-1
#quarkGluonDown.SetBinContent(1,quarkGluonDown.GetBinContent(1)*(1+offset))
#quarkGluonDown.SetBinContent(2,1-quarkGluonDown.GetBinContent(1))
#quarkGluonUp.Divide(partonFlavour)
#quarkGluonDown.Divide(partonFlavour)


#print 'Making Tail spectra for reweighting'
#tailSyst=0.0003
#tailUp=ROOT.TH1F("tailUp","tailUp",options.binsx,options.minx,options.maxx)
#tailDown=ROOT.TH1F("tailDown","tailDown",options.binsx,options.minx,options.maxx)
#for i in range(1,tailUp.GetNbinsX()+1):
#    x=tailUp.GetXaxis().GetBinCenter(i)
#    if x<2500:
#        tailUp.SetBinContent(i,1.0)
#        tailDown.SetBinContent(i,1.0)
#    else:
#        tailUp.SetBinContent(i,exp(tailSyst*(x-2500)))
#        tailDown.SetBinContent(i,1/tailUp.GetBinContent(i))



histogram=ROOT.TH1F("histo","histo",options.binsx,options.minx,options.maxx)
histogram.Sumw2()
histogram_res_up=ROOT.TH1F("histo_ResUp","histo",options.binsx,options.minx,options.maxx)
histogram_res_up.Sumw2()
histogram_res_down=ROOT.TH1F("histo_ResDown","histo",options.binsx,options.minx,options.maxx)
histogram_res_down.Sumw2()
histogram_scale_up=ROOT.TH1F("histo_ScaleUp","histo",options.binsx,options.minx,options.maxx)
histogram_scale_up.Sumw2()
histogram_scale_down=ROOT.TH1F("histo_ScaleDown","histo",options.binsx,options.minx,options.maxx)
histogram_scale_down.Sumw2()

histogram_top_up=ROOT.TH1F("histo_TOPUp","histo",options.binsx,options.minx,options.maxx)
histogram_top_up.Sumw2()
histogram_top_down=ROOT.TH1F("histo_TOPDown","histo",options.binsx,options.minx,options.maxx)
histogram_top_down.Sumw2()


histogram_scaleLog_up=ROOT.TH1F("histo_ScaleLogUp","histo",options.binsx,options.minx,options.maxx)
histogram_scaleLog_up.Sumw2()
histogram_scaleLog_down=ROOT.TH1F("histo_ScaleLogDown","histo",options.binsx,options.minx,options.maxx)
histogram_scaleLog_down.Sumw2()


histogram_pt_up=ROOT.TH1F("histo_PTUp","histo",options.binsx,options.minx,options.maxx)
histogram_pt_up.Sumw2()
histogram_pt_down=ROOT.TH1F("histo_PTDown","histo",options.binsx,options.minx,options.maxx)
histogram_pt_down.Sumw2()

histogram_wpt_up=ROOT.TH1F("histo_WPTUp","histo",options.binsx,options.minx,options.maxx)
histogram_wpt_up.Sumw2()

histogram_wpt_down=ROOT.TH1F("histo_WPTDown","histo",options.binsx,options.minx,options.maxx)
histogram_wpt_down.Sumw2()

histogram_qg_up=ROOT.TH1F("histo_GluonUp","histo",options.binsx,options.minx,options.maxx)
histogram_qg_up.Sumw2()

histogram_qg_down=ROOT.TH1F("histo_GluonDown","histo",options.binsx,options.minx,options.maxx)
histogram_qg_down.Sumw2()

histogram_tail_up=ROOT.TH1F("histo_TailUp","histo",options.binsx,options.minx,options.maxx)
histogram_tail_up.Sumw2()

histogram_tail_down=ROOT.TH1F("histo_TailDown","histo",options.binsx,options.minx,options.maxx)
histogram_tail_down.Sumw2()

histograms=[
    histogram,
    histogram_res_up,
#    histogram_res_down,
    histogram_scale_up,
    histogram_scale_down,
    histogram_top_up,
    histogram_top_down,
#    histogram_scaleLog_up,
#    histogram_scaleLog_down,
#    histogram_pt_up,
#    histogram_pt_down,
#    histogram_wpt_up,
#    histogram_wpt_down,
#    histogram_qg_up,
#    histogram_qg_down,
#    histogram_tail_up,
#    histogram_tail_down,

]

#ok lets populate!




for plotter,plotterNW in zip(dataPlotters,dataPlottersNW):
    histI=plotter.drawTH1(options.var,options.cut,"1",1,0,1000000000)
    norm=histI.Integral()
    #nominal
    histTMP=ROOT.TH1F("histoTMP","histo",options.binsx,options.minx,options.maxx)
    if options.var != 'lnujj_gen_partialMass':
        dataset=plotterNW.makeDataSet('lnujj_l1_pt,lnujj_gen_partialMass,lnujj_l2_partonFlavour,lnujj_l2_gen_pt,'+options.var,options.cut,-1)
    else:
        dataset=plotterNW.makeDataSet('lnujj_l1_pt,lnujj_l2_partonFlavour,lnujj_l2_gen_pt,'+options.var,options.cut,-1)
    datamaker=ROOT.cmg.GaussianSumTemplateMaker1D(dataset,options.var,'lnujj_l2_gen_pt',scale,res,histTMP);
    if histTMP.Integral()>0:
        histTMP.Scale(histI.Integral()/histTMP.Integral())
        histogram.Add(histTMP)
        if "TT" in plotterNW.filename:
            histogram_top_up.Add(histTMP,2.0)
            histogram_top_down.Add(histTMP,0.5)
        else:
            histogram_top_up.Add(histTMP,1.0)
            histogram_top_down.Add(histTMP,1.0)

    histTMP.Delete()


    #res Up
    histTMP=ROOT.TH1F("histoTMP","histo",options.binsx,options.minx,options.maxx)
    datamaker=ROOT.cmg.GaussianSumTemplateMaker1D(dataset,options.var,'lnujj_l2_gen_pt',scale,resUp,histTMP);
    if histTMP.Integral()>0:
        histTMP.Scale(histI.Integral()/histTMP.Integral())
        histogram_res_up.Add(histTMP)
    histTMP.Delete()


    #scale Up
    histTMP=ROOT.TH1F("histoTMP","histo",options.binsx,options.minx,options.maxx)
    datamaker=ROOT.cmg.GaussianSumTemplateMaker1D(dataset,options.var,'lnujj_l2_gen_pt',scaleUp,res,histTMP);
    if histTMP.Integral()>0:
        histTMP.Scale(histI.Integral()/histTMP.Integral())
        histogram_scale_up.Add(histTMP)
    histTMP.Delete()


    #scale Down
    histTMP=ROOT.TH1F("histoTMP","histo",options.binsx,options.minx,options.maxx)
    datamaker=ROOT.cmg.GaussianSumTemplateMaker1D(dataset,options.var,'lnujj_l2_gen_pt',scaleDown,res,histTMP);
    if histTMP.Integral()>0:
        histTMP.Scale(histI.Integral()/histTMP.Integral())
        histogram_scale_down.Add(histTMP)
    histTMP.Delete()


    histI.Delete()





f=ROOT.TFile(options.output,"RECREATE")
f.cd()

finalHistograms={}
for hist in histograms:
    hist.Write(hist.GetName()+"_raw")
    smoothTail(hist)
    hist.Write(hist.GetName())
    finalHistograms[hist.GetName()]=hist

histogram_res_down=mirror(finalHistograms['histo_ResUp'],finalHistograms['histo'],"histo_ResDown")
histogram_res_down.Write()


scaleUp.Write("scaleUp")
scaleDown.Write("scaleDown")
resUp.Write("resUp")
#resDown.Write("resDown")
#ptUp.Write("ptUp")
#ptDown.Write("ptDown")
#wptUp.Write("wptUp")
#wptDown.Write("wptDown")

#quarkGluonUp.Write("qgUp")
#quarkGluonDown.Write("qgDwn")

f.Close()




