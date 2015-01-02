// Sample C++ binary using the factorial library.
#include "croot/samples/factorial.h"

#include "croot/common/echo_utils.h"
#include "croot/common/global_macros.h"
#include "libxml/xmlreader.h"

#include <stdio.h>
#include <string.h>

using std::string;


void use_xml() {
  string xml_string = "<root>1</root>";
  xmlTextReaderPtr reader = xmlReaderForMemory(
      xml_string.c_str(), strlen(xml_string.c_str()), NULL, NULL, 0);
  CHECK(reader);
  xmlFreeTextReader(reader);
}

int main(int argc, char* argv[]) {
  CHECK(true);
  use_xml();
  cc_common::echo("\nHello, world.\n");
  cc_samples::print_math_number();
  static const int kValue = 9;
  printf("Factorial(%d) = %d\n", kValue,
         cc_samples::factorial(kValue));
}
