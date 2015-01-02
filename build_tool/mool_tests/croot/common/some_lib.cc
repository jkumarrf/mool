/*Code file details.*/
#include "croot/common/some_lib.h"
#include <math.h>

namespace cc_common {

double get_math_number() {
  return sqrt(2.0);
}

int get_special_number() {
  static const int kSpecialNumber = -1;
  return kSpecialNumber;
}

}  // cc_common
