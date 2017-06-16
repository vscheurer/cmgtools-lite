#!/usr/bin/env python

import ROOT
import optparse
from CMGTools.VVResonances.plotting.CMS_lumi import *
from CMGTools.VVResonances.plotting.tdrstyle import *
parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",default='limitPlot.root',help="Limit plot")

parser.add_option("-x","--minX",dest="minX",type=float,help="minimum x",default=1000.0)
parser.add_option("-X","--maxX",dest="maxX",type=float,help="maximum x",default=5000.0)
parser.add_option("-t","--titleX",dest="titleX",default='M_{X} [GeV]',help="title of x axis")
parser.add_option("-p","--period",dest="period",default='2015',help="period")
parser.add_option("-f","--final",dest="final",type=int, default=1,help="Preliminary or not")



#    parser.add_option("-x","--minMVV",dest="minMVV",type=float,help="minimum MVV",default=1000.0)
#    parser.add_option("-X","--maxMVV",dest="maxMVV",type=float,help="maximum MVV",default=13000.0)






(options,args) = parser.parse_args()
#define output dictionary



setTDRStyle()


f=ROOT.TFile(args[0])
limit=f.Get("limit")
data={}


for event in limit:
    if float(event.mh)<options.minX or float(event.mh)>options.maxX:
        continue
    
    if not (event.mh in data.keys()):
        data[event.mh]={}


    if event.quantileExpected<0:            
        data[event.mh]['obs']=event.limit
bandObs=ROOT.TGraph()
bandObs.SetName("bandObs")

N=0
for mass,info in data.iteritems():
    print 'Setting mass',mass,info

    if not 'obs' in info.keys():
        print 'Incomplete file'
        continue
    

    bandObs.SetPoint(N,mass,info['obs'])
    N=N+1


bandObs.Sort()


#plotting information

c=ROOT.TCanvas("c","c")
frame=c.DrawFrame(options.minX,ROOT.RooStats.SignificanceToPValue(4),options.maxX,0.5)



frame.GetXaxis().SetTitle(options.titleX)
frame.GetXaxis().SetTitleOffset(0.9)
frame.GetXaxis().SetTitleSize(0.05)
frame.GetYaxis().SetTitle("p-value")
frame.GetYaxis().SetTitleSize(0.05)
frame.GetYaxis().SetTitleOffset(1.15)
bandObs.SetLineWidth(3)
bandObs.SetLineColor(ROOT.kBlack)
bandObs.SetMarkerStyle(20)

c.cd()
frame.Draw()
c.Draw()
c.SetLogy()



line1=ROOT.TLine(options.minX,ROOT.RooStats.SignificanceToPValue(1),options.maxX,ROOT.RooStats.SignificanceToPValue(1))
line1.SetLineWidth(3)
line1.SetLineColor(ROOT.kRed)
line1.Draw()

line2=ROOT.TLine(options.minX,ROOT.RooStats.SignificanceToPValue(2),options.maxX,ROOT.RooStats.SignificanceToPValue(2))
line2.SetLineWidth(3)
line2.SetLineColor(ROOT.kRed)
line2.Draw()

line3=ROOT.TLine(options.minX,ROOT.RooStats.SignificanceToPValue(3),options.maxX,ROOT.RooStats.SignificanceToPValue(3))
line3.SetLineWidth(3)
line3.SetLineColor(ROOT.kRed)
line3.Draw()

line4=ROOT.TLine(options.minX,ROOT.RooStats.SignificanceToPValue(4),options.maxX,ROOT.RooStats.SignificanceToPValue(4))
line4.SetLineWidth(3)
line4.SetLineColor(ROOT.kRed)
line4.Draw()


if options.final:
    cmslabel_final(c,options.period,12)
else:
    cmslabel_prelim(c,options.period,12)

c.Update()
c.RedrawAxis()

bandObs.Draw("PLsame")
c.SaveAs(options.output+".png")    
c.SaveAs(options.output+".pdf")    

fout=ROOT.TFile(options.output+".root","RECREATE")
fout.cd()
c.Write()
bandObs.Write()
fout.Close()
f.Close()


