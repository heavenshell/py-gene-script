# -*- coding: utf-8 -*-
"""
    generate.tests
    ~~~~~~~~~~~~~~

    Tests for Flask project generator.


    :copyright: (c) 2014 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import os
import sys
import shutil
from os.path import dirname, join, exists
from datetime import datetime
from unittest import TestCase
from manage import Generator, GeneratorError
from _compat import to_unicode

if sys.version_info[0] == 2:
    from cStringIO import StringIO
else:
    from io import StringIO


class HookStdOut(object):
    def __init__(self):
        self.fp = StringIO()
        self.orig_stdout = sys.stdout
        sys.stdout = self.fp

    def dump(self):
        self.fp.seek(0)
        return self.fp.read()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        sys.stdout = self.orig_stdout


class TestsGenrator(TestCase):
    @classmethod
    def setUpClass(cls):
        current_path = dirname(os.path.abspath(__file__))
        var_path = join(current_path, 'var')

        cls.var_path = var_path
        cls.current_path = current_path

    def setUp(self):
        self.app = Generator(self.var_path)
        if os.path.exists(self.var_path):
            shutil.rmtree(self.var_path)
        os.mkdir(self.var_path)

    def test_should_raise_error_when_blank(self):
        """ Should raise error when blank given. """
        try:
            self.app.validate_name('')
            self.fail()
        except GeneratorError as e:
            self.assertTrue(e)

    def test_should_raise_error_when_start_with_numeric(self):
        """ Should raise error when start with numeric char. """
        try:
            self.app.validate_name('0foo')
            self.fail()
        except GeneratorError as e:
            self.assertTrue(e)

    def test_should_set_current_year_when_instance_created(self):
        """ Should set current year when Generator() instance created. """
        self.assertEqual(self.app.year, str(datetime.now().year))

    def test_shoud_set_author_default_env_user_name(self):
        """ Should set env USER as default author name. """
        self.assertEqual(self.app.author, os.environ['USER'])

    def test_shoud_set_author_name(self):
        """ Should set author name. """
        app = Generator(author='foo')
        self.assertEqual(app.author, 'foo')

    def test_should_set_paths(self):
        """ Should set default paths. """
        self.assertEqual(self.app.data_path,
                         join(self.current_path, 'var', 'data'))

        self.assertEqual(self.app.log_path,
                         join(self.current_path, 'var', 'logs'))

        self.assertEqual(self.app.doc_path,
                         join(self.current_path, 'var', 'docs'))

        self.assertEqual(self.app.tmpl_path,
                         join(self.current_path, 'templates'))

    def test_parse_options(self):
        """ Should parse options. """
        parsed = self.app.parse_options([
            '--project-name=testproject', '--author-name=test user'
        ])
        self.assertEqual(parsed.project_name, 'testproject')
        self.assertEqual(parsed.author_name, 'test user')

    def test_parse_short_options(self):
        """ Should parse short options. """
        parsed = self.app.parse_options([
            '-p testproject', '-u test user'
        ])
        self.assertEqual(parsed.project_name.lstrip(), 'testproject')
        self.assertEqual(parsed.author_name.lstrip(), 'test user')

    def test_build_line_separator(self):
        """ Should build Sphinx line separator. """
        self.assertEqual(self.app.build_line_separator('foo'), '~~~')
        self.assertEqual(self.app.build_line_separator('foo.bar'), '~~~~~~~')

    def test_should_build_package_path(self):
        """ Should build package path. """
        project_path = self.var_path
        ret = self.app.build_package_path('testproject', project_path,
                                          self.var_path, 'app.py_tmpl')
        self.assertEqual(ret, 'testproject.app')

        package_path = join(project_path, 'views', 'frontend')
        ret = self.app.build_package_path('testproject', package_path,
                                          self.var_path, 'index.py_tmpl')

        self.assertEqual(ret, 'testproject.views.frontend.index')

    def test_should_create_project(self):
        """ Should create testproject. """
        os.chdir(self.var_path)

        #: Delete stdout output string.
        with HookStdOut():
            self.app.create_project('testproject')

        self.assertTrue(exists(join(self.var_path, 'data')))
        self.assertTrue(exists(join(self.var_path, 'docs')))
        self.assertTrue(exists(join(self.var_path, 'LICENSE.txt')))
        self.assertTrue(exists(join(self.var_path, 'logs')))
        self.assertTrue(exists(join(self.var_path, 'manage.py')))
        self.assertTrue(exists(join(self.var_path, 'MANIFEST.in')))
        self.assertTrue(exists(join(self.var_path, 'README.rst')))
        self.assertTrue(exists(join(self.var_path, 'setup.py')))
        self.assertTrue(exists(join(self.var_path, 'testproject')))
        self.assertTrue(exists(join(self.var_path, 'var')))
        self.assertTrue(exists(join(self.var_path, 'tox.ini')))

    def test_should_create_view(self):
        """ Should create view file. """
        with HookStdOut():
            self.app.create_view('testproject', 'frontend/sample')

        expected = join(self.var_path, 'testproject', 'views', 'frontend')
        self.assertTrue(exists(join(expected, 'sample.py')))
        self.assertTrue(exists(join(expected, '__init__.py')))

    def test_should_create_restful_view(self):
        """ Should create restful view file. """
        with HookStdOut():
            self.app.create_rest('testproject', 'frontend/sample')

        expected = join(self.var_path, 'testproject',
                        'views', 'frontend')
        self.assertTrue(exists(join(expected, 'sample.py')))
        self.assertTrue(exists(join(expected, '__init__.py')))

    def test_should_create_entity(self):
        """ Should create entity file. """
        with HookStdOut():
            self.app.create_entity('testproject', 'entities/sample')

        expected = join(self.var_path, 'testproject', 'models', 'entities')
        self.assertTrue(exists(join(expected, 'sample.py')))
        self.assertTrue(exists(join(expected, '__init__.py')))

    def test_should_create_test(self):
        """ Should create test file. """
        with HookStdOut():
            self.app.create_test('testproject', 'views/sample')

        expected = join(self.var_path, 'testproject', 'tests', 'views')
        self.assertTrue(exists(join(expected, 'test_sample.py')))
        self.assertTrue(exists(join(expected, '__init__.py')))

    def test_should_create_sphinx_header(self):
        """ Should create Sphinx header. """
        os.chdir(self.var_path)
        with HookStdOut():
            self.app.create_project('testproject')

        view_path = join(self.var_path, 'testproject',
                         'views', 'frontend', 'index.py')

        with open(view_path, 'rb') as f:
            lines = f.readlines()
            self.assertEqual(to_unicode(lines[2].lstrip().rstrip()),
                             'testproject.views.frontend.index')
            self.assertEqual(to_unicode(lines[3].lstrip().rstrip()),
                             '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


if __name__ == '__main__':
    import unittest
    unittest.main()
