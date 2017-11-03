import ROOT
import os,sys
import time

cuts={}

cuts['common'] = '((HLT_JJ)*(run>500) + (run<500))*(njj>0&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_eeBadScFilter&&jj_LV_mass>700&&abs(jj_l1_eta-jj_l2_eta)<1.3&&jj_l1_softDrop_mass>0.)'
cuts['HP'] = '(jj_l1_tau2/jj_l1_tau1<0.35)'
cuts['LP'] = '(jj_l1_tau2/jj_l1_tau1>0.35&&jj_l1_tau2/jj_l1_tau1<0.75)'

cuts['nonres'] = '1'

purities=['HP','LP']
purities=['HP']

qWTemplate="QstarQW"
qZTemplate="QstarQZ"
BRqW=1.
BRqZ=1.

dataTemplate="JetHT"

nonResTemplate="QCD_Pt_3"


minMJJ=30.0
maxMJJ=610.0

minMVV=1000.0
maxMVV=7000.0

binsMJJ=290
binsMVV=160

cuts['acceptance']= "(jj_LV_mass>{minMVV}&&jj_LV_mass<{maxMVV}&&jj_l1_softDrop_mass>{minMJJ}&&jj_l1_softDrop_mass<{maxMJJ})".format(minMVV=minMVV,maxMVV=maxMVV,minMJJ=minMJJ,maxMJJ=maxMJJ)
#cuts['acceptanceGEN']= "(jj_l1_gen_softDrop_mass>{minMJJ}&&jj_l1_gen_softDrop_mass<{maxMJJ}&&jj_gen_partialMass>{minMVV}&&jj_gen_partialMass<{maxMVV})".format(minMJJ=25,maxMJJ=700,minMVV=700,maxMVV=10000)                
cuts['acceptanceGEN']='(jj_l1_gen_softDrop_mass>0&&jj_gen_partialMass>0)'

cuts['acceptanceMJJ']= "(jj_l1_softDrop_mass>{minMJJ}&&jj_l1_softDrop_mass<{maxMJJ})".format(minMJJ=minMJJ,maxMJJ=maxMJJ) 
#cuts['acceptanceGENMJJ']= "(jj_l1_gen_softDrop_mass>{minMJJ}&&jj_l1_gen_softDrop_mass<{maxMJJ}&&jj_LV_mass>{minMVV}&&jj_LV_mass<{maxMVV})".format(minMJJ=minMJJ-5,maxMJJ=maxMJJ+5,minMVV=minMVV,maxMVV=maxMVV)
cuts['acceptanceGENMJJ']= '(jj_l1_gen_softDrop_mass>0&&jj_gen_partialMass>0)'

def makeSignalShapesMVV(filename,template):
 cuts['sigVV'] = '((HLT_JJ)*(run>500) + (run<500))*(njj>0&&Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_eeBadScFilter&&abs(jj_l1_eta-jj_l2_eta)<1.3&&jj_l1_softDrop_mass>0.)'

 cut='*'.join([cuts['sigVV'],cuts['acceptanceMJJ']])
 rootFile=filename+"_MVV.root"
 cmd='vvMakeSignalMVVShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "jj_LV_mass"  samples'.format(template=template,cut=cut,rootFile=rootFile,minMJJ=minMJJ,maxMJJ=maxMJJ)
 os.system(cmd)
 jsonFile=filename+"_MVV.json"
 print 'Making JSON'
 cmd='vvMakeJSON.py  -o "{jsonFile}" -g "MEAN:pol1,SIGMA:pol2,ALPHA:pol3,N:pol0,SCALESIGMA:pol3,f:pol3" -m 1000 -M 6000  {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile)
 os.system(cmd)

def makeSignalShapesMJJ(filename,template):

 for p in purities:
  cut='*'.join([cuts['common'],cuts[p]])
  rootFile=filename+"_MJJ_"+p+".root"
  doExp=1
  if p=='HP':
      doExp=0
  cmd='vvMakeSignalMJJShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "jj_l1_softDrop_mass" -m {minMJJ} -M {maxMJJ} -e {doExp} -f "alpha:1.347" samples'.format(template=template,cut=cut,rootFile=rootFile,minMJJ=minMJJ,maxMJJ=maxMJJ,doExp=doExp)
  os.system(cmd)
  jsonFile=filename+"_MJJ_"+p+".json"

  if p=='HP':
   #cmd='vvMakeJSON.py  -o "{jsonFile}" -g "mean:pol4,sigma:pol4,alpha:pol3,n:pol0,alpha2:pol3,n2:pol0,slope:pol0,f:pol0" -m 1000 -M 6000  {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile)
   cmd='vvMakeJSON.py  -o "{jsonFile}" -g "mean:pol4,sigma:pol4,alpha:pol3,n:pol3,alpha2:pol3,n2:pol3" -m 1000 -M 6000  {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile)
  else:
   cmd='vvMakeJSON.py  -o "{jsonFile}" -g "mean:pol3,sigma:pol1,alpha:pol0,n:pol0,slope:pol1,f:laur4,alpha2:pol0,n2:pol0" -m 1000 -M 6000  {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile)

  os.system(cmd)

