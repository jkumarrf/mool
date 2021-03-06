"""Rule builder module."""

import logging
import os
import subprocess

import shared_utils as su
import java_common as jc
import python_common as pc
import release_package as rp
import rule_handler as rh


FILE_DEP_PREFIX = 'FILE: '

MAX_LOOP_COUNT = 5000
TRACE_COMMANDS = (os.environ.get('DEBUG_MODE', '') != '')

# Keys having relative path in rule, beginning with '.'.
EXPAND_RULE_KEYS = [su.DEPS_KEY, su.COMPILE_DEPS_KEY, su.PACKAGE_TESTS_KEY,
                    su.PACKAGE_MODULES_KEY, su.EXTRACT_RESOURCES_DEP_KEY]
# Keys which can have 'env.' variable, that should to be expanded.
EXPAND_VARS_KEYS = [su.SYS_DEPS_KEY, su.OTHER_INCLUDE_DIRS, su.PC_DEPS_KEY,
                    su.COMPILE_PARAMS_KEY]


class Error(Exception):
  """Generic error class."""


def _run_commands(command_list):
  """Run the commands generated by the steps."""
  tracer = logging.info if TRACE_COMMANDS else logging.debug
  for command in command_list:
    assert command
    tracer('Command: %s', str(command))
    if command[0] == su.PYTHON_CREATE_INITIALIZERS:
      pc.create_initializers(command[1:])
    elif command[0] == su.PYTHON_COMPILE_ALL_CURRDIR:
      pc.compile_all(command[1:])
    elif command[0] == su.CHANGE_CURR_DIR:
      su.change_dir(command[1:])
    elif command[0] == su.PERFORM_JAVA_LINK_ALL_CURRDIR:
      jc.perform_java_linkall_currdir(command[1:])
    elif command[0] == su.PERFORM_ZIP_ALL_CURRDIR:
      rp.zip_all_currdir(command[1:])
    elif command[0] == su.PYTHON_EXPAND_LIB:
      pc.expand_lib(command[1:])
    elif command[0] == su.JAVA_LINK_JAR_COMMAND:
      jc.perform_linking(command[1:])
    elif command[0] == su.PYTHON_LINK_ALL:
      pc.perform_linking(command[1:])
    else:
      subprocess.check_call(command)


def _split_rule_symbol(rule_symbol):
  """Split rule symbol."""
  rule_parts = rule_symbol.split(su.RULE_SEPARATOR)
  rule_path = su.RULE_SEPARATOR.join(rule_parts[:-1])
  rule_name = rule_parts[-1:][0]
  return rule_path, rule_name


