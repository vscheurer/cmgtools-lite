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
parser.add_option("-i","--input",dest="input",help="inputJSON")

(options,args) = parser.parse_args()

def returnString(func,options):
    varName="MH"
    if func.GetName().find("pol")!=-1:
        st='0'
        for i in range(0,func.GetNpar()):
            st=st+"+("+str(func.GetParameter(i))+")"+(("*"+varName)*i)
        return st    
    elif func.GetName().find("log")!=-1:
        return "("+str(func.GetParameter(0))+")+("+str(func.GetParameter(1))+")*log("+varName+")"
    else:
        return ""



samples={}



f=open(options.input)
info=json.load(f)



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
            dataPlotters[-1].setupFromFile(args[0]+'/'+fname+'.pck')
#            dataPlotters[-1].addCorrectionFactor('xsec','tree')
#            dataPlotters[-1].addCorrectionFactor('genWeight','tree')
            dataPlotters[-1].addCorrectionFactor('puWeight','tree')
    



data=MergedPlotter(dataPlotters)

h = data.drawTH2(options.vary+':'+options.varx,options.cut,str(options.lumi),options.binsx,options.minx,options.maxx,50,600,5000) 
histo=copy.deepcopy(h)
fitter=Fitter(['MH','m'])
fitter.w.var("m").setVal((options.maxx-options.minx)/2.0)
fitter.w.var("m").setMax(options.maxx)
fitter.w.var("m").setMin(options.minx)
fitter.w.var("MH").setVal(1000)
fitter.w.var("MH").setMax(5000)
fitter.w.var("MH").setMin(600)



fitter.w.factory("mean0[0,-20,20]")        
fitter.w.factory("mean1[0,-0.002,0.002]")        

fitter.w.factory("expr::meanS('{val}+mean0+mean1&MH',mean0,mean1,MH)".format(val=info['mean']))

fitter.w.factory("sigma0[0,-5,5]")        
fitter.w.factory("sigma1[0,-0.0005,0.0005]")        
fitter.w.factory("expr::sigmaS('{val}+sigma0+sigma1*MH',sigma0,sigma1,,MH)".format(val=info['sigma']))

fitter.w.factory("alpha[0,-1,1]")        
fitter.w.factory("expr::alphaS('{val}+alpha',alpha,MH)".format(val=info['alpha']))

fitter.w.factory("alpha2[0,-1,1]")        
fitter.w.factory("expr::alpha2S('{val}+alpha2',alpha2,MH)".format(val=info['alpha2']))

fitter.w.factory("expr::n1('{val}',MH)".format(val=info['n']))
fitter.w.factory("expr::n2('{val}',MH)".format(val=info['n2']))


peak = ROOT.RooDoubleCB('model','modelS',fitter.w.var("m"),fitter.w.function('meanS'),fitter.w.function('sigmaS'),fitter.w.function('alphaS'),fitter.w.function('n1'),fitter.w.function("alpha2S"),fitter.w.function("n2"))
getattr(fitter.w,'import')(peak,ROOT.RooFit.Rename('model'))
fitter.importBinnedData(histo,['m','MH'],'data')   
fitter.fit('model','data',[ROOT.RooFit.SumW2Error(0),ROOT.RooFit.ConditionalObservables(ROOT.RooArgSet(fitter.w.var("MH")))])
#chi=fitter.projectionCond("model","data","m","MH","debugfitMJJTop_"+options.output+".png")
    


m0,cErr=fitter.fetch('mean0')
m1,cErr=fitter.fetch('mean1')
info['mean']="("+info['mean']+"+("+str(m0)+"+("+str(m1)+")*MH))"

m0,cErr=fitter.fetch('sigma0')
m1,cErr=fitter.fetch('sigma1')
info['sigma']="("+info['sigma']+"+("+str(m0)+"+("+str(m1)+")*MH))"


for var in ['alpha','alpha2']:

    c,cErr=fitter.fetch(var)
    info[var]="("+info[var]+"+("+str(c)+"))"

f=open(options.output+".json","w")
json.dump(info,f)
f.close()
#return graphs



    
    
    