def makeSignalYields(filename,template,branchingFraction,sfP = {'HP':1.0,'LP':1.0}):
 	 
 for p in purities:
  cut = "*".join([cuts[p],cuts['common'],cuts['acceptance'],str(sfP[p])])
  #Signal yields
  yieldFile=filename+"_"+p+"_yield"
  cmd='vvMakeSignalYields.py -s {template} -c "{cut}" -o {output} -V "jj_LV_mass" -m {minMVV} -M {maxMVV} -f "pol2" -b {BR} -x 1000 samples'.format(template=template, cut=cut, output=yieldFile,minMVV=minMVV,maxMVV=maxMVV,BR=branchingFraction)
  os.system(cmd)

def makeDetectorResponse(name,filename,template,addCut="1"):
 #first parameterize detector response
 for p in purities:
  print "=========== PURITY: ", p
  cut='*'.join([cuts['common'],cuts[p],'(jj_l1_gen_softDrop_mass>10&&jj_gen_partialMass>1000&&jj_gen_partialMass<7000)',addCut])
  resFile=filename+"_"+name+"_detectorResponse_"+p+".root"		 
  #cmd='vvMake2DDetectorParam.py  -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "jj_LV_mass,jj_l1_softDrop_mass"  -g "jj_gen_partialMass,jj_l1_gen_softDrop_mass,jj_l1_gen_pt"  -b "150,200,250,300,350,400,450,500,600,700,800,900,1000,1500,2000,5000"   samples'.format(rootFile=resFile,samples=template,cut=cut,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,tag=name)
  cmd='vvMake2DDetectorParam.py  -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "jj_LV_mass,jj_l1_softDrop_mass"  -g "jj_gen_partialMass,jj_l1_gen_softDrop_mass,jj_l1_gen_softDrop_mass"  -b "10,20,30,35,40,45,50,80,100,120,150,200,250,350,500,600,800"   samples'.format(rootFile=resFile,samples=template,cut=cut,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,tag=name)

  os.system(cmd)
		 
def makeBackgroundShapesMJJKernel(name,filename,template,addCut="1"):
 
 #template += ",QCD_Pt-,QCD_HT"
 for p in purities:
  resFile=filename+"_"+name+"_detectorResponse_"+p+".root"	
  print "=========== PURITY: ", p
  cut='*'.join([cuts['common'],cuts[p],addCut,cuts['acceptanceGENMJJ'],'(jj_LV_mass>1000&&jj_LV_mass<7000)'])

  rootFile=filename+"_"+name+"_MJJ_"+p+".root"  	      
  #cmd='vvMake1DTemplateWithKernels.py -H "y" -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "jj_l1_gen_softDrop_mass" -b {binsMJJ}  -x {minMJJ} -X {maxMJJ} -r {res} samples'.format(rootFile=rootFile,samples=template,cut=cut,res=resFile,binsMJJ=binsMJJ,minMJJ=minMJJ,maxMJJ=maxMJJ)
  cmd='vvMake1DTemplateWithKernels.py --usegenmass -H "y" -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "jj_l1_gen_softDrop_mass" -b {binsMJJ}  -x {minMJJ} -X {maxMJJ} -r {res} samples'.format(rootFile=rootFile,samples=template,cut=cut,res=resFile,binsMJJ=binsMJJ,minMJJ=minMJJ,maxMJJ=maxMJJ)

  os.system(cmd)

def makeBackgroundShapesMVVKernel(name,filename,template,addCut="1"):
 
 #template += ",QCD_Pt-,QCD_HT"
 for p in purities:
  resFile=filename+"_"+name+"_detectorResponse_"+p+".root"	
  print "=========== PURITY: ", p
  cut='*'.join([cuts['common'],cuts[p],addCut,cuts['acceptanceGENMJJ'],'(jj_l1_softDrop_mass>30&&jj_l1_softDrop_mass<610)'])    
  rootFile=filename+"_"+name+"_MVV_"+p+".root"
  #cmd='vvMake1DMVVTemplateWithKernels.py -H "x" -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "jj_gen_partialMass" -b {binsMVV}  -x {minMVV} -X {maxMVV} -r {res} samples'.format(rootFile=rootFile,samples=template,cut=cut,res=resFile,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV)
  cmd='vvMake1DMVVTemplateWithKernels.py --usegenmass -H "x" -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "jj_gen_partialMass" -b {binsMVV}  -x {minMVV} -X {maxMVV} -r {res} samples'.format(rootFile=rootFile,samples=template,cut=cut,res=resFile,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV)

  os.system(cmd)

