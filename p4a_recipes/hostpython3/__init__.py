import sh
import os

from multiprocessing import cpu_count
from pathlib import Path
from os.path import join

from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import (
    BuildInterruptingException,
    current_directory,
    ensure_dir,
)

try:
    from pythonforandroid.prerequisites import OpenSSLPrerequisite
    _has_openssl_prereq = True
except ImportError:
    _has_openssl_prereq = False

HOSTPYTHON_VERSION_UNSET_MESSAGE = (
    'The hostpython recipe must have set version'
)

SETUP_DIST_NOT_FIND_MESSAGE = (
    'Could not find Setup.dist or Setup in Python build'
)


class HostPython3Recipe(Recipe):
    version = '3.11.9'
    name = 'hostpython3'

    build_subdir = 'native-build'

    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'

    patches = []

    @property
    def _exe_name(self):
        if not self.version:
            raise BuildInterruptingException(HOSTPYTHON_VERSION_UNSET_MESSAGE)
        return f'python{self.version.split(".")[0]}'

    @property
    def python_exe(self):
        return join(self.get_path_to_python(), self._exe_name)

    @property
    def local_bin(self):
        return join(self.get_path_to_python(), 'bin')

    @property
    def site_bin(self):
        return join(
            self.get_path_to_python(),
            f'lib/python{self.version[:4]}/site-packages/bin'
        )

    def get_recipe_env(self, arch=None):
        env = os.environ.copy()
        if _has_openssl_prereq:
            try:
                openssl_prereq = OpenSSLPrerequisite()
                pkg = openssl_prereq.pkg_config_location
                if env.get("PKG_CONFIG_PATH", ""):
                    env["PKG_CONFIG_PATH"] = os.pathsep.join(
                        [pkg, env["PKG_CONFIG_PATH"]]
                    )
                else:
                    env["PKG_CONFIG_PATH"] = pkg
            except Exception:
                pass
        return env

    def should_build(self, arch):
        if Path(self.python_exe).exists():
            self.ctx.hostpython = self.python_exe
            return False
        return True

    def get_build_container_dir(self, arch=None):
        choices = self.check_recipe_choices()
        dir_name = '-'.join([self.name] + choices)
        return join(self.ctx.build_dir, 'other_builds', dir_name, 'desktop')

    def get_build_dir(self, arch=None):
        return join(self.get_build_container_dir(), self.name)

    def get_path_to_python(self):
        return join(self.get_build_dir(), self.build_subdir)

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        recipe_build_dir = self.get_build_dir(arch.arch)
        build_dir = join(recipe_build_dir, self.build_subdir)
        ensure_dir(build_dir)

        with current_directory(build_dir):
            if not Path('config.status').exists():
                shprint(sh.Command(join(recipe_build_dir, 'configure')), _env=env)

        with current_directory(recipe_build_dir):
            setup_dist_location = join('Modules', 'Setup.dist')
            if Path(setup_dist_location).exists():
                shprint(sh.cp, setup_dist_location,
                        join(build_dir, 'Modules', 'Setup'))
            else:
                setup_location = join('Modules', 'Setup')
                if not Path(setup_location).exists():
                    raise BuildInterruptingException(SETUP_DIST_NOT_FIND_MESSAGE)

            shprint(sh.make, '-j', str(cpu_count()), '-C', build_dir, _env=env)

            for exe_name in ['python.exe', 'python']:
                exe = join(self.get_path_to_python(), exe_name)
                if Path(exe).is_file():
                    shprint(sh.cp, exe, self.python_exe)
                    break

        self.ctx.hostpython = self.python_exe


recipe = HostPython3Recipe()
