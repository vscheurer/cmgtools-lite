


import ROOT
import os




cuts={}


cuts['common'] = '(((HLT2_MU||HLT2_ELE||HLT2_ISOMU||HLT2_ISOELE||HLT2_MET120)&&run>2000)+(run<2000)*lnujj_sf)*(Flag_goodVertices&&Flag_CSCTightHaloFilter&&Flag_HBHENoiseFilter&&Flag_HBHENoiseIsoFilter&&Flag_eeBadScFilter&&lnujj_nOtherLeptons==0&&lnujj_l2_softDrop_mass>0&&lnujj_LV_mass>0&&Flag_badChargedHadronFilter&&Flag_badMuonFilter)'


cuts['mu'] = '(abs(lnujj_l1_l_pdgId)==13)'
cuts['e'] = '(abs(lnujj_l1_l_pdgId)==11)'
cuts['HP'] = '(lnujj_l2_tau2/lnujj_l2_tau1<0.6)'
cuts['LP'] = '(lnujj_l2_tau2/lnujj_l2_tau1>0.6&&lnujj_l2_tau2/lnujj_l2_tau1<0.75)'
cuts['NP'] = '(lnujj_l2_tau2/lnujj_l2_tau1>0)'

cuts['nob'] = '(lnujj_nMediumBTags==0)*lnujj_btagWeight'
cuts['b'] = '(lnujj_nMediumBTags>0)*lnujj_btagWeight'


cuts['res']='(lnujj_l2_mergedVTruth==1&&(lnujj_l2_nearestBDRTruth>0.8||lnujj_l2_nearestBDRTruth<0))'
cuts['nonres']='(lnujj_l2_mergedVTruth==0||(lnujj_l2_nearestBDRTruth>0.0&&lnujj_l2_nearestBDRTruth<0.8))'


leptons=['mu']
purities=['HP']
categories=['nob']


WWTemplate="BulkGravToWWToWlepWhad_narrow"
BRWW=2.*0.327*0.6760


WZTemplate="WprimeToWZToWlepZhad_narrow"
BRWZ=0.327*0.6991

WHTemplate="WprimeToWhToWlephbb"
BRWH=0.577*0.327

dataTemplate="SingleMuon,SingleElectron,MET"
resWTemplate="TTJets.,WWTo1L1Nu2Q"
resWMJJTemplate="TTJets.,WWTo1L1Nu2Q"

resZTemplate="WZTo1L1Nu2Q"
#nonResTemplate="WJetsToLNu_HT,TTJets.,DYJetsToLL_M50_HT"
nonResTemplate="TTJets."


minMJJ=30.0
maxMJJ=230.0

minMVV=600.0
maxMVV=4800.0


binsMJJ=100
binsMVV=100


cuts['acceptance']= "(lnujj_LV_mass>{minMVV}&&lnujj_LV_mass<{maxMVV}&&lnujj_l2_softDrop_mass>{minMJJ}&&lnujj_l2_softDrop_mass<{maxMJJ})".format(minMVV=minMVV,maxMVV=maxMVV,minMJJ=minMJJ,maxMJJ=maxMJJ)
cuts['acceptanceGEN']= "(lnujj_l2_gen_softDrop_mass>{minMJJ}&&lnujj_l2_gen_softDrop_mass<{maxMJJ}&&lnujj_gen_partialMass>{minMVV}&&lnujj_gen_partialMass<{maxMVV})".format(minMJJ=20,maxMJJ=260,minMVV=400,maxMVV=5000)                
cuts['acceptanceGENMVV']= "(lnujj_gen_partialMass>{minMVV}&&lnujj_gen_partialMass<{maxMVV})".format(minMVV=minMVV,maxMVV=maxMVV)

cuts['acceptanceMJJ']= "(lnujj_l2_softDrop_mass>{minMJJ}&&lnujj_l2_softDrop_mass<{maxMJJ})".format(minMJJ=minMJJ,maxMJJ=maxMJJ)                


def makeSignalShapesMVV(filename,template):
    for l in leptons:
        cut='*'.join([cuts['common'],cuts[l],cuts['acceptanceMJJ']])
        rootFile=filename+"_MVV_"+l+".root"
        cmd='vvMakeSignalMVVShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "lnujj_LV_mass"  samples'.format(template=template,cut=cut,rootFile=rootFile,minMJJ=minMJJ,maxMJJ=maxMJJ)
        os.system(cmd)
        jsonFile=filename+"_MVV_"+l+".json"
        print 'Making JSON'
        cmd='vvMakeJSON.py  -o "{jsonFile}" -g "MEAN:pol1,SIGMA:pol1,ALPHA1:pol2,N1:pol0,ALPHA2:pol2,N2:pol0" -m 800 -M 5000  {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile)
        os.system(cmd)


