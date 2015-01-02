/*Code file details.*/
#include "croot/samples/factorial.h"
#include "croot/common/some_lib.h"
#include <stdio.h>

namespace cc_samples {

void print_math_number() {
  printf("%.5f\n", cc_common::get_math_number());
}

int factorial(int n) {
  if (n < 0) {
    return cc_common::get_special_number();
  }
  int product = 1;
  for (;n > 0; --n) {
    product *= n;
  }
  return product;
}

}  // cc_samples
