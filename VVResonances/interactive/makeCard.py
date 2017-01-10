import ROOT
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
from CMGTools.VVResonances.statistics.DataCardMaker import DataCardMaker
cmd='combineCards.py '


for category in ['nob','vbf']:
    if category=='vbf':
        pur=['NP']
    else:
        pur=['HP','LP']
    for purity in pur:
        for lepton in ['e','mu']:
            card=DataCardMaker(lepton,purity,'13TeV',12900,category)
            cat='_'.join([category,lepton,purity,'13TeV'])
            cmd=cmd+" "+cat+'=datacard_'+cat+'.txt '

            #WW signal-MVV
            card.addMVVSignalParametricShape("XWW_MVV","MLNuJ","LNuJJ_XWW_MVV_"+lepton+".json",{'CMS_scale_j':1,'CMS_scale_MET':1.0},{'CMS_res_j':1.0,'CMS_res_MET':1.0})
            if purity=='LP':
                card.addMJJSignalParametricShape("Wqq","MJ","LNuJJ_XWW_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0})
            else:
                card.addMJJSignalParametricShapeNOEXP("Wqq","MJ","LNuJJ_XWW_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0})

            card.product("XWW","Wqq","XWW_MVV")



            #WZ signal-MVV
#            card.addMVVSignalParametricShape("XWZ_MVV","MLNuJ","LNuJJ_XWZ_MVV_"+lepton+".json",{'CMS_scale_j':1,'CMS_scale_MET':1.0},{'CMS_res_j':1.0,'CMS_res_MET':1.0})
#            if purity=='LP':
#                card.addMJJSignalParametricShape("Zqq","MJ","LNuJJ_XWZ_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0})
#            else:
#                card.addMJJSignalParametricShapeNOEXP("Zqq","MJ","LNuJJ_XWZ_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0})
#            card.product("XWZ","Zqq","XWZ_MVV")




            card.addParametricYield("XWW",0,"LNuJJ_XWW_"+lepton+"_"+purity+"_"+category+"_yield.json")
            #For VBF use this:
#            card.addParametricYield("XWW",0,"LNuJJ_VBFXWW_"+lepton+"_"+purity+"_"+category+"_yield.json")
            #For WZ use this:
#            card.addParametricYield("XWZ",0,"LNuJJ_XWZ_"+lepton+"_"+purity+"_"+category+"_yield.json")

            #QCD
            rootFile="LNuJJ_nonRes_2D_"+lepton+"_"+purity+"_"+category+".root"
            qcdTag ="_".join([lepton,purity,category])
#            card.addHistoShapeFromFile("nonRes",["MLNuJ","MJ"],rootFile,"histo",['ScaleY:CMS_VV_LNuJ_nonRes_ScaleY_'+qcdTag,'ScaleX:CMS_VV_LNuJ_nonRes_ScaleX_'+qcdTag,'ResX:CMS_VV_LNuJ_nonRes_ResX_'+qcdTag,'ResY:CMS_VV_LNuJ_nonRes_ResY_'+qcdTag],False,0)       
            card.addHistoShapeFromFile("nonRes",["MLNuJ","MJ"],rootFile,"histo",['ScaleY:CMS_VV_LNuJ_nonRes_ScaleY_'+qcdTag,'ScaleX:CMS_VV_LNuJ_nonRes_ScaleX_'+qcdTag],False,0)       


            
            card.addFixedYieldFromFile("nonRes",1,"LNuJJ_"+lepton+"_"+purity+"_"+category+".root","nonRes")

            #Wjet
            if purity =='LP':
                card.addMJJSignalParametricShapeNOEXP("WqqRes","MJ","LNuJJ_MJJ_resW_LP.json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0},"MLNuJ")
            else:
                card.addMJJSignalParametricShapeNOEXP("WqqRes","MJ","LNuJJ_MJJ_resW_HP.json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0},"MLNuJ")     

            rootFile="LNuJJ_resW_MVV_"+lepton+"_"+purity+"_"+category+".root"
            resWTag ="_".join([lepton,purity,category])
#            card.addHistoShapeFromFile("resW_MVV",["MLNuJ"],rootFile,"histo",['Scale:CMS_VV_LNuJ_resW_Scale_'+resWTag,'Res:CMS_VV_LNuJ_resW_Res_'+resWTag],False,0)       
            card.addHistoShapeFromFile("resW_MVV",["MLNuJ"],rootFile,"histo",['Scale:CMS_VV_LNuJ_resW_Scale_'+resWTag],False,0)       

            card.conditionalProduct("resW","WqqRes","MLNuJ","resW_MVV")
            card.addFixedYieldFromFile("resW",2,"LNuJJ_"+lepton+"_"+purity+"_"+category+".root","resW")

            #DATA
            card.importBinnedData("LNuJJ_"+lepton+"_"+purity+"_"+category+".root","data",["MLNuJ","MJ"])
            #####SYSTEMATICS

            #luminosity
            card.addSystematic("CMS_lumi","lnN",{'XWW':1.05,'XWZ':1.05,'nonRes':1.05,'resW':1.05})

            #lepton efficiency
            card.addSystematic("CMS_eff_"+lepton,"lnN",{'XWW':1.1,'XWZ':1.1,'nonRes':1.1,'resW':1.1})

            #W+jets cross section in acceptance-dominated by pruned mass
            card.addSystematic("CMS_VV_LNuJ_nonRes_norm_"+purity+"_"+category,"lnN",{'nonRes':1.5})
            card.addSystematic("CMS_VV_LNuJ_resW_norm_"+purity+"_"+category,"lnN",{'resW':1.5})

            #tau21 
            if purity=='HP':
                card.addSystematic("CMS_VV_LNuJ_tau21_eff","lnN",{'resW':1-0.08,'XWW':1-0.08,'XWZ':1-0.08})

            if purity=='LP':
                card.addSystematic("CMS_VV_LNuJ_tau21_eff","lnN",{'resW':1+0.25,'XWW':1+0.25,'XWZ':1+0.25})


            #inter-category
            if category=='vbf':
                card.addSystematic("CMS_VV_LNuJ_vbf_intercategory","lnN",{'XWW':1.3,'XWZ':1.3})
            else:    
                card.addSystematic("CMS_VV_LNuJ_vbf_intercategory","lnN",{'XWW':0.95,'XWZ':0.95})

            card.addSystematic("CMS_btag_fake","lnN",{'XWW':1+0.02,'XWZ':1+0.02})



               
            #pruned mass scale    
            card.addSystematic("CMS_scale_j","param",[0.0,0.02])
            card.addSystematic("CMS_res_j","param",[0.0,0.05])
            card.addSystematic("CMS_scale_prunedj","param",[0.01,0.04])
            card.addSystematic("CMS_res_prunedj","param",[0.0,0.05])
            card.addSystematic("CMS_scale_MET","param",[0.0,0.02])
            card.addSystematic("CMS_res_MET","param",[0.0,0.01])
            card.addSystematic("CMS_VV_LNuJ_nonRes_ScaleY_"+qcdTag,"param",[0.0,0.6])
            card.addSystematic("CMS_VV_LNuJ_nonRes_ScaleX_"+qcdTag,"param",[0.0,0.333])
#            card.addSystematic("CMS_VV_LNuJ_nonRes_ResX_"+qcdTag,"param",[0.0,0.333])
#            card.addSystematic("CMS_VV_LNuJ_nonRes_ResY_"+qcdTag,"param",[0.0,0.333])
                


            card.addSystematic("CMS_VV_LNuJ_resW_Scale_"+resWTag,"param",[0.0,0.333])
#            card.addSystematic("CMS_VV_LNuJ_resW_Res_"+resWTag,"param",[0.0,0.333])


            card.makeCard()

#make combined cards



print cmd
            