def makeSignalShapesMJJ(filename,template):
    for p in purities:
        cut='*'.join([cuts['common'],cuts[p]])
        rootFile=filename+"_MJJ_"+p+".root"
        doExp=1
        if p=='HP':
            doExp=0
        cmd='vvMakeSignalMJJShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -V "lnujj_l2_softDrop_mass" -m {minMJJ} -M {maxMJJ} -e {doExp}  samples'.format(template=template,cut=cut,rootFile=rootFile,minMJJ=minMJJ,maxMJJ=maxMJJ,doExp=doExp)
        os.system(cmd)
        jsonFile=filename+"_MJJ_"+p+".json"

        if p=='HP':
            cmd='vvMakeJSON.py  -o "{jsonFile}" -g "mean:pol4,sigma:pol4,alpha:pol3,n:pol0,alpha2:pol0,n2:pol0,slope:pol0,f:pol0" -m 500 -M 5000  {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile)
        else:
            cmd='vvMakeJSON.py  -o "{jsonFile}" -g "mean:pol3,sigma:pol1,alpha:pol0,n:pol0,slope:pol1,f:pol4,alpha2:pol0,n2:pol0" -m 500 -M 5000  {rootFile}  '.format(jsonFile=jsonFile,rootFile=rootFile)

        os.system(cmd)


def makeSignalYields(filename,template,branchingFraction):
    for region in categories:
        for lepton in leptons:
            for purity in purities:
                cut = "*".join([cuts[lepton],cuts[purity],cuts['common'],cuts[region],cuts['acceptance']])
                #Signal yields
                yieldFile=filename+"_"+lepton+"_"+purity+"_"+region+"_yield"
                cmd='vvMakeSignalYields.py -s {template} -c "{cut}" -o {output} -V "lnujj_LV_mass" -m {minMVV} -M {maxMVV} -f "pol5" -b {BR} -x 800 samples'.format(template=template, cut=cut, output=yieldFile,minMVV=minMVV,maxMVV=maxMVV,BR=branchingFraction)
                os.system(cmd)

def makeBackgroundShapesMVV(name,filename,template,addCut=""):
    for l in leptons:
        for p in purities:
            for c in categories:
                if addCut=='':
                    cut='*'.join([cuts['common'],cuts[l],cuts[c],cuts[p]])
                else:
                    cut='*'.join([cuts['common'],cuts[l],cuts[c],cuts[p],addCut])
                
            mvvFile=filename+"_MVV_"+name+"_"+l+"_"+c
            cmd='vvMakeBackgroundMVVConditionalShapes.py -s "{template}" -c "{cut}"  -o "{rootFile}" -v "lnujj_LV_mass" -V "lnujj_l2_softDrop_mass"  -b 200  -x {minMVV} -X {maxMVV}   -B 20 -y {minMJJ} -Y {maxMJJ}   samples'.format(template=template,cut=cut,rootFile=mvvFile,minMVV=minMVV-200,maxMVV=maxMVV,minMJJ=minMJJ-12,maxMJJ=maxMJJ+12)
            os.system(cmd)


def makeBackgroundShapes(name,filename,template,addCut=""):
    for l in leptons:
        for p in purities:
            for c in categories:
                if addCut=='':
                    cut='*'.join([cuts['common'],cuts[l],cuts[c],cuts[p]])
                else:
                    cut='*'.join([cuts['common'],cuts[l],cuts[c],cuts[p],addCut])
                
                jsonFile=filename+"_MJJ_"+name+"_"+l+"_"+p+"_"+c+'.json'
                outFile=filename+"_MVV_"+name+"_"+l+"_"+p+"_"+c+".json"
                if c=='nob':
                    param='p0:1|p1:2|p2:2'
                else:
                    param='p0:0|p1:2|p2:1'

                cmd='vvMakeBackgroundShapes2D.py -s "{template}" -c "{cut}"  -o "{rootFile}" -v "lnujj_LV_mass" -V "lnujj_l2_softDrop_mass"  -b {binsMVV} -x {minMVV} -X {maxMVV}   -B {binsMJJ} -y {minMJJ} -Y {maxMJJ} -p "{param}"  -j {jsonFile} samples'.format(template=template,cut=cut,rootFile=outFile,minMVV=minMVV,maxMVV=maxMVV,minMJJ=minMJJ,maxMJJ=maxMJJ,binsMVV=binsMVV,binsMJJ=binsMJJ,jsonFile=jsonFile,param=param)
                os.system(cmd)



