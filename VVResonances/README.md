# CMG-VV ntuple production

Prepare you working directory:

```
mkdir  VVAnalysisWith2DFit
mkdir CMGToolsForProduction
cd CMGToolsForProduction/
cmsrel CMSSW_8_0_25
cd CMSSW_8_0_25/src
cmsenv
git cms-init
```

add the central cmg-cmssw repository to get the Heppy 80X branch

```
git remote add cmg-central https://github.com/${GITUSER}/cmg-cmssw.git -f  -t heppy_80X
```

configure the sparse checkout, and get the base heppy package

```
cp /afs/cern.ch/user/c/cmgtools/public/sparse-checkout_80X_heppy .git/info/sparse-checkout
git checkout -b heppy_80X cmg-central/heppy_80X
```

add your mirror, and push the 80X branch to it  

```  
git remote add origin git@github.com:jngadiub/cmg-cmssw.git
git push -u origin heppy_80X
```
  
now get the CMGTools subsystem from the cmgtools-lite repository  

```
git clone -o cmg-central https://github.com/jngadiub/cmgtools-lite.git -b 80X CMGTools
cd CMGTools
```
  
add your fork, and push the 80X branch to it  

```
git remote add origin  git@github.com:jngadiub/cmgtools-lite.git
git push -u origin 80X
```

checkout your development branch

```
git checkout -b qstarProduction
git push origin qstarProduction
```
  
compile  

```
cd $CMSSW_BASE/src && scram b clean && scram b -j 8
```

now you can run a simple local test do:

```
cd CMGTools/VVResonances
heppy test cfg/runVV_cfg_simple.py -N 100
```
