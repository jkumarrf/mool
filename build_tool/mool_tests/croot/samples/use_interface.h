/*Header file details.*/
#ifndef __CROOT_SAMPLES_USE_INTERFACE__
#define __CROOT_SAMPLES_USE_INTERFACE__

namespace cc_samples {

class UseInterface {
 public:
  virtual void use() = 0;
};

void use_interface(UseInterface* interface);

}  // cc_samples

#endif  // __CROOT_SAMPLES_USE_INTERFACE__