def makeBackgroundShapesHisto(name,filename):
    for l in leptons:
        for p in purities:               
            for c in categories:               
                mvvFile=filename+"_MVV_"+name+"_"+l+"_"+p+"_"+c
                mjjFile=filename+"_MJJ_"+name+"_"+l+"_"+p+"_"+c+".json"
                rootFile=filename+"_MVVHist_"+name+"_"+l+"_"+p+"_"+c+".root"
                cmd="vvPDFToHisto.py -n histo -s 'slopeSyst_{name}:1.0:0.15' -m 'meanSyst0_{name}:1.0:0.15,meanSyst1_{name}:mjj:1e-3' -w 'widthSyst_{name}:1.0:0.15' -S 'slopeSystMJJ_{name2}:1.0:0.5' -M 'meanSystMJJ_{name2}:1.0:0.5' -W 'widthSystMJJ_{name2}:1.0:0.5'   -j {mjjFile} -o '{rootFile}' -b {binsMVV} -x {minMVV} -X {maxMVV} -B {binsMJJ} -y {minMJJ} -Y {maxMJJ} {mvvFile}.json".format(name=name+"_"+l+"_"+p+"_"+c,name2=name+"_"+l+"_"+p+"_"+c,rootFile=rootFile,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,binsMJJ=binsMJJ,minMJJ=minMJJ,maxMJJ=maxMJJ,mvvFile=mvvFile,mjjFile=mjjFile) 
                os.system(cmd)



def makeBackgroundShapesMJJ(name,filename,template,addCut=""):
    for l in leptons:
        for p in purities:
            for c in categories:

                if addCut=='':
                    cut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],cuts['acceptance']])
                    gencut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],cuts['acceptanceMJJLoose']])
                else:
                    cut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],addCut,cuts['acceptance']])
                    gencut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],addCut,cuts['acceptanceMJJLoose']])
                rootFile=filename+"_MJJ_"+name+"_"+l+"_"+p+"_"+c+".root"            
                cmd='vvFitGaussianSum.py  -o "{rootFile}" -s "{samples}" -c "{cut}" -C "{genCut}" -v "lnujj_l2_softDrop_mass" -b {binsMJJ} -m {minMJJ} -M {maxMJJ} -g "lnujj_l2_gen_softDrop_mass" -q "scaleSyst_{tag}:0.1" -w "widthSyst_{tag}:5.0"  -d 2  samples'.format(rootFile=rootFile,samples=template,cut=cut,genCut=gencut,binsMJJ=binsMJJ,minMJJ=minMJJ,maxMJJ=maxMJJ,tag=name+"_"+l+"_"+p+"_"+c)
                os.system(cmd)

def makeBackgroundShapesMJJConditional(name,filename,template,addCut=""):
    for l in leptons:
        for p in purities:
            for c in categories:

                if addCut=='':
                    cut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],cuts['acceptance']])
                    gencut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],cuts['acceptance'],cuts['acceptanceGEN']])
                else:
                    cut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],addCut,cuts['acceptance']])
                    gencut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],addCut,cuts['acceptance'],cuts['acceptanceGEN']])
                rootFile=filename+"_MJJ_"+name+"_"+l+"_"+p+"_"+c+".root"            
                cmd='vvFitGaussianSumCond.py  -o "{rootFile}" -s "{samples}" -c "{cut}" -C "{genCut}" -v "lnujj_l2_softDrop_mass" -b {binsMJJ} -m {minMJJ} -M {maxMJJ} -g "lnujj_l2_gen_softDrop_mass" -V "lnujj_LV_mass" -B "600,650,700,750,800,850,900,1000,1200,1400,1600,1800,2000,2250,2500,3000,3500,4800"  samples'.format(rootFile=rootFile,samples=template,cut=cut,genCut=gencut,binsMJJ=binsMJJ,minMJJ=minMJJ,maxMJJ=maxMJJ,tag=name+"_"+l+"_"+p+"_"+c)
                os.system(cmd)

