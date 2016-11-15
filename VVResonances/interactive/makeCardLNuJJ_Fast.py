import ROOT
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
from CMGTools.VVResonances.statistics.DataCardMaker import DataCardMaker
cmd='combineCards.py '



for lepton in ['e','mu']:
    for purity in ['HP','LP']:
        for category in ['nob','b']:
            card=DataCardMaker(lepton,purity,'13TeV',12900,category)
            cat='_'.join([category,lepton,purity,'13TeV'])
            cmd=cmd+" "+cat+'=datacard_'+cat+'.txt '
         


            #WW signal-MVV
            card.addMVVSignalParametricShape("XWW_MVV","MLNuJ","LNuJJ_XWW_MVV_"+lepton+".json",{'CMS_scale_j':1,'CMS_scale_MET':1.0},{'CMS_res_j':1.0,'CMS_res_MET':1.0})

            if purity=='HP':
                card.addMJJSignalParametricShapeNOEXP("Wqq","MJ","LNuJJ_XWW_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0})
            else:
                card.addMJJSignalParametricShape("Wqq","MJ","LNuJJ_XWW_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0})

            card.product("XWW","Wqq","XWW_MVV")
            card.addParametricYield("XWW",0,"LNuJJ_XWW_"+lepton+"_"+purity+"_"+category+"_yield.json")
#            card.addParametricYieldWithCrossSection("XWW",0,"LNuJJ_XWW_"+lepton+"_"+purity+"_"+category+"_yield.json",'sigma_hvt.json','sigma0','BRWW')



            #W+jets
            rootFile="LNuJJ_MVVHist_Wjets_"+lepton+"_"+purity+"_"+category+".root"
            card.addHistoShapeFromFile("Wjets",["MLNuJ","MJ"],rootFile,"histo",["slopeSyst_Wjets_"+lepton+"_"+category,"widthSyst_Wjets_"+lepton+"_"+category,"meanSyst0_Wjets_"+lepton+"_"+category,"meanSyst1_Wjets_"+lepton+"_"+category,"slopeSystMJJ_Wjets_"+purity,"widthSystMJJ_Wjets_"+purity,"meanSystMJJ_Wjets_"+purity],False,0)       
            card.addFixedYieldFromFile("Wjets",1,"LNuJJ_"+lepton+"_"+purity+"_"+category+".root","Wjets")


            #TOP RES
            card.addMJJSignalParametricShapeNOEXP("WqqTop","MJ","LNuJJ_MJJ_topW_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0},"MLNuJ")

            rootFile="LNuJJ_MVVHist_topW_"+lepton+"_"+category+".root"
            card.addHistoShapeFromFile("topW_MVV",["MLNuJ"],rootFile,"histo",["slopeSyst_topW_"+lepton+"_"+category,"widthSyst_topW_"+lepton+"_"+category,"meanSyst_topW_"+lepton+"_"+category],False,0)       
            card.conditionalProduct("topW","WqqTop","MLNuJ","topW_MVV")
            card.addFixedYieldFromFile("topW",2,"LNuJJ_"+lepton+"_"+purity+"_"+category+".root","topW")



            #SM WW
            if purity=='HP':
                card.addMJJSignalParametricShape("WqqVV","MJ","LNuJJ_XWW_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0},"MLNuJ")
            else:
                card.addMJJSignalParametricShapeNOEXP("WqqVV","MJ","LNuJJ_XWW_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0},"MLNuJ")


            rootFile="LNuJJ_MVVHist_WW_"+lepton+"_"+category+".root"
            card.addHistoShapeFromFile("WW_MVV",["MLNuJ"],rootFile,"histo",[],False,0)       
            card.conditionalProduct("WW","WqqVV","MLNuJ","WW_MVV")
            card.addFixedYieldFromFile("WW",3,"LNuJJ_"+lepton+"_"+purity+"_"+category+".root","WW")

            #SM WZ RES
            if purity=='HP':
                card.addMJJSignalParametricShapeNOEXP("ZqqVV","MJ","LNuJJ_XWZ_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0},"MLNuJ")
            else:
                card.addMJJSignalParametricShape("ZqqVV","MJ","LNuJJ_XWZ_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0},"MLNuJ")

            rootFile="LNuJJ_MVVHist_WZ_"+lepton+"_"+category+".root"
            card.addHistoShapeFromFile("WZ_MVV",["MLNuJ"],rootFile,"histo",[],False,0)       
            card.conditionalProduct("WZ","ZqqVV","MLNuJ","WZ_MVV")
            card.addFixedYieldFromFile("WZ",4,"LNuJJ_"+lepton+"_"+purity+"_"+category+".root","WZ")

            #TOP NONRES
            rootFile="LNuJJ_MVVHist_topOther_"+lepton+"_"+purity+"_"+category+".root"
            if purity=="HP":
                card.addHistoShapeFromFile("topOther",["MLNuJ","MJ"],rootFile,"histo",["slopeSyst_topOther_"+lepton+"_"+category,"widthSyst_topOther_"+lepton+"_"+category,"meanSyst0_topOther_"+lepton+"_"+category,"meanSyst1_topOther_"+lepton+"_"+category,"slopeSystMJJ_topOther_"+purity,"widthSystMJJ_topOther_"+purity,"meanSystMJJ_topOther_"+purity],False,0)       
            else:
                card.addHistoShapeFromFile("topOther",["MLNuJ","MJ"],rootFile,"histo",["slopeSyst_topOther_"+lepton+"_"+category,"widthSyst_topOther_"+lepton+"_"+category,"meanSyst0_topOther_"+lepton+"_"+category,"meanSyst1_topOther_"+lepton+"_"+category,"slopeSystMJJ_topOther_"+purity],False,2)       

            card.addFixedYieldFromFile("topOther",5,"LNuJJ_"+lepton+"_"+purity+"_"+category+".root","topOther")

            #DATA
            card.importBinnedData("LNuJJ_"+lepton+"_"+purity+"_"+category+".root","data",["MLNuJ","MJ"])


            #####
            #####SYSTEMATICS

            #luminosity
            card.addSystematic("CMS_lumi","lnN",{'XWW':1.04,'XWZ':1.04,'WW':1.04,'WZ':1.04})

            #lepton efficiency
            card.addSystematic("CMS_eff_"+lepton,"lnN",{'XWW':1.05,'XWZ':1.05,'WW':1.05,'WZ':1.05,'Wjets':1.05,'topW':1.05,'topOther':1.05})


            #W+jets cross section in acceptance-dominated by pruned mass
            card.addSystematic("CMS_Wjets_norm","lnN",{'Wjets':1.5})
            card.addSystematic("CMS_VV_norm","lnN",{'WW':1.5,'WZ':1.5})

            #Top cross section    
            card.addSystematic("CMS_top_norm","lnN",{'topW':1.5})
            card.addSystematic("CMS_top_resFraction","lnN",{'topOther':1.5,'topW':0.5})

            #tau21 
            if purity=='HP':
                card.addSystematic("CMS_tau21_eff","lnN",{'topW':1-0.2,'XWW':1-0.2,'XWZ':1-0.2,'WW':1-0.2,'WZ':1-0.2})
                card.addSystematic("CMS_tau21_fake_Wjets","lnN",{'Wjets':1-0.17})
                card.addSystematic("CMS_tau21_fake_topOther","lnN",{'topOther':1-0.1})

            if purity=='LP':
                card.addSystematic("CMS_tau21_eff","lnN",{'topW':1+1.2,'XWW':1+1.2,'XWZ':1+1.2,'WW':1+1.2,'WZ':1+1.2})
                card.addSystematic("CMS_tau21_fake_Wjets","lnN",{'Wjets':1+0.33})
                card.addSystematic("CMS_tau21_fake_topOther","lnN",{'topOther':1+0.36})

            if category=='b':
                card.addSystematic("CMS_btag_eff","lnN",{'topW':1.12,'topOther':1.12})
                card.addSystematic("CMS_btag_fake","lnN",{'XWW':1-0.45,'XWZ':1-0.45,'WW':1-0.45,'WZ':1-0.45})
            else:
                card.addSystematic("CMS_btag_eff","lnN",{'topW':0.95,'topOther':0.95})
                card.addSystematic("CMS_btag_fake","lnN",{'XWW':1+0.02,'XWZ':1+0.02,'WW':1+0.02,'WZ':1+0.02})
               
            #pruned mass scale    
            card.addSystematic("CMS_scale_j","param",[0.0,0.02])
            card.addSystematic("CMS_res_j","param",[0.0,0.05])
            card.addSystematic("CMS_scale_prunedj","param",[0.0,0.1])
#            card.addSystematic("CMS_scale_prunedj_f","param",[0.0,0.0005])
            card.addSystematic("CMS_res_prunedj","param",[0.0,0.2])
#            card.addSystematic("CMS_res_prunedj_f","param",[0.0,0.0005])
            card.addSystematic("CMS_scale_MET","param",[0.0,0.02])
            card.addSystematic("CMS_res_MET","param",[0.0,0.01])



            card.addSystematic("slopeSyst_Wjets_"+lepton+"_"+category,"param",[0.0,0.333])
            card.addSystematic("meanSyst0_Wjets_"+lepton+"_"+category,"param",[0.0,0.333])
            card.addSystematic("meanSyst1_Wjets_"+lepton+"_"+category,"param",[0.0,0.333])
            card.addSystematic("widthSyst_Wjets_"+lepton+"_"+category,"param",[0.0,0.333])

            card.addSystematic("slopeSystMJJ_Wjets_"+purity,"param",[0.0,0.333])
            card.addSystematic("meanSystMJJ_Wjets_"+purity,"param",[0.0,0.333])
            card.addSystematic("widthSystMJJ_Wjets_"+purity,"param",[0.0,0.333])

            card.addSystematic("slopeSyst_topOther_"+lepton+"_"+category,"param",[0.0,0.333])
            card.addSystematic("meanSyst0_topOther_"+lepton+"_"+category,"param",[0.0,0.333])
            card.addSystematic("meanSyst1_topOther_"+lepton+"_"+category,"param",[0.0,0.333])
            card.addSystematic("widthSyst_topOther_"+lepton+"_"+category,"param",[0.0,0.333])

            card.addSystematic("slopeSystMJJ_topOther_"+purity,"param",[0.0,0.333])
            if purity=='HP':
                card.addSystematic("meanSystMJJ_topOther_"+purity,"param",[0.0,0.333])
                card.addSystematic("widthSystMJJ_topOther_"+purity,"param",[0.0,0.333])

            card.addSystematic("slopeSyst_topW_"+lepton+"_"+category,"param",[0.0,0.333])
            card.addSystematic("meanSyst_topW_"+lepton+"_"+category,"param",[0.0,0.333])
            card.addSystematic("widthSyst_topW_"+lepton+"_"+category,"param",[0.0,0.333])


            card.makeCard()

#make combined cards



print cmd
            
