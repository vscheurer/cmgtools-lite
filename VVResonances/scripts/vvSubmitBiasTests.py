#!/usr/bin/env python

import ROOT
import os, sys, re, optparse,pickle,shutil,json,random




parser = optparse.OptionParser()

parser.add_option("-q","--queue",dest="queue",help="Batch Queue",default='8nh')
parser.add_option("-t","--toyCard",dest="toyCard",help="Toy DataCard",default='')
parser.add_option("-N","--nToys",dest="toys",type=int,help="number of tens of toys",default=1)
parser.add_option("-r","--r",dest="r",type=float,help="Generate Signal",default=0)
parser.add_option("-m","--mass",dest="mass",type=int,help="Mass",default=0)
parser.add_option("-l","--label",dest="label",help="label")
parser.add_option("-f","--freq",dest="freq",type=int,help="frequentistFit",default=0)


(options,args) = parser.parse_args()




for i in range(0,options.toys):
    submitFile="submit_{tag}_{mass}_{i}.sh".format(i=i,tag=options.label,mass=options.mass)
    f=open(submitFile,'w')
    execScript = 'cd {cwd} \n'.format(cwd=os.getcwd())
    execScript += 'eval `scramv1 runtime -sh` \n'
    seed=int(201606+random.random()*10101982)
    if options.freq==0:
        execScript += "combine -m {mass} -M MaxLikelihoodFit --expectSignal={r} --bypassFrequentistFit -t 10 --seed {seed}  -n {tag}_{i}_{mass} --rMin=-1 --rMax=1 --skipBOnlyFit  {card}\n".format(mass=options.mass,seed=seed,card=options.toyCard,r=options.r,tag=options.label,i=i)
    else:
        execScript += "combine -m {mass} -M MaxLikelihoodFit --expectSignal={r} --bypassFrequentistFit -t 10 --seed {seed} --snapshotName MultiDimFit -n {tag}_{i}_{mass} --rMin=-1 --rMax=1 --skipBOnlyFit  {card}\n".format(mass=options.mass,seed=seed,card=options.toyCard,r=options.r,tag=options.label,i=i)


    f.write(execScript)
    f.close()
    os.system('chmod +x {submitFile}'.format(submitFile=submitFile))

    if options.queue!="local":
        os.system('bsub -q {queue} {submitFile}'.format(queue=options.queue,submitFile=submitFile))
    else:    
        os.system('sh {submitFile}'.format(i=i,submitFile=submitFile))