class RuleBuilder(object):
  """Traverse rules graph and apply them."""
  def __init__(self, rules_list):
    """Initialize."""
    self._all_rules = '{}{}'.format(su.RULE_SEPARATOR, su.ALL_RULES_KEY)
    self._all_light_rules = '{}{}'.format(
        su.RULE_SEPARATOR, su.ALL_LIGHT_RULES_KEY)
    self._target_prefix = su.BUILD_RULE_PREFIX
    self._rule_handler = rh.RuleHandler()
    self._rules_map = {}
    self._rule_file_cache = {}
    self._build_order = []
    self._load_rules_list_to_map(rules_list)
    self._load_build_order()
    self._load_all_recursive_deps()

  def _expand_symbol(self, item, path):
    """Rule symbol expansion routine."""
    if item.startswith(su.RULE_SEPARATOR):
      return '{}{}'.format(path, item)
    if item.startswith(self._target_prefix):
      return item
    assert False

  def _expand_symbols_in_rule(self, rule_details, rule_path):
    """Expand symbols in the rule details dictionary."""
    for key in EXPAND_RULE_KEYS:
      value = rule_details.get(key, [])
      rule_details[key] = [self._expand_symbol(x, rule_path) for x in value]
    for key in EXPAND_VARS_KEYS:
      value = rule_details.get(key, [])
      rule_details[key] = [su.expand_env_vars(x) if x.startswith(
                           su.PC_DEPS_PREFIX) else x for x in value]

  def _get_rule_file(self, rule_symbol):
    """Get rule file from rule symbol."""
    assert rule_symbol.startswith(self._target_prefix)
    rule_parts = rule_symbol.split(su.RULE_SEPARATOR)
    assert all([r for r in rule_parts])
    assert len(rule_parts) >= 3
    rule_parts[0] = su.BUILD_ROOT
    rule_parts[-1] = su.BUILD_FILE_NAME
    return os.sep.join(rule_parts)

  def _load_file_cache(self, rule_file):
    """Load file contents from file cache."""
    if rule_file not in self._rule_file_cache:
      self._rule_file_cache[rule_file] = su.read_build_file(rule_file)
    return self._rule_file_cache[rule_file]

  def _get_rule_details(self, rule_path, rule_name, rule_file, rule_symbol):
    """Load rule details from symbol."""
    assert rule_symbol.startswith(self._target_prefix)
    # Discourage all upper case build rules to avoid conflict with
    # keyword 'ALL'.
    assert rule_symbol != rule_symbol.upper()
    if rule_name not in self._load_file_cache(rule_file):
      raise Error('Rule "{}" does not exist in {}.'
                  .format(rule_name, rule_file))
    rule_details = self._load_file_cache(rule_file)[rule_name]
    assert su.PATH_KEY not in rule_details
    rule_details[su.PATH_KEY] = rule_path
    assert su.NAME_KEY not in rule_details
    rule_details[su.NAME_KEY] = rule_name
    self._expand_symbols_in_rule(rule_details, rule_path)
    if su.RELEASE_PACKAGE_TYPE == rule_details[su.TYPE_KEY]:
      rule_details[su.DEPS_KEY].extend(rule_details[su.PACKAGE_MODULES_KEY])
      rule_details[su.DEPS_KEY].extend(rule_details[su.PACKAGE_TESTS_KEY])
    if su.JAVA_TEST_TYPE == rule_details[su.TYPE_KEY]:
      rule_details[su.DEPS_KEY].extend(
          rule_details.get(su.EXTRACT_RESOURCES_DEP_KEY, []))
    # The list of "all dependencies" must be computed automatically. There are
    # no realistic known scenarios where this list should be specified in the
    # BLD specifications file.
    rule_details[su.ALL_DEPS_KEY] = []
    rule_details[su.ALL_DEP_PATHS_KEY] = [rule_file]
    dir_name = os.path.dirname(rule_file)
    su.check_dirname(dir_name)
    rule_details[su.DIR_ROOT_KEY] = dir_name
    rule_details[su.SYMBOL_KEY] = rule_symbol
    return rule_details

  def _load_rules_list_to_map(self, rules_list):
    """Load rules from list to map."""
    active_list = rules_list[:]
    iters = 0
    while active_list:
      rule_symbol = active_list[0]
      active_list = active_list[1:]
      if rule_symbol in self._rules_map:
        continue
      iters += 1
      assert iters <= MAX_LOOP_COUNT
      rule_path, rule_name = _split_rule_symbol(rule_symbol)
      rule_file = self._get_rule_file(rule_symbol)
      self._load_file_cache(rule_file)
      if rule_symbol.endswith(self._all_rules):
        active_list.extend(
            ['{}{}{}'.format(rule_path, su.RULE_SEPARATOR, r)
             for r in self._rule_file_cache[rule_file].keys()])
      elif rule_symbol.endswith(self._all_light_rules):
        light_rules_list = [
            l for l in self._rule_file_cache[rule_file]
            if self._rule_file_cache[rule_file][l].get(
                su.RULE_WEIGHT_KEY, None) is None]
        active_list.extend(['{}{}{}'.format(rule_path, su.RULE_SEPARATOR, r)
                            for r in light_rules_list])
      else:
        rule_details = self._get_rule_details(
            rule_path, rule_name, rule_file, rule_symbol)
        self._rules_map[rule_symbol] = rule_details
        active_list.extend(rule_details[su.DEPS_KEY])
        active_list.extend(rule_details[su.COMPILE_DEPS_KEY])

  def _check_test_dependency(self, rule_details):
    """A non test rule shouldn't have any test dependency."""
    # Test commands key is only set iff the rule is a test rule.
    if any([self._rule_handler.rule_test(rule_details),
            rule_details[su.TYPE_KEY] == su.RELEASE_PACKAGE_TYPE]):
      return
    depends_on = []
    depends_on.extend(rule_details[su.DEPS_KEY])
    depends_on.extend(rule_details[su.COMPILE_DEPS_KEY])
    for rule in depends_on:
      if self._rule_handler.rule_test(self._rules_map[rule]):
        raise Error('Non test rule {} cannot depend on test rule {}'.format(
                    rule_details[su.SYMBOL_KEY], rule))

  def _load_build_order(self):
    """Load build order from rules map."""
    # Build order is a list of list of rule symbols. Every first order list
    # is a list of rule symbols that can be built in parallel.
    active_set = set(self._rules_map.keys())
    built_set = set()
    iters = 0
    while active_set:
      iters += 1
      assert iters <= MAX_LOOP_COUNT
      ready_set = set()
      for rule_symbol in active_set:
        deps = self._rules_map[rule_symbol][su.DEPS_KEY][:]
        deps.extend(self._rules_map[rule_symbol][su.COMPILE_DEPS_KEY])
        if all([s in built_set for s in deps]):
          ready_set.add(rule_symbol)
      assert ready_set
      self._build_order.append(sorted(list(ready_set)))
      built_set.update(ready_set)
      active_set = [s for s in active_set if s not in ready_set]

  def _load_all_recursive_deps(self):
    """Load all recursive dependencies for build optimization."""
    for build_group in self._build_order:
      for rule_symbol in build_group:
        rule_details = self._rules_map[rule_symbol]
        all_deps = [rule_symbol]
        for dep_rule_symbol in rule_details[su.DEPS_KEY]:
          dep_rule_details = self._rules_map[dep_rule_symbol]
          include_recursively = (
              self._rule_handler.rule_include_deps_recursively(
                  dep_rule_details))
          if include_recursively:
            all_deps.extend(dep_rule_details[su.ALL_DEPS_KEY])
          all_deps.append(dep_rule_symbol)
        rule_details[su.ALL_DEPS_KEY] = list(set(all_deps))

  def _build_rule_details(self, rule_symbol, rule_details):
    """Execute build steps from rule detail."""
    file_list = self._rule_handler.rule_file_list(rule_details)
    if not su.needs_build(rule_details[su.WDIR_KEY], file_list):
      logging.info(' Skipping build for %s', rule_symbol)
      return
    if not su.TEST_MODE_EXECUTION:
      su.cleandir(rule_details[su.WDIR_KEY])
      start_time_milli = su.get_epoch_milliseconds()
    command_list = self._rule_handler.rule_build_commands(rule_details)
    _run_commands(command_list)
    su.save_file_list_cache(rule_details[su.WDIR_KEY], file_list)
    if not su.TEST_MODE_EXECUTION:
      end_time_milli = su.get_epoch_milliseconds()
      logging.info('Time (in seconds): %.2f',
                   (end_time_milli - start_time_milli) / 1000.0)

  def _add_test_instrumentation(self, rule_symbol, rule_details,
                                dependency_dict):
    """Add unit test specific instrumentation."""
    if not su.TEST_MODE_EXECUTION:
      return
    dependency_dict[rule_symbol] = [
        FILE_DEP_PREFIX + self._rules_map[rs][su.OUT_KEY]
        for rs in rule_details[su.COMPILE_DEPS_KEY]]
    dependency_dict[rule_symbol].extend(
        [FILE_DEP_PREFIX + f for f in rule_details[su.ALL_DEP_PATHS_KEY]])

  def _build_rule_symbol(self, rule_symbol, run_tests, dependency_dict):
    """Build a symbol assuming all dependencies have been built."""
    logging.info('-----\nBuilding %s', rule_symbol)
    rule_details = self._rules_map[rule_symbol]
    self._rule_handler.rule_setup(rule_details, self._rules_map)
    self._add_test_instrumentation(rule_symbol, rule_details, dependency_dict)
    self._build_rule_details(rule_symbol, rule_details)
    self._check_test_dependency(rule_details)
    if run_tests:
      command_list = self._rule_handler.rule_test(rule_details)
      if command_list:
        logging.info('-----\nRunning test %s', rule_symbol)
        _run_commands(command_list)

  def do_builds(self, run_tests, dependency_dict):
    """Execute the rules."""
    for build_group in self._build_order:
      # Note: Parallelization logic should go here.
      for rule_symbol in build_group:
        self._build_rule_symbol(rule_symbol, run_tests, dependency_dict)
    return 0
