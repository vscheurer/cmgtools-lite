#include "RooDataSet.h"
#include "TH2.h"
#include "TH1.h"
namespace cmg {

class GaussianSumTemplateMaker {
 public:
  GaussianSumTemplateMaker();
  ~GaussianSumTemplateMaker();
  GaussianSumTemplateMaker(const RooDataSet*,const char*, const char*,TH2*,TH2*,TH2*,TH2*,TH2*);


 private:
  double gaus2D(double, double,double,double,double,double);
};


}