def makeBackgroundShapesMJJSpline(name,filename,template,addCut="1"):

 #template += ",QCD_Pt-,QCD_HT"
 for p in purities:
  print "=========== PURITY: ", p
  cut='*'.join([cuts['common'],cuts[p],addCut,cuts['acceptance']])
  rootFile=filename+"_"+name+"_MJJ_"+p+".root"	      
  cmd='vvMake1DTemplateSpline.py  -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "jj_l1_softDrop_mass"  -b {binsMJJ}  -x {minMJJ} -X {maxMJJ} -f 6 samples'.format(rootFile=rootFile,samples=template,cut=cut,binsMJJ=binsMJJ,minMJJ=minMJJ,maxMJJ=maxMJJ)
  os.system(cmd)
		
def makeBackgroundShapesMVVConditional(name,filename,template,addCut=""):
	
 #template += ",QCD_Pt-,QCD_HT"
 for p in purities:
  resFile=filename+"_"+name+"_detectorResponse_"+p+".root"	
  print "=========== PURITY: ", p
  cut='*'.join([cuts['common'],cuts[p],addCut,cuts['acceptanceGEN']])
  rootFile=filename+"_"+name+"_COND2D_"+p+".root"		 
  #cmd='vvMake2DTemplateWithKernels.py  -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "jj_gen_partialMass,jj_l1_gen_softDrop_mass"  -b {binsMVV} -B {binsMJJ} -x {minMVV} -X {maxMVV} -y {minMJJ} -Y {maxMJJ}  -r {res} samples'.format(rootFile=rootFile,samples=template,cut=cut,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,res=resFile,binsMJJ=binsMJJ,minMJJ=minMJJ,maxMJJ=maxMJJ)
  cmd='vvMake2DTemplateWithKernels.py --usegenmass -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "jj_gen_partialMass,jj_l1_gen_softDrop_mass"  -b {binsMVV} -B {binsMJJ} -x {minMVV} -X {maxMVV} -y {minMJJ} -Y {maxMJJ}  -r {res} samples'.format(rootFile=rootFile,samples=template,cut=cut,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,res=resFile,binsMJJ=binsMJJ,minMJJ=minMJJ,maxMJJ=maxMJJ)
  os.system(cmd)

def mergeBackgroundShapes(name,filename):

 for p in purities:
  inputy=filename+"_"+name+"_MJJ_"+p+".root"	    
  inputx=filename+"_"+name+"_COND2D_"+p+".root"	       
  rootFile=filename+"_"+name+"_2D_"+p+".root"	     
  cmd='vvMergeHistosToPDF2D.py -i "{inputx}" -I "{inputy}" -o "{rootFile}" -s "altshape:altshapeX" -S "altshape:altshapeY" -C "" '.format(rootFile=rootFile,inputx=inputx,inputy=inputy)
  os.system(cmd)

def makeNormalizations(name,filename,template,data=0,addCut='1',factor=1):

  for p in purities:
   rootFile=filename+"_"+p+".root"
   cut='*'.join([cuts['common'],cuts[p],addCut,cuts['acceptance']])
   cmd='vvMakeData.py -s "{samples}" -d {data} -c "{cut}"  -o "{rootFile}" -v "jj_LV_mass,jj_l1_softDrop_mass" -b "{BINS},{bins}" -m "{MINI},{mini}" -M "{MAXI},{maxi}" -f {factor} -n "{name}"  samples'.format(samples=template,cut=cut,rootFile=rootFile,BINS=binsMVV,bins=binsMJJ,MINI=minMVV,MAXI=maxMVV,mini=minMJJ,maxi=maxMJJ,factor=factor,name=name,data=data)
   os.system(cmd)

start_time = time.time()
									
#makeSignalShapesMVV("JJ_XqW",qWTemplate)
#makeSignalShapesMJJ("JJ_XqW",qWTemplate)
#makeSignalYields("JJ_XqW",qWTemplate,BRqW,{'HP':0.99,'LP':1.03})

#makeSignalShapesMVV("JJ_XqZ",qZTemplate)
#makeSignalShapesMJJ("JJ_XqZ",qZTemplate)
#makeSignalYields("JJ_XqZ",qZTemplate,BRqZ,{'HP':0.99,'LP':1.03})

makeDetectorResponse("nonRes","JJ",nonResTemplate,cuts['nonres'])
#makeBackgroundShapesMJJSpline("nonRes","JJ",nonResTemplate,cuts['nonres'])  #either splines OR kernel
makeBackgroundShapesMJJKernel("nonRes","JJ",nonResTemplate,cuts['nonres'])
makeBackgroundShapesMVVKernel("nonRes","JJ",nonResTemplate,cuts['nonres'])
makeBackgroundShapesMVVConditional("nonRes","JJ",nonResTemplate,cuts['nonres'])
##mergeBackgroundShapes("nonRes","JJ")

#makeNormalizations("nonRes","JJ",nonResTemplate,0,cuts['nonres'],1.0)
#makeNormalizations("data","JJ","QCD_HT",0,cuts['nonres'],1.0)
#makeNormalizations("data","JJ",dataTemplate,1)

finish_time = time.time()
print "time: ", finish_time - start_time