def makeBackgroundShapesMVVConditional(name,filename,template,addCut=""):
    for l in leptons:
        for p in purities:
            for c in categories:
                if addCut=='':
                    cut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],cuts['acceptance']])
                    gencut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],cuts['acceptance'],cuts['acceptanceGENMVV']])
                else:
                    cut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],addCut,cuts['acceptance']])
                    gencut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],addCut,cuts['acceptance'],cuts['acceptanceGENMVV']])
                rootFile=filename+"_MVV_"+name+"_"+l+"_"+p+"_"+c+".root"            
                cmd='vvFitGaussianSumCond.py  -o "{rootFile}" -s "{samples}" -c "{cut}" -C "{genCut}" -v "lnujj_LV_mass" -b {binsMVV} -m {minMVV} -M {maxMVV} -g "lnujj_gen_partialMass" -V "lnujj_l2_softDrop_mass" -B "30,40,50,60,70,80,90,100,120,140,160,180,200,250"   samples'.format(rootFile=rootFile,samples=template,cut=cut,genCut=gencut,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,tag=name+"_"+l+"_"+p+"_"+c)
                os.system(cmd)


def makeBackgroundShapes2D(name,filename,template,addCut=""):

    #first parameterize detector response
    cut='*'.join([cuts['common'],cuts['acceptanceGEN'],addCut])
    resFile=filename+"_"+name+"_detectorResponse.root"            
    cmd='vvMake2DDetectorParam.py  -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "lnujj_LV_mass,lnujj_l2_softDrop_mass"  -g "lnujj_gen_partialMass,lnujj_l2_gen_softDrop_mass"  -B "20,30,40,50,60,70,80,90,100,120,140,160,180,200,250" -b "400,600,700,800,1000,1250,1500,2000,2500,3500,4800,5000"   samples'.format(rootFile=resFile,samples=template,cut=cut,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,tag=name)
    os.system(cmd)

    for l in leptons:
        for p in purities:
            for c in categories:
                if addCut=='':
                    cut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],cuts['acceptance'],cuts['acceptanceGEN']])
                else:
                    cut='*'.join([cuts['common'],cuts[l],cuts[p],cuts[c],addCut,cuts['acceptance'],cuts['acceptanceGEN']])

                    rootFile=filename+"_"+name+"_2D_"+l+"_"+p+"_"+c+".root"            

                    cmd='vvMake2DTemplateWithKernels.py  -o "{rootFile}" -s "{samples}" -c "{cut}"  -v "lnujj_gen_partialMass,lnujj_l2_gen_softDrop_mass" -d 2 -b {binsMVV} -B {binsMJJ} -x {minMVV} -X {maxMVV} -y {minMJJ} -Y {maxMJJ}  -r {res} samples'.format(rootFile=rootFile,samples=template,cut=cut,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,res=resFile,binsMJJ=binsMJJ,minMJJ=minMJJ,maxMJJ=maxMJJ)
    os.system(cmd)
                


def makeResMVVShapes(name,filename,template,addCut=""):
    for l in leptons:    
        for p in purities:
            for c in categories:
                if addCut=='':
                    cut='*'.join([cuts['common'],cuts[l],cuts[c]])
                else:
                    cut='*'.join([cuts['common'],addCut,cuts[l],cuts[c]])

                rootFile="tmp.root"
                cmd='vvMakeData.py -s "{samples}"  -c "{cut}"  -o "{rootFile}" -v "lnujj_LV_mass" -b "{bins}" -m "{mini}" -M "{maxi}"  -n "{name}"  -d 0 samples'.format(samples=template,cut=cut,rootFile=rootFile,bins=100,mini=600,maxi=maxMVV,name=name)
                os.system(cmd)
                
                jsonFile=filename+"_MVV_"+name+"_"+l+"_"+p+"_"+c
                cmd='vvSimpleFit.py -o {jsonFile} -i {histo} -f erfpow {rootFile}'.format(jsonFile=jsonFile,rootFile=rootFile,histo=name)
                os.system(cmd)

                rootFile=filename+"_MVVHist_"+name+"_"+l+"_"+p+"_"+c+".root"
                cmd="vvPDFToHisto1D.py -n histo -s 'slopeSyst_{name}:1.0:0.1' -m 'meanSyst_{name}:1.0:0.1' -w 'widthSyst_{name}:1.0:0.1' -o '{rootFile}' -b {binsMVV} -x {minMVV} -X {maxMVV}  {mvvFile}.json".format(name=name+"_"+l+"_"+p+"_"+c,rootFile=rootFile,binsMVV=binsMVV,minMVV=minMVV,maxMVV=maxMVV,mvvFile=jsonFile) 
                os.system(cmd)




