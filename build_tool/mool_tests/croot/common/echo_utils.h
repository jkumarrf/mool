/*Header file details.*/
#ifndef __CROOT_COMMON_ECHO_UTILS__
#define __CROOT_COMMON_ECHO_UTILS__

#include <string>

namespace cc_common {

using std::string;

// This header file shows a sample library for demonstrating cross directory
// dependencies.
void echo(const string& text);

}  // cc_common

#endif  // __CROOT_COMMON_ECHO_UTILS__
