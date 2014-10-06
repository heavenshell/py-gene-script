#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    gene.script.manage
    ~~~~~~~~~~~~~~~~~~

    Generat Flask project/file.

    A lot of generator did not generate Sphinx header.
    But I want to generate Sphinx header.
    That's why I reinventing the wheel.

    :copyright: (c) 2014 Shinya Ohyanagi, All rights reserved.
    :license: BSD, see LICENSE for more details.
"""
import os
import sys
import re
import shutil
from datetime import datetime
from argparse import ArgumentParser
from _compat import iteritems


__version__ = '0.3'


def red(msg):
    """
    Output red color.

    :param msg:
    """
    return '\033[31m{0}\033[0m'.format(msg)


def green(msg):
    """
    Output green color.

    :param msg: Message
    """
    return '\033[32m{0}\033[0m'.format(msg)


def grey(msg):
    """
    Output grey color.

    :param msg: Message
    """
    return '\033[37m{0}\033[0m'.format(msg)


def output(msg):
    """
    Write message to stdout.

    :param msg: Message
    """
    sys.stdout.write('{0}\n'.format(msg))


class GeneratorError(Exception):
    pass


class Generator(object):
    def __init__(self, file_path=None, author=None):
        """
        Initialize.
          - Set templates path
          - Set year
          - Set default author name

        :param file_path:
        :param author:
        """
        dirname = os.path.dirname
        current_path = dirname(os.path.abspath(__file__))
        if file_path is None:
            file_path = dirname(current_path)

        join = os.path.join

        self.file_path = file_path
        self.data_path = join(file_path, 'data')
        self.log_path = join(file_path, 'logs')
        self.doc_path = join(file_path, 'docs')
        self.tmpl_path = join(current_path, 'templates')

        now = datetime.now()
        self.year = str(now.year)
        if author is None:
            #: If author did'nt set, use `env` user name.
            author = os.environ['USER']

        self.author = author

    def parse_options(self, cmdline=None):
        """ Parse options. """
        parser = ArgumentParser(description='Flask builder', add_help=True)
        parser.add_argument('-p', '--project-name', help='Create project')
        parser.add_argument('-u', '--author-name', help='Author name')
        parser.add_argument('--version', action='version',
                            version='%(prog)s 1.0')

        if cmdline is None:
            return parser.parse_args()

        return parser.parse_args(cmdline)

    def build_line_separator(self, package):
        """
        Build Sphinx line separator.

        :param package: Package path.
        """
        separator = '~' * len(package)

        return separator

    def render_template(self, file_path, **kwargs):
        """
        Render template.

        :param file_path: Path to template file.
        :param **kwargs: Template vars
        """
        tmpl = None
        if file_path.endswith('_tmpl'):
            _path = file_path.replace('_tmpl', '')
            os.rename(file_path, _path)
            file_path = _path

        #: Template variable {{foo}}
        with open(file_path, 'r') as f:
            tmpl = f.read()
            for k, v in iteritems(kwargs):
                #: Equivalent to `{{%s}} % k`.
                #: Should use String.template?
                var = '{{{}}}'.format(k)
                tmpl = tmpl.replace('{{{0}}}'.format(var), v)

        if tmpl is None:
            return

        with open(file_path, 'w') as f:
            f.write(tmpl)

    def validate_name(self, name):
        """
        Validate name.

        Name should be Start with alphabet.
        Can use `A-z`, `0-9`, `-`, `_`.

        :param name: File name
        """
        if not re.search(r'^[a-zA-Z][a-zA-Z0-9_\/\-]*$', name):
            if not re.search(r'^[a-zA-Z]', name):
                msg = 'make sure the name begins with a letter'
            else:
                msg = 'use only numbers, letters and dashes'

            msg = '{0} is not a valid file name. Please {1}.'.format(name, msg)
            error = red(msg)

            raise GeneratorError(error)

    def validate_exists(self, path, file_name):
        """
        Check is file/directory exists.

        :param path:
        :param file_name:
        """
        if os.path.exists(os.path.join(path, file_name)):
            error = red('{0} already exists in {1}'.format(file_name, path))
            raise GeneratorError(error)

    def build_package_path(self, project_name, root, project_path, file_name):
        """
        Build package path.

        foo
          foo.app
          foo.configs
          foo.tests

        :param project_name: Project name
        :param root: File path
        :param project_path: Project path
        :param file_name: Generat file name
        """
        tmpl = '{0}.{1}'.format(project_name, root[len(project_path):])
        tmpl = tmpl.rstrip('.') if tmpl.endswith('.') else tmpl
        tmpl = '{0}.{1}'.format(tmpl, file_name)
        tmpl = tmpl.replace('/', '.').replace('..', '.')
        tmpl = tmpl.replace('.py_tmpl', '').replace('.__init__', '')

        return tmpl

    def recrsive(self, project_name, project_path, project_root=None):
        """
        Recrsive files.

        :param project_name:
        :param project_path:
        :param project_root:
        """
        if project_root is None:
            project_root = os.path.dirname(project_path)

        for root, dirs, files in os.walk(project_path):
            for fname in files:
                if fname.endswith('_tmpl'):
                    package = self.build_package_path(project_name, root,
                                                      project_path, fname)
                    separator = self.build_line_separator(package)

                    template_var = {
                        'package': package,
                        'separator': separator,
                        'project_root': project_root,
                        'project': project_name,
                        'project_upper': project_name.upper(),
                        'year': self.year,
                        'author': self.author
                    }
                    self.render_template(os.path.join(root, fname),
                                         **template_var)

    def create_project(self, project_name):
        """
        Create project.

        :param project_name: Project name
        """
        self.validate_name(project_name)
        self.validate_exists(self.file_path, project_name)

        #: Copy project templates.
        create_message = 'Creating {0} to {1}'
        output(green(create_message.format(project_name, self.file_path)))
        shutil.copytree(os.path.join(self.tmpl_path, 'app'), project_name)
        project_path = os.path.join(self.file_path, project_name)

        self.recrsive(project_name, project_path)

        default_files = [
            'manage.py_tmpl', 'LICENSE.txt_tmpl', 'MANIFEST.in_tmpl',
            'README.rst_tmpl', 'setup.py_tmpl', 'tox.ini_tmpl'
        ]
        for fname in default_files:
            src = os.path.join(self.tmpl_path, fname)
            dst = os.path.join(self.file_path, fname)
            package = fname.replace('_tmpl', '')

            output(green(create_message.format(package, self.file_path)))
            shutil.copy(src, dst)
            separator = self.build_line_separator(project_name)
            template_var = {
                'package': package,
                'separator': separator,
                'project': project_name,
                'project_upper': project_name.upper(),
                'year': self.year,
                'author': self.author
            }
            self.render_template(dst, **template_var)

        # Create docs, logs directoire.
        dirs = ['docs', 'logs', 'var/run']
        for d in dirs:
            path = os.path.join(self.file_path, d)
            if self.validate_exists(self.file_path, d):
                continue

            output(green(create_message.format(d, self.file_path)))
            os.makedirs(path)

        # Copy data directory.
        if self.validate_exists(self.file_path, 'data'):
            return

        output(green(create_message.format('data', self.file_path)))

        dst = os.path.join(self.file_path, 'data')
        shutil.copytree(os.path.join(self.tmpl_path, 'data'), dst)
        self.recrsive(project_name, dst)

        output(green('Create project success.'))
        msg = 'Type pip install -r data/requirement.txt to install packages.'
        output(grey(msg))

    def create_file(self, project_name, file_name, category, src=None):
        """
        Create file.

        :param project_name:
        :param file_name:
        :param category:
        """
        self.validate_name(file_name)
        file_path = os.path.join(self.file_path, project_name, category)
        self.validate_exists(file_path, file_name + '.py')
        items = file_name.split('/')
        class_name = items[-1]
        if category == 'tests':
            items[-1] = 'test_{0}'.format(items[-1])
            file_name = '/'.join(items)

        file_path = os.path.join(file_path, file_name + '.py')

        directory_name = ''
        if len(items) > 1:
            directory_name = '/'.join(items[:-1])
            directory = os.path.join(self.file_path, project_name,
                                     category, directory_name)

            if not os.path.exists(directory):
                os.makedirs(directory)
                tmpl_init = os.path.join(self.tmpl_path, '__init__.py')

                for root, dirs, files in os.walk(directory):
                    shutil.copy(tmpl_init, os.path.join(root, '__init__.py'))

        output(green('Creating {0}'.format(file_path)))
        package = '{0}/{1}/{2}'.format(project_name, category, directory_name)
        package = package.replace('/', '.')

        if src is None:
            src = os.path.join(self.tmpl_path, category + '.py_tmpl')

        shutil.copy(src, file_path)
        separator = self.build_line_separator(package + '.' + items[-1])
        template_var = {
            'package': package,
            'name': items[-1],
            'klass': class_name.title(),
            'separator': separator,
            'project': project_name,
            'year': self.year,
            'dir': directory_name,
            'author': self.author,
            'module': directory_name.replace('/', '.')
        }
        self.render_template(file_path, **template_var)

    def create_view(self, project_name, file_name):
        """
        Create view file.

        :param project_name:
        :param file_name:
        """
        self.create_file(project_name, file_name, category='views')

        routing = '{0}.views.{1}'.format(project_name, file_name)
        routing = routing.replace('/', '.')
        output(green('-' * 80))
        output(green('Add routing `{0}` to views/__init__.py'.format(routing)))
        output(green('-' * 80))

    def create_rest(self, project_name, file_name):
        """
        Create RESTful view.

        GET    /     index()
        GET    /<id> show(id)
        POST   /     create()
        PUT    /<id> update(id)
        DELETE /<id> delete(id)

        :param project_name:
        :param file_name:
        """
        src = os.path.join(self.tmpl_path, 'rest.py_tmpl')
        self.create_file(project_name, file_name, category='views', src=src)

        routing = '{0}.views.{1}'.format(project_name, file_name)
        routing = routing.replace('/', '.')
        output(green('-' * 80))
        output(green('Add routing `{0}` to views/__init__.py'.format(routing)))
        output(green('-' * 80))

    def create_entity(self, project_name, file_name):
        """
        Create model file.

        :param project_name:
        :param file_name:
        """
        src = os.path.join(self.tmpl_path, 'models_entity.py_tmpl')
        self.create_file(project_name, file_name, category='models', src=src)

    def create_test(self, project_name, file_name):
        """
        Create test file.

        :param project_name:
        :param file_name:
        """
        self.create_file(project_name, file_name, category='tests')

    def output_error(self, msg):
        """
        Output error message.

        :param msg: Error message
        """
        output(red(msg))

    def run(self):
        """ Run. """
        parser = self.parse_options()
        if parser.author_name is not None:
            self.author = parser.author_name

        if parser.project_name is None:
            return

        project_name = parser.project_name
        try:
            self.create_project(project_name)
        except Exception as e:
            output(e.message)


if __name__ == '__main__':
    Generator().run()