def makeResMJJShapes(name,filename,template,addCut=""):

    for p in purities:
        if p=='HP':
            if addCut=='':
                cut='*'.join([cuts['common'],cuts[p]])
            else:
                cut='*'.join([cuts['common'],cuts[p],addCut])
            doExp=0    
        else:
            if addCut=='':
                cut='*'.join([cuts['common'],cuts[p]])
            else:
                cut='*'.join([cuts['common'],cuts[p],addCut])
            doExp=1    
                       
        mjjFile=filename+"_MJJ_"+name+"_"+p
        jsonFile=filename+"_XWW_MJJ_"+p+".json"
        cmd='vvMakeTopMJJConditionalShapesFromTruth.py -s "{template}" -c "{cut}"  -o "{rootFile}" -v "lnujj_l2_softDrop_mass" -V "lnujj_LV_mass"  -b 20  -x {minMJJ} -X {maxMJJ} -e {doExp} -j {jsonFile} samples'.format(template=template,cut=cut,rootFile=mjjFile,minMJJ=minMJJ,maxMJJ=180,doExp=doExp,jsonFile=jsonFile)
        os.system(cmd)
#        print 'NOT RUNNING FIT'
        jsonFile=filename+"_MJJ_"+name+"_"+p+".json"

        cmd='vvMakeJSON.py  -o "{jsonFile}" -g "mean:pol1,sigma:pol1,alpha:pol3,n:pol0,alpha2:pol0,n2:pol0" -m 500 -M 3500  {rootFile}  '.format(jsonFile=jsonFile,rootFile=mjjFile+'.root')
        os.system(cmd)





def makeNormalizations(name,filename,template,data=0,addCut='',factor=1):
    for lepton in leptons:
        for purity in purities:
            for region in categories:
                rootFile=filename+"_"+lepton+"_"+purity+"_"+region+".root"
                if addCut=='':
                    cut='*'.join([cuts['common'],cuts[purity],cuts[lepton],cuts[region],cuts['acceptance']])
                else:
                    cut='*'.join([cuts['common'],cuts[purity],cuts[lepton],cuts[region],addCut,cuts['acceptance']])
                cmd='vvMakeData.py -s "{samples}" -d {data} -c "{cut}"  -o "{rootFile}" -v "lnujj_LV_mass,lnujj_l2_softDrop_mass" -b "{BINS},{bins}" -m "{MINI},{mini}" -M "{MAXI},{maxi}" -f {factor} -n "{name}"  samples'.format(samples=template,cut=cut,rootFile=rootFile,BINS=binsMVV,bins=binsMJJ,MINI=minMVV,MAXI=maxMVV,mini=minMJJ,maxi=maxMJJ,factor=factor,name=name,data=data)
                os.system(cmd)




def estimateSystematicsCorrelations(tau21factor,bfactor):
    print 'Estimate the effect of 10% of tau21 in the different categories'

    for sample in ["BulkGravToWWToWlepWhad_narrow_2000"]:
        for purity in purities:
            denom='*'.join([cuts['common'],cuts['acceptance']])           
            print 'Tau21 - Sample:',sample,purity
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_l2_tau2/lnujj_l2_tau1" -f {factor} samples'.format(sample=sample,denom=denom,num='*'.join([cuts[purity]]),factor=tau21factor)
            os.system(cmd)


            print 'btagged - Sample:',sample,purity
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_highestOtherBTag" -f {factor} samples'.format(sample=sample,denom=denom,num='lnujj_highestOtherBTag>0.8',factor=bfactor)
            os.system(cmd)

            print 'no-btagged - Sample:',sample,purity
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_highestOtherBTag" -f {factor} samples'.format(sample=sample,denom=denom,num='lnujj_nCentralJets==0||lnujj_highestOtherBTag<0.8',factor=bfactor)
            os.system(cmd)


    for sample in [WJetsTemplate]:
        for purity in purities:
            denom='*'.join([cuts['common'],cuts['acceptance']])
            print 'Sample:',sample,purity
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_l2_tau2/lnujj_l2_tau1" -f {factor} samples'.format(sample=sample,denom=denom,num='*'.join([cuts[purity]]),factor=tau21factor)
            os.system(cmd)

            print 'btagged - Sample:',sample,purity
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_highestOtherBTag" -f {factor} samples'.format(sample=sample,denom=denom,num='lnujj_highestOtherBTag>0.8',factor=bfactor)
            os.system(cmd)

            print 'no-btagged - Sample:',sample,purity
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_highestOtherBTag" -f {factor} samples'.format(sample=sample,denom=denom,num='lnujj_nCentralJets==0||lnujj_highestOtherBTag<0.8',factor=bfactor)
            os.system(cmd)



    for sample in [topTemplate]:
        for purity in purities:
            
            denom='*'.join([cuts['common'],cuts['acceptance'],'(lnujj_l2_mergedVTruth&&lnujj_l2_nearestBDRTruth>0.8)'])
            print 'Merged Top',purity
            print 'Sample:',sample
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_l2_tau2/lnujj_l2_tau1" -f {factor} samples'.format(sample=sample,denom=denom,num='*'.join([cuts[purity]]),factor=tau21factor)
            os.system(cmd)


