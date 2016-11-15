#!/usr/bin/env python

import ROOT
from array import array
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log
import os, sys, re, optparse,pickle,shutil,json
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
import copy



parser = optparse.OptionParser()
parser.add_option("-s","--samples",dest="samples",default='',help="Type of sample")
parser.add_option("-c","--cut",dest="cut",help="Cut to apply for yield",default='')
parser.add_option("-o","--output",dest="output",help="Output ROOT",default='')
parser.add_option("-v","--varx",dest="varx",help="variablex",default='lnujj_LV_mass')
parser.add_option("-b","--binsx",dest="binsx",type=int,help="bins in x",default=1000)
parser.add_option("-x","--minx",dest="minx",type=float,help="minimum x",default=600)
parser.add_option("-X","--maxx",dest="maxx",type=float, help="maximum x",default=5000)
parser.add_option("-V","--vary",dest="vary",help="variablex",default='lnujj_l2_pruned_mass')
parser.add_option("-l","--lumi",dest="lumi",type=float, help="lumi",default=1)


(options,args) = parser.parse_args()





samples={}



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
#            dataPlotters[-1].addCorrectionFactor('genWeight','tree')
            dataPlotters[-1].addCorrectionFactor('puWeight','tree')
    



data=MergedPlotter(dataPlotters)



h = data.drawTH2(options.vary+':'+options.varx,options.cut,str(options.lumi),options.binsx,options.minx,options.maxx,100,600,5000) 
histo=copy.deepcopy(h)
fitter=Fitter(['m','M'])
fitter.w.var("m").setVal((options.maxx-options.minx)/2.0)
fitter.w.var("m").setMax(options.maxx)
fitter.w.var("m").setMin(options.minx)

fitter.jetResonanceNOEXP2D('model','m')
fitter.importBinnedData(histo,['m','M'],'data')   
fitter.fit('model','data',[ROOT.RooFit.SumW2Error(0),ROOT.RooFit.Minos(1),ROOT.RooFit.ConditionalObservables(ROOT.RooArgSet(fitter.w.var("M")))])
    


info={}

mean0,err=fitter.fetch('mean0')
mean1,err=fitter.fetch('mean1')

info['mean']='(({m0})+({m1})*MH)'.format(m0=mean0,m1=mean1)


sigma0,err=fitter.fetch('sigma0')
sigma1,err=fitter.fetch('sigma1')
sigma2,err=fitter.fetch('sigma2')

info['sigma']='(({m0})+({m1})*MH+({m2})*MH*MH)'.format(m0=sigma0,m1=sigma1,m2=sigma2)



alpha,err=fitter.fetch('alpha')
info['alpha']='({m0}+0.0*MH)'.format(m0=alpha)

n,err=fitter.fetch('n')
info['n']='({m0}+0*MH)'.format(m0=n)

alpha2,err=fitter.fetch('alpha2')
info['alpha2']='({m0}+0*MH)'.format(m0=alpha2)

n2,err=fitter.fetch('n2')
info['n2']='({m0}+0*MH)'.format(m0=n2)


f=open(options.output+".json","w")
json.dump(info,f)
f.close()
    



