/*Header file details.*/
#ifndef __CROOT_COMMON_GLOBAL_MACROS__
#define __CROOT_COMMON_GLOBAL_MACROS__
#include <stdio.h>
#include <stdlib.h>

#define CHECK(_x) \
  if (!(_x)) { \
    printf("Check failed in File %s Line %d\n", __FILE__, __LINE__); \
    exit(1); \
  }

#endif  // __CROOT_COMMON_GLOBAL_MACROS__
