/*Code file details.*/
#include "croot/samples/use_interface.h"

namespace cc_samples {

void use_interface(UseInterface* interface) {
  if (interface) {
    interface->use();
  }
}

}  // cc_samples