#            print 'btagged - Sample:',sample,purity
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_highestOtherBTag" -f {factor} samples'.format(sample=sample,denom=denom,num='lnujj_highestOtherBTag>0.8',factor=bfactor)
            os.system(cmd)

            print 'no-btagged - Sample:',sample,purity
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_highestOtherBTag" -f {factor} samples'.format(sample=sample,denom=denom,num='lnujj_nCentralJets==0||lnujj_highestOtherBTag<0.8',factor=bfactor)
            os.system(cmd)


            denom='*'.join([cuts['common'],cuts['acceptance'],'(!(lnujj_l2_mergedVTruth&&lnujj_l2_nearestBDRTruth>0.8))'])
            print 'Other Top',purity
            print 'Sample:',sample
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_l2_tau2/lnujj_l2_tau1" -f {factor} samples'.format(sample=sample,denom=denom,num='*'.join([cuts[purity]]),factor=tau21factor)
            os.system(cmd)

            print 'btagged - Sample:',sample,purity
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_highestOtherBTag" -f {factor} samples'.format(sample=sample,denom=denom,num='lnujj_highestOtherBTag>0.8',factor=bfactor)
            os.system(cmd)

            print 'no-btagged - Sample:',sample,purity
            cmd='vvEstimateSystematicsCorrelations.py -s "{sample}" -d "{denom}" -n "{num}" -v "lnujj_highestOtherBTag" -f {factor} samples'.format(sample=sample,denom=denom,num='lnujj_nCentralJets==0||lnujj_highestOtherBTag<0.8',factor=bfactor)
            os.system(cmd)



#makeSignalShapesMJJ("LNuJJ_XWW",WWTemplate)
#makeSignalShapesMJJ("LNuJJ_XWZ",WZTemplate)

#makeSignalShapesMVV("LNuJJ_XWW",WWTemplate)
#makeSignalShapesMVV("LNuJJ_XWZ",WZTemplate)

#makeSignalYields("LNuJJ_XWW",WWTemplate,BRWW)
#makeSignalYields("LNuJJ_XWZ",WZTemplate,BRWZ)



#makeResMJJShapes("resW","LNuJJ",resWMJJTemplate,"(lnujj_l2_mergedVTruth==1&&(lnujj_l2_nearestBDRTruth>0.8||lnujj_l2_nearestBDRTruth<0))")
#makeResMVVShapes("resW","LNuJJ",resWTemplate,"(lnujj_l2_mergedVTruth==1&&(lnujj_l2_nearestBDRTruth>0.8||lnujj_l2_nearestBDRTruth<0))")



###makeBackgroundShapesMJJ("nonRes","LNuJJ",nonResTemplate,cuts['nonres'])
#makeBackgroundShapesMVV("nonRes","LNuJJ",nonResTemplate,cuts['nonres'])
###makeBackgroundShapesHisto("nonRes","LNuJJ")

#makeBackgroundShapes2D("nonRes","LNuJJ",nonResTemplate,cuts['nonres'])
#makeBackgroundShapes("nonRes","LNuJJ",nonResTemplate,cuts['nonres'])
#makeBackgroundShapesHisto("nonRes","LNuJJ")


#makeNormalizations("nonRes","LNuJJ",nonResTemplate,0,cuts['nonres'],0.88)
#makeNormalizations("resW","LNuJJ",resWTemplate,0,cuts['res'])
#makeNormalizations("data","LNuJJ",dataTemplate,1)
