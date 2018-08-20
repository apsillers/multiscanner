from __future__ import division, absolute_import, with_statement, print_function, unicode_literals
import sys
import os
import types
import mock
import time

# Makes sure we use the multiscanner in ../
CWD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(CWD))
import multiscanner
sys.path.append(os.path.join(CWD, '..', 'libs'))
import common


def test_loadModule():
    """Ensure _loadModule works"""
    m = multiscanner.load_module('test_1', [os.path.join(CWD, "modules")])
    assert isinstance(m, types.ModuleType)


def test_fail_loadModule():
    """Ensure _loadModule works"""
    m = multiscanner.load_module('notathing', [os.path.join(CWD, "modules")])
    assert m is None


class _runmod_tests(object):
    @classmethod
    def setup_class(cls):
        cls.real_mod_dir = multiscanner.MODULEDIR
        multiscanner.MODULEDIR = os.path.join(CWD, "modules")
        cls.filelist = common.parseDir(os.path.join(CWD, 'files'))
        cls.files = ['a', 'b', 'C:\\c', '/d/d']
        cls.threadDict = {}

    @classmethod
    def teardown_class(cls):
        multiscanner.MODULEDIR = cls.real_mod_dir


class Test_runModule_test_1(_runmod_tests):
    def setup(self):
        m = multiscanner.load_module('test_1', [multiscanner.MODULEDIR])
        global_module_interface = multiscanner._GlobalModuleInterface()
        self.result = multiscanner._run_module('test_1', m, self.filelist, self.threadDict, global_module_interface)
        global_module_interface._cleanup()

    def test_runModule_results(self):
        """Test module 1 results"""
        results, meta = self.result
        for fname, fresult in results:
            assert fname == fresult

        assert meta == {'Include': False, 'Type': 'Test', 'Name': 'test_1'}


class Test_runModule_test_2(_runmod_tests):
    def setup(self):
        self.m = multiscanner.load_module('test_2', [multiscanner.MODULEDIR])
        self.threadDict['test_2'] = mock.Mock()
        self.threadDict['test_1'] = mock.Mock()
        self.threadDict['test_1'].ret = ([('a', 'a'), ('C:\\c', 'c')], {})
        self.global_module_interface = multiscanner._GlobalModuleInterface()

    def teardown(self):
        self.threadDict = {}
        self.global_module_interface._cleanup()

    def test_no_requires(self):
        del self.threadDict['test_1']
        self.result = multiscanner._run_module(
            'test_2', self.m, self.filelist, self.threadDict, self.global_module_interface)
        assert self.result is None

    def test_results_1(self):
        self.result = multiscanner._run_module(
            'test_2', self.m, self.files, self.threadDict, self.global_module_interface)
        assert self.result == ([('a', True), ('b', 'b'), ('C:\\c', True), ('/d/d', '/d/d')], {'Type': 'Test', 'Name': 'test_2', 'Include': True})   # noqa: E501

    def test_replacepath_linux(self):
        self.m.DEFAULTCONF['replacement path'] = '/tmp'
        self.result = multiscanner._run_module(
            'test_2', self.m, self.files, self.threadDict, self.global_module_interface)
        assert self.result == ([('a', True), ('b', '/tmp/b'), ('C:\\c', True), ('/d/d', '/tmp/d')], {'Name': 'test_2', 'Include': True, 'Type': 'Test'})    # noqa: E501

    def test_replacepath_windows(self):
        self.m.DEFAULTCONF['replacement path'] = 'X:\\'
        self.result = multiscanner._run_module(
            'test_2', self.m, self.files, self.threadDict, self.global_module_interface)
        assert self.result == ([('a', True), ('b', 'X:\\b'), ('C:\\c', True), ('/d/d', 'X:\\d')], {'Type': 'Test', 'Name': 'test_2', 'Include': True})  # noqa: E501


class test_start_module_threads(_runmod_tests):
    def setup(self):
        self.config = {}
        self.global_module_interface = multiscanner._GlobalModuleInterface()

    def teardown(self):
        del self.config
        self.global_module_interface._cleanup()

    def test_all_started(self):
        ThreadList = multiscanner._start_module_threads(
            self.filelist, common.parseDir(os.path.join(CWD, "modules")), self.config, self.global_module_interface)
        time.sleep(.001)
        for t in ThreadList:
            assert t.started
