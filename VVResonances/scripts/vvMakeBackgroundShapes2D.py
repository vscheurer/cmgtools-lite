#!/usr/bin/env python

import ROOT
from array import array
from CMGTools.VVResonances.plotting.TreePlotter import TreePlotter
from CMGTools.VVResonances.plotting.MergedPlotter import MergedPlotter
from CMGTools.VVResonances.statistics.Fitter import Fitter
from math import log,exp
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
parser.add_option("-B","--binsy",dest="binsy",type=int,help="bins in x",default=20)
parser.add_option("-y","--miny",dest="miny",type=float,help="minimum y",default=0)
parser.add_option("-Y","--maxy",dest="maxy",type=float, help="maximum y",default=160)
parser.add_option("-l","--lumi",dest="lumi",type=float, help="lumi",default=1)
parser.add_option("-p","--order",dest="order",type='string', help="order",default="order")
parser.add_option("-j","--json",dest="json",type='string', help="json file for MJJ",default="order")


(options,args) = parser.parse_args()

def returnString(func,options):
    varName="mjj"
    if func.GetName().find("pol")!=-1:
        st='0'
        for i in range(0,func.GetNpar()):
            st=st+"+("+str(func.GetParameter(i))+")"+(("*"+varName)*i)
        return st    
    elif func.GetName().find("log")!=-1:
        return str(func.GetParameter(0))+"+("+str(func.GetParameter(1))+")*log("+varName+")"
    else:
        return ""

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
            dataPlotters[-1].setupFromFile(args[0]+'/'+fname+'.pck')
            dataPlotters[-1].addCorrectionFactor('xsec','tree')
            dataPlotters[-1].addCorrectionFactor('genWeight','tree')
            dataPlotters[-1].addCorrectionFactor('puWeight','tree')
    

sigmas=[]
for d in dataPlotters:
    sigmas.append(d.tree.GetMaximum("xsec")/d.weightinv)
sigmaW=max(sigmas)
for p in dataPlotters:
    p.addCorrectionFactor(1.0/sigmaW,'flat')



data=MergedPlotter(dataPlotters)




orderInfo={}
orders=options.order.split('|')
for v in orders:
    sp=v.split(':')
    orderInfo[sp[0]] = int(sp[1])






h = data.drawTH2(options.vary+':'+options.varx,options.cut,str(options.lumi),options.binsx,options.minx,options.maxx,options.binsy,options.miny,options.maxy)
histo=copy.deepcopy(h)
 


fitter=Fitter(['M','mjj'])
fitter.w.var("M").setVal((options.maxx-options.minx)/2.0)
fitter.w.var("M").setMax(options.maxx)
fitter.w.var("M").setMin(options.minx)
fitter.w.var("mjj").setVal((options.maxy-options.miny)/2.0)
fitter.w.var("mjj").setMax(options.maxy)
fitter.w.var("mjj").setMin(options.miny)

#The MJ first that is trivial


jsonFile=open(options.json)
data=json.load(jsonFile)
jsonFile.close()

if data['type']=='erfexp':
    fitter.erfexp('modelJ','mjj')


    fitter.w.var("c_0").setVal(data['c_0'])
    fitter.w.var("c_0").setConstant(1)

    fitter.w.var("c_1").setVal(data['c_1'])
    fitter.w.var("c_1").setConstant(1)

    fitter.w.var("c_2").setVal(data['c_2'])
    fitter.w.var("c_2").setConstant(1)

if data['type']=='expo':
    fitter.expo('modelJ','mjj')
    fitter.w.var("c_0").setVal(data['c_0'])
    fitter.w.var("c_0").setConstant(1)

#now create the variables of the erfpow

formulas={}

for p,val in orderInfo.iteritems():
    STR='0'
    DEPS=['mjj']
    for i in range(0,val+1):
        if p=='p0':
            mini=-8.0
            maxi=-3.0
            mean=-5.0
            if i==1:
                mini=-0.02
                maxi=+0.02
                mean=0.

            if i>1:
                mini=-1.0/pow(150,i)
                maxi=+1.0/pow(150,i)
                mean=0.

        if p=='p1':
            mini=300.
            maxi=800.
            mean=519.
            if i==1:
                mini=-1.0
                maxi=+1.0
                mean=0.
            if i==2:
                mini=-0.01
                maxi=+0.01
                mean=0.
            elif i>2:
                mini=-200.0/pow(150,i)
                maxi=+200.0/pow(150,i)
                mean=0.
        if p=='p2':
            mini=100.
            maxi=300.
            mean=150.
            if i==1:
                mini=-0.5
                maxi=+0.5
                mean=0.
            if i==2:
                mini=-0.005
                maxi=+0.005
                mean=0.
            elif i>2:
                mini=-200.0/pow(150,i)
                maxi=+200.0/pow(150,i)
                mean=0.


        fitter.w.factory("{p}{i}[{mean},{mini},{maxi}]".format(p=p,i=i,mean=mean,mini=mini,maxi=maxi))
        STR=STR+"+("+p+str(i)+")"+(("*mjj")*i)
        DEPS.append(p+str(i))

    formulas[p]=STR
    fitter.w.factory("expr::{p}('{st}',{deps})".format(p=p,st=STR,deps=','.join(DEPS)))    


erfpow = ROOT.RooErfPowPdf('modelM','modelM',fitter.w.var('M'),fitter.w.function("p0"),fitter.w.function("p1"),fitter.w.function("p2"))
getattr(fitter.w,'import')(erfpow,ROOT.RooFit.Rename('modelM'))
fitter.w.factory("PROD::model(modelM|mjj,modelJ)")
fitter.importBinnedData(histo,["M",'mjj'],"data")
fitter.fit("model","data",[ROOT.RooFit.SumW2Error(1),ROOT.RooFit.NumCPU(8)])
fitter.w.writeToFile("debugWorkspace.root")


for p,val in orderInfo.iteritems():
    for i in range(0,val+1):
        c=fitter.w.var(p+str(i)).getVal()
        formulas[p]=formulas[p].replace(p+str(i),"("+str(c)+")")

outF=open(options.output,"w")
json.dump(formulas,outF)
outF.close()

#debug
c=ROOT.TCanvas("C")
frame=fitter.w.var("M").frame()
for val in [40.,50.,60.,70.,80.,90.,100.,110.,120.,130.,140.]:
    fitter.w.var("mjj").setVal(val)
    fitter.w.pdf("modelM").plotOn(frame)

frame.Draw()
c.SaveAs("debug_"+options.output+".png")



