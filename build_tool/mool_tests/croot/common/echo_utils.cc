/*Code file details.*/
#include "croot/common/echo_utils.h"

#include <stdio.h>

namespace cc_common {

void echo(const string& text) {
  printf("%s\n", text.c_str());
}

}  // cc_common
