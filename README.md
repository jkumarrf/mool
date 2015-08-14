mool: The mool build tool.
==========================

#### What is it?

* It is a collection of scripts that help building code written in C++, Python,
Scala or Java.
* It is very similar to the following tools:

1. [Twitter pants](http://pantsbuild.github.io/)
2. [Facebook buck](http://facebook.github.io/buck/)

The current implementation has been extended from another implementation of
[mooltool](https://github.com/anirban001/mooltool).

#### Installation
Checkout latest code from this repository and run following command from repo
root:
`python2.7 installer/install\_mooltool.py`

Above command takes some time and creates a complete working setup in your
current working directory. For more installation options run installer script
with `--help` option.

All the tests should pass at the end of installation!

#### Usage
Once installation is done, you can immediately start using by:

```bash
# Set project root to repository root directory. This is used by shared_settings.
export PROJECT_ROOT=$(git rev-parse --show-toplevel)
# Load all general settings. This also exposes init_working_dirs() function.
source shared_settings.sh
# Load all installation specific or user settings. Check contents of
# local_setting.sh for more details on this.
source local_settings.sh
# Set build root, initialize temporary directories.
export BUILD_ROOT=${PROJECT_ROOT}/code_root
init_working_dirs
# Lets build a rule now.
bu do_test mool.java.com.rocketfuel.ei.common.RpcTest
```
Above steps should work and you can create a handy bash script with above commands.

#### Installation help
It requires following prerequisites:
* Java >= 1.7.0
* Python >= 2.7.3
* g++
* openssl >= 1.0.0

**Environment variables:**
* JAVA_HOME: In case you have more than one JDKs installed or you have java installation in custom path, you can appropriately set *JAVA_HOME* environment variable.
* OPENSSL_INSTALL_PATH: Latest OpenSSL version is required to compiled thrift from source. You can check your current version using `openssl -v`. In case you have openssl installation in custom path, set environment variable *OPENSSL_INSTALL_PATH*.

---
## General Rule Format
BLD file format is mostly _JSON_ with _comments_. Each rule has a `rule_name` which hold a dictionary of key/value pairs. Most rules have following skelton:
```python
"rule_name": {
    "rule_type": <java_lib/cc_bin/...>
    "srcs": [List of sources],
    "deps": [List of dependencies]
}
```
##### Rule types:
- **c++**: `cc_lib`, `cc_bin`, `cc_test`
- **java**: `java_lib`, `java_bin`, `java_test`
- **python**: `py_lib`, `py_bin`, `py_test`
- **scala**: `scala_lib`, `scala_bin`, `scala_test`
- **clojure**: `clojure_lib`, `clojure_bin`, `clojure_test`
- **protobuf**: `cc_proto_lib`, `java_proto_lib`, `py_proto_lib`
- **thrift**: `cc_thrift_lib`, `java_thrift_lib`, `py_thrift_lib`

#### Dependency path:
You can specify dependencies on other rules and mool builds all rule dependencies before building given rule. Dependencies can have a full path which is of the format `mool.path.to.bld.file.RuleName` or it can be relative path w.r.t given BLD file.

Examples:
* "mool.java.com.example.project.MyPrototype" refers to a rule which is in file `${BUILD_ROOT}/java/com/example/project/BLD` with name `MyPrototype`.
* ".Slf4jApi" refers to build rule in same BLD file.
* ".resources.TestResources" refers to a build rule in file `<curret_directory>/resources/BLD` with name `TestResources`.

---


### 1. Java Build Rules.
Each `java_lib` and `java_bin` rules produce one out file which is named after `rule_name`.
```python
# Libraries.
"HelloWorld": {
    "rule_type": "java_lib",
    "srcs": ["HelloWorld.java"]
},

"StringMatcher": {
    "rule_type": "java_lib",
    "srcs": ["JavaStringMatcher.java"],
    "compileDeps": [".ApacheCommonStripped"]
},

"CommonsLang3": {
    "rule_type": "java_lib",
    "maven_specs": {
        "repo_url": "http://repo1.maven.org/maven2",
        "group_id": "org.apache.commons",
        "artifact_id": "commons-lang3",
        "version": "3.0"
        #"classifier": "some classifier"
    }
},

"ApacheCommmonStripped": {
    "rule_type": "java_lib",
    "deps": [
        # Refer to other rules in this file using relative path.
        ".CommonsLang3"
    ],
    "jar_include_paths": [
        "org/apache/commons/lang3/StringUtils.class"
    ]
},

# Binaries.
"HelloWorldRunnable": {
    "rule_type": "java_bin",
    "srcs": ["HelloWorld.java"],
    "main_class": "com.example.HelloWorld"
},

"HelloWorldUsingDep": {
    "rule_type": "java_bin",
    "deps": [".HelloWorld"],
    "main_class": "com.example.HelloWorld"
},

# Tests.
"HelloCheck": {
    "rule_type": "java_test",
    "srcs": ["TestHelloWorld.java"],
    "deps": [
        ".HelloWorld",
        # Add TestNg and JCommander libs as mool supports TestNG
        # tests only as of now.
        "mool.java.mvn.org.TestNg",
        "mool.java.mvn.com.buest.JCommander"
    ],
    "test_classes": ["com.example.HelloCheck"],
    # ["unit"] is used by default is none is specified.
    "test_groups": ["my_test_group"]
}

```

#### Details of Java rule keys
- **rule_name**: One of [`java_lib`, `java_bin`, `java_test`]
- **srcs**: Java sources present in the same directory as BLD file _(list)_
- **deps**: deps used for compiling and packed with final rule output _(list)_
- **compileDeps**: deps used only for compilation
- **precompiled_deps**: external deps without a build rule, example: `/user/home/path/to/jar` or `env.HOME/path/to/jar`. We expand env.`<variable_name>` by looking up environment variables.
- **compile_params**: arguments for javac compiler.
- **runtime_params**: arguments for java binary, used for java_test
- **test_groups**: list of TestNg groups to run tests on
- ~~**test_class**~~: test class name; _deprecated_ instead use `test_classes`
- **test_classes**: list of classes to be passed to testng
- **main_class**: main java class for making executable jar
- **maven_specs**: maven specifications for referring to thirdparty jars (artifacts)
  - *repo_url*: artifact repo url
  - *group_id*: artifact group id
  - *artifact_id*: artifact id
  - *version*: artifact version number
  - *classifier*: _optional_ artifact classifier
- **extract_deps**: list of deps to be extracted in cwd during test execution, useful for file read/write tests.
- **jar_include_paths**: list of paths to be included in final jar, for a directory path, whole directory is included, i.e. `com/example/project1` will include all the classes which are inside com/example/project1 directory of jar.
- **jar_exclude_paths**: list of paths to be excluded, *this is applied before inclusions*
- **includeDeps**: extra key to specify if "deps" should be packed with final jar or not, default `False` for `java_test` rule, `True` otherwise.
- **java_version**```: java version to be passed to `--source` and `--target` params of `javac` command. It has to be at least the jdk version you are using.
---

### 2. C++ Build Rules.
`cc_lib` creates a collection of object (.o) files and copies mentioned headers (.h) files to output directory. `cc_bin` and `cc_test` create single executable file. We support GMOCK for cc tests.
```python
# Libraries.
"hello_world": {
    "rule_type": "cc_lib",
    # Multiple source/header files can be added in one lib rule.
    "srcs": [ "helloworld.cc"],
    "hdrs": [ "helloworld.h"]
},

"hello_gcc": [
    "rule_type": "cc_lib",
    # All source files MUST be of same type '.c' or '.cc'
    # We use `gcc` if all sources are '.c' files else we use `g++`.
    "srcs": ["hello_gcc.c", "hello_gcc_macros.c"],
    "hdrs": ["hello_gcc.h"]
],

"factorial_lib": {
    "rule_type": "cc_lib",
    "srcs": ["factorial.cc"],
    "hdrs": ["factorial.h"]
},

# Binaries.
"factorial": {
    "rule_type": "cc_bin",
    # You can specify only one cc file for cc_bin rule.
    "srcs": ["factorial_main.cc"],
    "deps": [".factorial_lib"],
    # Headers from custom locations can be added here.
    # You can use environment variables as well to keep it portable.
    "incdirs": ["env.BOOST_DIR/include"],
    # Library directories used by `gcc/g++` to search for "sys_deps".
    "libdirs": ["env.BOOST_DIR/lib"],
    "sys_deps": ["-lboost_regex", "-pthread"]
},

# Tests.
"factorial_test": {
    "rule_type": "cc_test",
    "srcs": ["factorial_test.cc"],
    "deps": [".factorial"],
    # We support cc testing using gtest & gmock libraries.
    # Following libs are added by mool by default, so these are not ideally required here.
    "precompiled_deps": ["env.GTEST_MAIN_LIB", "env.GTEST_MOCK_LIB"]
}
```

---

### 3. Python Build Rules.
`py_lib` compiles and packs all python sources into a zip file, `py_bin` appends an executable header to _py_lib_ zip and `py_test` creates python library and runs it using py.test. All dependencies of a rule are always packed to create a standalone python library or binary.

As of now we don't support a direct way to refer to thirdparty python dependencies but we use python virtual environment for running all mool commands so one can simply install the required dependencies using `pip install <dep name==version>` command. Even better maintain a `requirements.txt` file and just use `pip install -r path/to/requirements.txt` file to install all dependencies from requirements file.

Mool also does pylint and pep8 checking for you for all python rules by default!
```python
# Libraries.
"hello_world_utils": {
    "rule_type": "py_lib",
    "srcs": ["hello_world_utils.py"]
},

# Binaries.
"hello_world": {
    "rule_type": "py_bin",
    "srcs": ["hello_world_main.py"],
    "deps": [".hello_world_utils"],
    # Path to main module is always w.r.t. BUILD_ROOT.
    # NOTICE that it uses file name 'hello_world_main' and then the main function 'main_func' inside it.
    "main_method": "my.first_package.hello_world_main.main_func"
}

# Tests.
"simple_test": {
    "rule_type": "py_test",
    "srcs": ["simple_py_test.py"],
    "deps": [".hello_world_utils"]
}
```
