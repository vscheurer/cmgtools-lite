# CMG-VV ntuple production

Prepare you working directory:

```
mkdir VVAnalysisWith2DFit
mkdir CMGToolsForProduction
cd CMGToolsForProduction/
cmsrel CMSSW_8_0_25
cd CMSSW_8_0_25/src
cmsenv
git cms-init
```

Checkout the base heppy package

```
git remote add my-cmg-cmssw https://github.com/jngadiub/cmg-cmssw.git
cp /afs/cern.ch/user/c/cmgtools/public/sparse-checkout_80X_heppy .git/info/sparse-checkout
git fetch my-cmg-cmssw
git checkout -b heppy_80X my-cmg-cmssw/heppy_80X
```

Now get the CMGTools subsystem from the cmgtools-lite repository 

```
git clone -o my-cmg-cmssw https://github.com/jngadiub/cmgtools-lite.git -b qstarProduction CMGTools
scram b clean; scram b -j 8
```

Try to run a simple local test do:

```
cd CMGTools/VVResonances
heppy test cfg/runVV_cfg_simple.py -N 100
```

Try a simple test on the lxbatch (NB: do not forget to run voms):

```
heppy_batch.py -r /store/cmst3/user/${LXBATCHUSER}/test -o /eos/cms/store/cmst3/user/${LXBATCHUSER}/test/ cfg/runVV_cfg_simple.py -b 'bsub -q 8nh -u ${LXBATCHUSER} -o std_output.txt -J test  < batchScript.sh'
```

---------------------------------------------------------------

For full production on lxbatch switch to test type = 0 at line https://github.com/jngadiub/cmgtools-lite/blob/qstarProduction/VVResonances/cfg/runVV_cfg.py#L94

then run

```
heppy_batch.py -r /store/cmst3/group/exovv/VVtuple/qstarProduction/QstarToQV -o /eos/cms/store/cmst3/group/exovv/VVtuple/qstarProduction/QstarToQV cfg/runVV_cfg.py -b 'bsub -q 8nh -u ${LXBATCHUSER} -o std_output.txt -J QstarToQV  < batchScript.sh' 
```

