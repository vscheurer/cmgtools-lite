#!/usr/bin/env python
import ROOT
from array import array
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log
import os, sys, re, optparse,pickle,shutil,json
import json
from CMGTools.VVResonances.plotting.tdrstyle import *
setTDRStyle()
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter

parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output",default='')
parser.add_option("-s","--samples",dest="samples",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for yield in gen sample",default='')
parser.add_option("-d","--isData",dest="data",type=int,help="isData",default=1)
parser.add_option("-v","--vars",dest="vars",help="variable for gen",default='')
parser.add_option("-b","--binsx",dest="binsx",help="bins",default='')
parser.add_option("-B","--binsy",dest="binsy",help="conditional bins split by comma",default='')
parser.add_option("-g","--genVars",dest="genVars",help="variable for gen",default='')



(options,args) = parser.parse_args()


random=ROOT.TRandom3(101082)


def randomSample(dataset,N=5000):
    newdata=ROOT.RooDataSet("gen","gen",dataset.get(),'weight')
    entries=dataset.numEntries()
    if entries<N:
        return dataset
    sampled=[]
    while len(sampled)<N:
        i=int(random.Rndm()*entries)
        if not (i in sampled):
            line=dataset.get(i)
            newdata.add(line,dataset.weight())
            sampled.append(i)
    return newdata

    


def returnHisto(name,w,options):
    histo=w.pdf("model").createHistogram(options.var,w.var(options.var).getBins())
    histo.SetName(name)
    histo.Scale(1.0/histo.Integral())
    return histo


sampleTypes=options.samples.split(',')
dataPlotters=[]

for filename in os.listdir(args[0]):
    for sampleType in sampleTypes:
        if filename.find(sampleType)!=-1:
            fnameParts=filename.split('.')
            fname=fnameParts[0]
            ext=fnameParts[1]
            if ext.find("root") ==-1:
                continue
            dataPlotters.append(TreePlotter(args[0]+'/'+fname+'.root','tree'))
            if options.data==0 or options.data==2:
                dataPlotters[-1].setupFromFile(args[0]+'/'+fname+'.pck')
                dataPlotters[-1].addCorrectionFactor('xsec','tree')
#                dataPlotters[-1].addCorrectionFactor('genWeight','tree')
                dataPlotters[-1].addCorrectionFactor('puWeight','tree')
if options.data==2:
    sigmas=[]
    for d in dataPlotters:
        sigmas.append(d.tree.GetMaximum("xsec")/d.weightinv)
    sigmaW=max(sigmas)
    for p in dataPlotters:
        p.addCorrectionFactor(1.0/sigmaW,'flat')
data=MergedPlotter(dataPlotters)



binsxStr=options.binsx.split(',')
binsx=[]
for b in binsxStr:
    binsx.append(float(b))

binsyStr=options.binsy.split(',')
binsy=[]
for b in binsyStr:
    binsy.append(float(b))
    

binsz=[]
for b in range(0,101):
    binsz.append(0.5+b/100.0)


scalexHisto=ROOT.TH2F("scalexHisto","scaleHisto",len(binsx)-1,array('d',binsx),len(binsy)-1,array('d',binsy))
resxHisto=ROOT.TH2F("resxHisto","resHisto",len(binsx)-1,array('d',binsx),len(binsy)-1,array('d',binsy))

scaleyHisto=ROOT.TH2F("scaleyHisto","scaleHisto",len(binsx)-1,array('d',binsx),len(binsy)-1,array('d',binsy))
resyHisto=ROOT.TH2F("resyHisto","resHisto",len(binsx)-1,array('d',binsx),len(binsy)-1,array('d',binsy))

variables=options.vars.split(',')
genVariables=options.genVars.split(',')


gaussian=ROOT.TF1("gaussian","gaus",0.5,1.5)


f=ROOT.TFile(options.output,"RECREATE")
f.cd()


superHX=data.drawTH3Binned(variables[0]+'/'+genVariables[0]+':'+variables[1]+':'+variables[0],options.cut,"1",binsx,binsy,binsz)
superHY=data.drawTH3Binned(variables[1]+'/'+genVariables[1]+':'+variables[1]+':'+variables[0],options.cut,"1",binsx,binsy,binsz)

for i in range(1,superHX.GetNbinsX()+1):
    for j in range(1,superHX.GetNbinsY()+1):
        bin=scalexHisto.GetBin(i,j)

        tmp=superHX.ProjectionZ("q",i,i,j,j)
        scalexHisto.SetBinContent(bin,tmp.GetMean())
        scalexHisto.SetBinError(bin,tmp.GetMeanError())
        resxHisto.SetBinContent(bin,tmp.GetRMS())
        resxHisto.SetBinError(bin,tmp.GetRMSError())

        tmp=superHY.ProjectionZ("q",i,i,j,j)
        scaleyHisto.SetBinContent(bin,tmp.GetMean())
        scaleyHisto.SetBinError(bin,tmp.GetMeanError())
        resyHisto.SetBinContent(bin,tmp.GetRMS())
        resyHisto.SetBinError(bin,tmp.GetRMSError())

        
        
scalexHisto.Write()
scaleyHisto.Write()
resxHisto.Write()
resyHisto.Write()
superHX.Write("dataX")
superHY.Write("dataY")
f.Close()    
