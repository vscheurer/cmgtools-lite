#include "CMGTools/VVResonances/interface/GaussianSumTemplateMaker.h"
#include "CMGTools/VVResonances/interface/PTWeightTemplateMaker.h"
#include "CMGTools/VVResonances/interface/GaussianSumTemplateMaker1D.h"

namespace cmg{

  struct cmg_vvresonances_dictionary {
    cmg::GaussianSumTemplateMaker templateMaker;
    cmg::GaussianSumTemplateMaker1D templateMaker1D;
    cmg::PTWeightTemplateMaker ptTemplateMaker;
  };
}
