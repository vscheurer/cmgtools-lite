#!/usr/bin/env python

import ROOT
import os, sys, re, optparse,pickle,shutil,json,random




parser = optparse.OptionParser()

parser.add_option("-q","--queue",dest="queue",help="Batch Queue",default='8nh')
parser.add_option("-N","--nToys",dest="toys",type=int,help="number of fifths of toys",default=1)
parser.add_option("-x","--minx",dest="minx",type=float,help="min",default=0)
parser.add_option("-X","--maxX",dest="maxx",type=float,help="max",default=0)
parser.add_option("-n","--nPoints",dest="points",type=int,help="points",default=0)



(options,args) = parser.parse_args()



for i in range(0,options.toys):
    submitFile="submit_{i}.sh".format(i=i)
    f=open(submitFile,'w')
    execScript = 'cd {cwd} \n'.format(cwd=os.getcwd())
    execScript += 'eval `scramv1 runtime -sh` \n'
    seed=int(201606+random.random()*10101982+i)
    execScript += "combine  -M GenerateOnly --toysFrequentist -m 1350 -t 5 --seed {seed} --saveToys --expectSignal=0  {card} \n".format(card=args[0],seed=seed)  
    for j in range(1,6):
        execScript+="combine  -m 1350 -M MultiDimFit --redefineSignalPOI MH  --setPhysicsModelParameters r=0 --freezeNuisances r,MH --saveNLL -n bfit_{i}_{j} -D higgsCombineTest.GenerateOnly.mH1350.{seed}.root:toys/toy_{j} {card} \n".format(mini=options.minx,maxi=options.maxx,points=options.points,seed=seed,i=i,j=j,card=args[0])
        execScript+="combine  -M MultiDimFit --redefineSignalPOI MH --algo=grid --setPhysicsModelParameterRange MH={mini},{maxi}:r=0,0.1 --points {points} --saveNLL -n {i}_{j} -D higgsCombineTest.GenerateOnly.mH1350.{seed}.root:toys/toy_{j} {card} \n".format(mini=options.minx,maxi=options.maxx,points=options.points,seed=seed,i=i,j=j,card=args[0])

    f.write(execScript)
    f.close()
    os.system('chmod +x {submitFile}'.format(submitFile=submitFile))

    if options.queue!="local":
        os.system('bsub -q {queue} {submitFile}'.format(queue=options.queue,submitFile=submitFile))
    else:    
        os.system('sh {submitFile}'.format(i=i,submitFile=submitFile))





