# VV statistical analysis in 74X

Prepare your working dir with Higgs combine tools (74X)

```
mkdir VVAnalysisWith2DFit
mkdir CMGToolsForStat74X
cd CMGToolsForStat74X
cmsrel CMSSW_7_4_7
cd CMSSW_7_4_7/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v6.3.1
scram b clean; scram b -j 8
```

Checkout the VV statistical tools

```
cd ../..
git clone https://github.com/jngadiub/cmgtools-lite.git -b qstarStat CMGTools
scram b -j 8
```

Run the main code to produce the inputs to the combine
 
```
cd VVResonances/interactive
ln -s samples_location samples
python makeInputs_qStar.py
```
