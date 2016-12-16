#!/usr/bin/env python
import ROOT
from array import array
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log,exp,sqrt
import os, sys, re, optparse,pickle,shutil,json
import json
from CMGTools.VVResonances.plotting.tdrstyle import *
setTDRStyle()
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter

parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output",default='')
parser.add_option("-r","--res",dest="res",help="res",default='')
parser.add_option("-s","--samples",dest="samples",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for yield in gen sample",default='')
parser.add_option("-d","--isData",dest="data",type=int,help="isData",default=1)
parser.add_option("-v","--vars",dest="vars",help="variable for x",default='')
parser.add_option("-b","--binsx",dest="binsx",type=int,help="bins",default=1)
parser.add_option("-B","--binsy",dest="binsy",type=int,help="conditional bins split by comma",default=1)
parser.add_option("-x","--minx",dest="minx",type=float,help="bins",default=0)
parser.add_option("-X","--maxx",dest="maxx",type=float,help="conditional bins split by comma",default=1)
parser.add_option("-y","--miny",dest="miny",type=float,help="bins",default=0)
parser.add_option("-Y","--maxy",dest="maxy",type=float,help="conditional bins split by comma",default=1)





(options,args) = parser.parse_args()


random=ROOT.TRandom3(101082)




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
                dataPlotters[-1].addCorrectionFactor('genWeight','tree')
#                if filename.find("TTJets."):
#                    dataPlotters[-1].addCorrectionFactor('6383.9077','flat')
                dataPlotters[-1].addCorrectionFactor('puWeight','tree')
                dataPlotters[-1].addCorrectionFactor('lnujj_sf','branch')
#if options.data==2:
#    sigmas=[]
#    for d in dataPlotters:
#        sigmas.append(d.tree.GetMaximum("xsec")/d.weightinv)
#    sigmaW=max(sigmas)
#    for p in dataPlotters:
#        p.addCorrectionFactor(1.0/sigmaW,'flat')
data=MergedPlotter(dataPlotters)


fcorr=ROOT.TFile(options.res)
scale_x=fcorr.Get("scalexHisto")
scale_y=fcorr.Get("scaleyHisto")
res_x=fcorr.Get("resxHisto")
res_y=fcorr.Get("resyHisto")


variables=options.vars.split(',')


ptBins=[0,100,200,300,400,500,600,700,800,1000,1500,2000,5000]

###Make pt spectrum
ptNominal=data.drawTH1Binned("lnujj_l2_gen_pt",options.cut,'1',ptBins)
ptUp=data.drawTH1Binned("1.3*lnujj_l2_gen_pt",options.cut,'1',ptBins)
ptDown=data.drawTH1Binned("0.7*lnujj_l2_gen_pt",options.cut,'1',ptBins)
ptUp.Divide(ptNominal)
ptDown.Divide(ptNominal)


#make qg
quarks=data.drawTH1Binned("lnujj_l2_gen_pt",options.cut+"*(lnujj_l2_partonFlavour<21)",'1',ptBins)
gluons=data.drawTH1Binned("lnujj_l2_gen_pt",options.cut+"*(lnujj_l2_partonFlavour==21)",'1',ptBins)
both=data.drawTH1Binned("lnujj_l2_gen_pt",options.cut,'1',ptBins)
quarkFraction=data.drawTH1Binned("lnujj_l2_gen_pt",options.cut+"*(lnujj_l2_partonFlavour<21)",'1',ptBins)
quarkFraction.Divide(both)

quarks.Scale(1.0/quarks.Integral())
gluons.Scale(1.0/gluons.Integral())

qg_nominal=data.drawTH1Binned("lnujj_l2_gen_pt",options.cut+"*(lnujj_l2_partonFlavour<21)",'1',ptBins)
qg0_up=data.drawTH1Binned("lnujj_l2_gen_pt",options.cut+"*(lnujj_l2_partonFlavour<21)",'1',ptBins)
qg0_down=data.drawTH1Binned("lnujj_l2_gen_pt",options.cut+"*(lnujj_l2_partonFlavour==21)",'1',ptBins)

qg1_up=data.drawTH1Binned("lnujj_l2_gen_pt",options.cut+"*(lnujj_l2_partonFlavour<21)",'1',ptBins)
qg1_down=data.drawTH1Binned("lnujj_l2_gen_pt",options.cut+"*(lnujj_l2_partonFlavour==21)",'1',ptBins)



syst_frac0=0.05
syst_frac1=0.05/2000.


for  i in range(1,ptNominal.GetNbinsX()+1):
    frac = quarkFraction.GetBinContent(i)
    qg_nominal.SetBinContent(i, frac*quarks.GetBinContent(i)+(1-frac)*gluons.GetBinContent(i))

    frac = quarkFraction.GetBinContent(i)*(1+3*syst_frac0)
    qg0_up.SetBinContent(i, frac*quarks.GetBinContent(i)+(1-frac)*gluons.GetBinContent(i))
    frac = quarkFraction.GetBinContent(i)*(1-3*syst_frac0)
    qg0_down.SetBinContent(i, frac*quarks.GetBinContent(i)+(1-frac)*gluons.GetBinContent(i))

    x=ptNominal.GetXaxis().GetBinCenter(i)
    frac = quarkFraction.GetBinContent(i)*(1+3*syst_frac1*x)
    qg1_up.SetBinContent(i, frac*quarks.GetBinContent(i)+(1-frac)*gluons.GetBinContent(i))
    frac = quarkFraction.GetBinContent(i)*(1-3*syst_frac1*x)
    qg1_down.SetBinContent(i, frac*quarks.GetBinContent(i)+(1-frac)*gluons.GetBinContent(i))
    
qg0_up.Divide(qg_nominal)
qg0_down.Divide(qg_nominal)

qg1_up.Divide(qg_nominal)
qg1_down.Divide(qg_nominal)



#systs
histogram=ROOT.TH2F("histo","histo",options.binsx,options.minx,options.maxx,options.binsy,options.miny,options.maxy)

histogram_isr_up=ROOT.TH2F("histo_CMS_VV_LNuJ_ISRUp","histo",options.binsx,options.minx,options.maxx,options.binsy,options.miny,options.maxy)
histogram_isr_down=ROOT.TH2F("histo_CMS_VV_LNuJ_ISRDown","histo",options.binsx,options.minx,options.maxx,options.binsy,options.miny,options.maxy)

histogram_qg0_up=ROOT.TH2F("histo_CMS_VV_LNuJ_QGFraction0Up","histo",options.binsx,options.minx,options.maxx,options.binsy,options.miny,options.maxy)
histogram_qg0_down=ROOT.TH2F("histo_CMS_VV_LNuJ_QGFraction0Down","histo",options.binsx,options.minx,options.maxx,options.binsy,options.miny,options.maxy)

histogram_qg1_up=ROOT.TH2F("histo_CMS_VV_LNuJ_QGFraction1Up","histo",options.binsx,options.minx,options.maxx,options.binsy,options.miny,options.maxy)
histogram_qg1_down=ROOT.TH2F("histo_CMS_VV_LNuJ_QGFraction1Down","histo",options.binsx,options.minx,options.maxx,options.binsy,options.miny,options.maxy)


histograms=[
    histogram,
    histogram_isr_up,
    histogram_isr_down,
    histogram_qg0_up,
    histogram_qg0_down,
    histogram_qg1_up,
    histogram_qg1_down,
]





syst_sx0=0.05
syst_sx1=20.
syst_sy0=0.05
syst_sy1=1.0/100.


syst_rx0=0.1*0.1
syst_rx1=0.1*0.1*(600)
syst_ry0=0.15*0.15
syst_ry1=0.1*0.1*(30)


#ok lets populate!

stepMVV=(options.maxx-options.minx)/options.binsx
binsMVV=[options.minx-stepMVV]
for i in range(0,options.binsx+1):
    binsMVV.append(options.minx+i*stepMVV)
    
stepMJJ=(options.maxy-options.miny)/options.binsy
binsMJJ=[options.miny-stepMJJ]

for i in range(0,options.binsy+1):
    binsMJJ.append(options.miny+i*stepMJJ)

histogramGEN=data.drawTH3Binned('lnujj_l2_gen_pt:'+variables[1]+':'+variables[0],options.cut,'1',binsMVV,binsMJJ,ptBins)



#dataset=data.makeDataSet('lnujj_l2_gen_pt,'+variables[1]+','+variables[0],options.cut,-1)
#print 'dataset has ',dataset.numEntries(),'entries'
#entries=dataset.numEntries()


w=ROOT.RooWorkspace("w","w")
#w.factory("x[{mini},{maxi}]".format(mini=options.minx,maxi=options.maxx))
#w.factory("y[{mini},{maxi}]".format(mini=options.miny,maxi=options.maxy))
w.factory("x[-5000,5000]".format(mini=options.minx,maxi=options.maxx))
w.factory("y[-500,500]".format(mini=options.miny,maxi=options.maxy))

w.factory("mux[0,5000]")
w.factory("muy[0,5000]")
w.factory("sigmax[0,5000]")
w.factory("sigmay[0,5000]")
w.factory("RooGaussian::gausx(x,mux,sigmax)")
w.factory("RooGaussian::gausy(y,muy,sigmay)")
w.factory("PROD::kernel(gausx,gausy)")





totalBins=len(binsMJJ)*len(binsMVV)*len(ptBins)
N=0
for gi in  range(1,histogramGEN.GetNbinsX()+1):
    genx=histogramGEN.GetXaxis().GetBinCenter(gi)
    sx=scale_x.Interpolate(genx)
    rx=res_x.Interpolate(genx)
    for gj in  range(1,histogramGEN.GetNbinsY()+1):
        geny=histogramGEN.GetYaxis().GetBinCenter(gj)
        sy=scale_y.Interpolate(geny)
        ry=res_y.Interpolate(geny)
        for gk in  range(1,histogramGEN.GetNbinsZ()+1):
            genpt=histogramGEN.GetZaxis().GetBinCenter(gk)
            gbin=histogramGEN.GetBin(gi,gj,gk)
            weight=histogramGEN.GetBinContent(gbin)

            N=N+1
            if weight<=0:
                continue
            
            if N % 10000==0:
                print 'processed ',N,'out of',totalBins
            
            meanx=sx*genx
            meany=sy*geny
            sigmax=rx*genx
            sigmay=ry*geny
            
            weight_isr_up=ptUp.Interpolate(genpt)
            weight_isr_down=ptDown.Interpolate(genpt)
            weight_qg0_up=qg0_up.Interpolate(genpt)
            weight_qg0_down=qg0_down.Interpolate(genpt)
            weight_qg1_up=qg1_up.Interpolate(genpt)
            weight_qg1_down=qg0_down.Interpolate(genpt)

            w.var("mux").setVal(genx)
            w.var("muy").setVal(geny)
            w.var("sigmax").setVal(sigmax)
            w.var("sigmay").setVal(sigmay)

            for i in range(1,histogram.GetNbinsX()+1):
                for j in range(1,histogram.GetNbinsY()+1):
                    x=histogram.GetXaxis().GetBinCenter(i)
                    y=histogram.GetYaxis().GetBinCenter(j)
                    if ((x-genx)*(x-genx)+(y-geny)*(y-geny))>6*(sigmax*sigmax+sigmay*sigmay):
                        continue
                    w.var("x").setVal(x)
                    w.var("y").setVal(y)
                    rbin=histogram.GetBin(i,j)
                    oldWeight=histogram.GetBinContent(rbin)
                    histogram.SetBinContent(rbin,oldWeight+weight*w.pdf("kernel").getVal())
                    histogram_isr_up.SetBinContent(rbin,oldWeight+weight*weight_isr_up*w.pdf("kernel").getVal())
                    histogram_isr_down.SetBinContent(rbin,oldWeight+weight*weight_isr_down*w.pdf("kernel").getVal())
                    histogram_qg0_up.SetBinContent(rbin,oldWeight+weight*weight_qg0_up*w.pdf("kernel").getVal())
                    histogram_qg0_down.SetBinContent(rbin,oldWeight+weight*weight_qg0_down*w.pdf("kernel").getVal())
                    histogram_qg1_up.SetBinContent(rbin,oldWeight+weight*weight_qg1_up*w.pdf("kernel").getVal())
                    histogram_qg1_down.SetBinContent(rbin,oldWeight+weight*weight_qg1_down*w.pdf("kernel").getVal())
                    




f=ROOT.TFile(options.output,"RECREATE")
f.cd()
    
#get the X
for hist in histograms:
    proj=hist.ProjectionY('y_'+hist.GetName())
    proj.Write()

#Smooth the x!
expo=ROOT.TF1("expo","expo",1500,8000)

for hist in histograms:
    for i in range(1,hist.GetNbinsY()+1):
        proj=hist.ProjectionX("q",i,i)
        proj.Fit(expo,"","",2000,8000)
        for j in range(1,hist.GetNbinsX()+1):
            x=hist.GetXaxis().GetBinCenter(j)
            if x>3000:
                hist.SetBinContent(j,i,expo.Eval(x))

#conditional x
for hist in histograms:
    for i in range(1,hist.GetNbinsY()+1):
        proj=hist.ProjectionX("q",i,i)
        integral=proj.Integral()
        for j in range(1,hist.GetNbinsX()+1):
            hist.SetBinContent(j,i,hist.GetBinContent(j,i)/integral)
            

for hist in histograms:
    hist.Write('x_'+hist.GetName())

histogramGEN.Write("hgen")    
ptUp.Write('isr_up')
ptDown.Write('isr_down')
qg0_up.Write('qg0_up')
qg0_down.Write('qg0_down')
qg1_up.Write('qg1_up')
qg1_down.Write('qg1_down')
quarkFraction.Write('qg')

f.Close()




