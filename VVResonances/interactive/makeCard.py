import ROOT
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
from CMGTools.VVResonances.statistics.DataCardMaker import DataCardMaker
cmd='combineCards.py '


for category in ['nob']:
    if category=='vbf':
        pur=['NP']
    else:
        pur=['HP','LP']
    for purity in pur:
        for lepton in ['e','mu']:
            card=DataCardMaker(lepton,purity,'13TeV',35900,category)
            cat='_'.join([category,lepton,purity,'13TeV'])
            cmd=cmd+" "+cat+'=datacard_'+cat+'.txt '

            #WW signal-MVV
            card.addMVVSignalParametricShape("XWW_MVV","MLNuJ","LNuJJ_XWW_MVV_"+lepton+".json",{'CMS_scale_j':1,'CMS_scale_MET':1.0},{'CMS_res_j':1.0,'CMS_res_MET':1.0})
            if purity=='LP':
                card.addMJJSignalParametricShape("Wqq","MJ","LNuJJ_XWW_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0})
            else:
                card.addMJJSignalParametricShapeNOEXP("Wqq","MJ","LNuJJ_XWW_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0})
#
            card.product("XWW","Wqq","XWW_MVV")


            #WZ signal-MVV
#            card.addMVVSignalParametricShape("XWZ_MVV","MLNuJ","LNuJJ_XWZ_MVV_"+lepton+".json",{'CMS_scale_j':1,'CMS_scale_MET':1.0},{'CMS_res_j':1.0,'CMS_res_MET':1.0})
#            if purity=='LP':
#                card.addMJJSignalParametricShape("Zqq","MJ","LNuJJ_XWZ_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0})
#            else:
#                card.addMJJSignalParametricShapeNOEXP("Zqq","MJ","LNuJJ_XWZ_MJJ_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0})
#            card.product("XWZ","Zqq","XWZ_MVV")




            card.addParametricYield("XWW",0,"LNuJJ_XWW_"+lepton+"_"+purity+"_"+category+"_yield.json")
#            card.addParametricYield("XWZ",0,"LNuJJ_XWZ_"+lepton+"_"+purity+"_"+category+"_yield.json")

            #For VBF use this:
#            card.addParametricYield("XWW",0,"LNuJJ_VBFXWW_"+lepton+"_"+purity+"_"+category+"_yield.json")
            #For WZ use this:

            #QCD
            rootFile="LNuJJ_nonRes_2D_"+lepton+"_"+purity+"_"+category+".root"
            qcdTag ="_".join([lepton,purity,category])
#            card.addHistoShapeFromFile("nonRes",["MLNuJ","MJ"],rootFile,"histo",['OPTX:CMS_VV_LNuJ_nonRes_OPTX_'+qcdTag,'PTX:CMS_VV_LNuJ_nonRes_PTX_'+qcdTag,'PTX2:CMS_VV_LNuJ_nonRes_PTX2_'+qcdTag,'PTY:CMS_VV_LNuJ_nonRes_PTY_'+qcdTag,'OPTY:CMS_VV_LNuJ_nonRes_OPTY_'+qcdTag],False,0)        

            card.addHistoShapeFromFile("nonRes",["MLNuJ","MJ"],rootFile,"histo",['OPTX:CMS_VV_LNuJ_nonRes_OPTX_'+qcdTag,'PTX:CMS_VV_LNuJ_nonRes_PTX_'+qcdTag,'ResX:CMS_VV_LNuJ_nonRes_ResX_'+qcdTag,'OPTY:CMS_VV_LNuJ_nonRes_OPTY_'+qcdTag,'PTY:CMS_VV_LNuJ_nonRes_PTY_'+qcdTag],False,0)        


            
            card.addFixedYieldFromFile("nonRes",1,"LNuJJ_"+lepton+"_"+purity+"_"+category+".root","nonRes")

            #Wjet
            card.addMJJTopMergedParametricShape("mjjRes","MJ","LNuJJ_MJJ_resW_"+purity+".json",{'CMS_scale_prunedj':1},{'CMS_res_prunedj':1.0},{'CMS_VV_topPt_0_'+lepton+"_"+purity+"_"+category:1,'CMS_VV_topPt_1_'+lepton+"_"+purity+"_"+category:"1.0/MH^2"},"MLNuJ")   
            rootFile="LNuJJ_resW_MVV_"+lepton+"_"+purity+"_"+category+".root"
            resWTag ="_".join([lepton,purity,category])
#            card.addHistoShapeFromFile("resW_MVV",["MLNuJ"],rootFile,"histo",['Scale:CMS_VV_LNuJ_resW_Scale_'+resWTag,'Res:CMS_VV_LNuJ_resW_Res_'+resWTag],False,0)       
            card.addHistoShapeFromFile("resW_MVV",["MLNuJ"],rootFile,"histo",['PT:CMS_VV_LNuJ_resW_Scale_'+resWTag,'Res:CMS_VV_LNuJ_resW_Res_'+resWTag],False,0)       

            card.conditionalProduct("resW","mjjRes","MLNuJ","resW_MVV")
            card.addFixedYieldFromFile("resW",2,"LNuJJ_"+lepton+"_"+purity+"_"+category+".root","resW")

            #DATA
            card.importBinnedData("LNuJJ_"+lepton+"_"+purity+"_"+category+".root","data",["MLNuJ","MJ"])
            #####SYSTEMATICS

            #luminosity
            card.addSystematic("CMS_lumi","lnN",{'XWW':1.026,'XWZ':1.026})

            #lepton efficiency
            card.addSystematic("CMS_eff_"+lepton,"lnN",{'XWW':1.1,'XWZ':1.1})

            #W+jets cross section in acceptance-dominated by pruned mass
            card.addSystematic("CMS_VV_LNuJ_nonRes_norm_"+lepton+"_"+purity+"_"+category,"lnN",{'nonRes':1.5})
            card.addSystematic("CMS_VV_LNuJ_resW_norm_"+lepton+"_"+purity+"_"+category,"lnN",{'resW':1.5})

            #tau21 
            if purity=='HP':
                card.addSystematic("CMS_VV_LNuJ_tau21_eff","lnN",{'XWW':1+0.03,'XWZ':1+0.03})

            if purity=='LP':
                card.addSystematic("CMS_VV_LNuJ_tau21_eff","lnN",{'XWW':1-0.1,'XWZ':1-0.1})


            #inter-category
#            if category=='vbf':
#                card.addSystematic("CMS_VV_LNuJ_vbf_intercategory","lnN",{'XWW':1.3,'XWZ':1.3})
#            else:    
#                card.addSystematic("CMS_VV_LNuJ_vbf_intercategory","lnN",{'XWW':0.95,'XWZ':0.95})

            card.addSystematic("CMS_btag_fake","lnN",{'XWW':1+0.02,'XWZ':1+0.02})



               
            #pruned mass scale    
            card.addSystematic("CMS_scale_j","param",[0.0,0.02])
            card.addSystematic("CMS_res_j","param",[0.0,0.05])
            card.addSystematic("CMS_scale_prunedj","param",[-0.008,0.005])
            card.addSystematic("CMS_res_prunedj","param",[0.08,0.06])
            card.addSystematic('CMS_VV_topPt_0_'+lepton+"_"+purity+"_"+category,"param",[0.0,0.2])
            card.addSystematic('CMS_VV_topPt_1_'+lepton+"_"+purity+"_"+category,"param",[0.0,25000])

            card.addSystematic("CMS_scale_MET","param",[0.0,0.02])
            card.addSystematic("CMS_res_MET","param",[0.0,0.01])
            card.addSystematic("CMS_VV_LNuJ_nonRes_PTX_"+qcdTag,"param",[0.0,0.333])
            card.addSystematic("CMS_VV_LNuJ_nonRes_OPTX_"+qcdTag,"param",[0.0,0.333])
            card.addSystematic("CMS_VV_LNuJ_nonRes_ResX_"+qcdTag,"param",[0.0,0.333])
#            card.addSystematic("CMS_VV_LNuJ_nonRes_ScaleY_"+qcdTag,"param",[0.0,333])
            card.addSystematic("CMS_VV_LNuJ_nonRes_PTY_"+qcdTag,"param",[0.0,333])
            card.addSystematic("CMS_VV_LNuJ_nonRes_OPTY_"+qcdTag,"param",[0.0,0.6])


            card.addSystematic("CMS_VV_LNuJ_resW_PT_"+resWTag,"param",[0.0,0.333])
            card.addSystematic("CMS_VV_LNuJ_resW_Res_"+resWTag,"param",[0.0,0.333])



            card.makeCard()

#make combined cards



print cmd
            
