import glob
import sh
import subprocess
import shutil

from multiprocessing import cpu_count
from os import environ, utime
from os.path import dirname, exists, join
from pathlib import Path

from pythonforandroid.logger import info, warning, shprint
from pythonforandroid.patching import version_starts_with
from pythonforandroid.recipe import Recipe, TargetPythonRecipe
from pythonforandroid.util import (
    current_directory,
    ensure_dir,
    walk_valid_filens,
    BuildInterruptingException,
)

NDK_API_LOWER_THAN_SUPPORTED_MESSAGE = (
    'Target ndk-api is {ndk_api}, '
    'but the python3 recipe supports only {min_ndk_api}+'
)


class Python3Recipe(TargetPythonRecipe):
    version = '3.11.9'
    url = 'https://www.python.org/ftp/python/{version}/Python-{version}.tgz'
    name = 'python3'

    patches = [
        'patches/pyconfig_detection.patch',
        'patches/reproducible-buildinfo.diff',
        ('patches/py3.8.1.patch', version_starts_with("3.8")),
        ('patches/py3.8.1.patch', version_starts_with("3.9")),
        ('patches/py3.8.1.patch', version_starts_with("3.10")),
        ('patches/py3.8.1.patch', version_starts_with("3.11")),
    ]

    if shutil.which('lld') is not None:
        patches = patches + [
            ("patches/py3.8.1_fix_cortex_a8.patch", version_starts_with("3.8")),
            ("patches/py3.8.1_fix_cortex_a8.patch", version_starts_with("3.9")),
            ("patches/py3.8.1_fix_cortex_a8.patch", version_starts_with("3.10")),
            ("patches/py3.8.1_fix_cortex_a8.patch", version_starts_with("3.11")),
        ]

    depends = ['hostpython3', 'sqlite3', 'openssl', 'libffi']
    opt_depends = ['libbz2', 'liblzma']

    configure_args = (
        '--host={android_host}',
        '--build={android_build}',
        '--enable-shared',
        '--enable-ipv6',
        'ac_cv_file__dev_ptmx=yes',
        'ac_cv_file__dev_ptc=no',
        '--without-ensurepip',
        'ac_cv_little_endian_double=yes',
        'ac_cv_header_sys_eventfd_h=no',
        '--prefix={prefix}',
        '--exec-prefix={exec_prefix}',
        '--enable-loadable-sqlite-extensions',
        '--without-static-libpython',
    )

    MIN_NDK_API = 21

    stdlib_dir_blacklist = {
        '__pycache__', 'test', 'tests', 'lib2to3',
        'ensurepip', 'idlelib', 'tkinter',
    }
    stdlib_filen_blacklist = ['*.py', '*.exe', '*.whl']
    site_packages_dir_blacklist = {'__pycache__', 'tests'}
    site_packages_filen_blacklist = ['*.py']
    compiled_extension = '.pyc'

    def __init__(self, *args, **kwargs):
        self._ctx = None
        super().__init__(*args, **kwargs)

    @property
    def _libpython(self):
        return 'libpython{link_version}.so'.format(
            link_version=self.link_version
        )

    @property
    def link_version(self):
        major, minor = self.major_minor_version_string.split('.')
        flags = ''
        if major == '3' and int(minor) < 8:
            flags += 'm'
        return '{major}.{minor}{flags}'.format(
            major=major, minor=minor, flags=flags
        )

    def include_root(self, arch_name):
        return join(self.get_build_dir(arch_name), 'Include')

    def link_root(self, arch_name):
        return join(self.get_build_dir(arch_name), 'android-build')

    def should_build(self, arch):
        return not Path(self.link_root(arch.arch), self._libpython).is_file()

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        self.ctx.python_recipe = self

    def get_recipe_env(self, arch=None, with_flags_in_cc=True):
        env = super().get_recipe_env(arch)
        env['HOSTARCH'] = arch.command_prefix
        env['CC'] = arch.get_clang_exe(with_target=True)
        env['PATH'] = (
            '{hostpython_dir}:{old_path}').format(
                hostpython_dir=self.get_recipe(
                    'host' + self.name, self.ctx).get_path_to_python(),
                old_path=env['PATH'])
        env['CFLAGS'] = ' '.join(['-fPIC', '-DANDROID'])
        env['LDFLAGS'] = env.get('LDFLAGS', '')
        if shutil.which('lld') is not None:
            env['LDFLAGS'] += ' -L. -fuse-ld=lld'
        else:
            warning('lld not found, linking without it.')
        return env

    def set_libs_flags(self, env, arch):
        def add_flags(include_flags, link_dirs, link_libs):
            env['CPPFLAGS'] = env.get('CPPFLAGS', '') + include_flags
            env['LDFLAGS'] = env.get('LDFLAGS', '') + link_dirs
            env['LIBS'] = env.get('LIBS', '') + link_libs

        if 'sqlite3' in self.ctx.recipe_build_order:
            info('Activating flags for sqlite3')
            recipe = Recipe.get_recipe('sqlite3', self.ctx)
            add_flags(' -I' + recipe.get_build_dir(arch.arch),
                      ' -L' + recipe.get_lib_dir(arch), ' -lsqlite3')

        if 'libffi' in self.ctx.recipe_build_order:
            info('Activating flags for libffi')
            recipe = Recipe.get_recipe('libffi', self.ctx)
            env['PKG_CONFIG_PATH'] = recipe.get_build_dir(arch.arch)
            add_flags(' -I' + ' -I'.join(recipe.get_include_dirs(arch)),
                      ' -L' + join(recipe.get_build_dir(arch.arch), '.libs'),
                      ' -lffi')

        if 'openssl' in self.ctx.recipe_build_order:
            info('Activating flags for openssl')
            recipe = Recipe.get_recipe('openssl', self.ctx)
            self.configure_args += \
                ('--with-openssl=' + recipe.get_build_dir(arch.arch),)
            add_flags(recipe.include_flags(arch),
                      recipe.link_dirs_flags(arch), recipe.link_libs_flags())

        for library_name in {'libbz2', 'liblzma'}:
            if library_name in self.ctx.recipe_build_order:
                info(f'Activating flags for {library_name}')
                recipe = Recipe.get_recipe(library_name, self.ctx)
                add_flags(recipe.get_library_includes(arch),
                          recipe.get_library_ldflags(arch),
                          recipe.get_library_libs_flag())

        info("Activating flags for android's zlib")
        zlib_lib_path = arch.ndk_lib_dir_versioned
        zlib_includes = self.ctx.ndk.sysroot_include_dir
        zlib_h = join(zlib_includes, 'zlib.h')
        try:
            with open(zlib_h) as fileh:
                zlib_data = fileh.read()
        except IOError:
            raise BuildInterruptingException(
                "Could not determine android's zlib version, no zlib.h ({}) in"
                " the NDK dir includes".format(zlib_h)
            )
        for line in zlib_data.split('\n'):
            if line.startswith('#define ZLIB_VERSION '):
                break
        else:
            raise BuildInterruptingException(
                'Could not parse zlib.h to find zlib version'
            )
        env['ZLIB_VERSION'] = line.replace('#define ZLIB_VERSION ', '')
        add_flags(' -I' + zlib_includes, ' -L' + zlib_lib_path, ' -lz')
        return env

    def build_arch(self, arch):
        if self.ctx.ndk_api < self.MIN_NDK_API:
            raise BuildInterruptingException(
                NDK_API_LOWER_THAN_SUPPORTED_MESSAGE.format(
                    ndk_api=self.ctx.ndk_api, min_ndk_api=self.MIN_NDK_API
                ),
            )

        recipe_build_dir = self.get_build_dir(arch.arch)
        build_dir = join(recipe_build_dir, 'android-build')
        ensure_dir(build_dir)

        sys_prefix = '/usr/local'
        sys_exec_prefix = '/usr/local'

        env = self.get_recipe_env(arch)
        env = self.set_libs_flags(env, arch)

        android_build = sh.Command(
            join(recipe_build_dir, 'config.guess'))().stdout.strip().decode('utf-8')

        with current_directory(build_dir):
            if not exists('config.status'):
                shprint(
                    sh.Command(join(recipe_build_dir, 'configure')),
                    *(' '.join(self.configure_args).format(
                        android_host=env['HOSTARCH'],
                        android_build=android_build,
                        prefix=sys_prefix,
                        exec_prefix=sys_exec_prefix)).split(' '),
                    _env=env)

            shprint(
                sh.make, 'all', '-j', str(cpu_count()),
                'INSTSONAME={lib_name}'.format(lib_name=self._libpython),
                _env=env
            )
            sh.cp('pyconfig.h', join(recipe_build_dir, 'Include'))

    def compile_python_files(self, dir):
        args = [self.ctx.hostpython]
        args += ['-OO', '-m', 'compileall', '-b', '-f', dir]
        subprocess.call(args)

    def create_python_bundle(self, dirn, arch):
        modules_build_dir = join(
            self.get_build_dir(arch.arch),
            'android-build', 'build',
            'lib.linux{}-{}-{}'.format(
                '2' if self.version[0] == '2' else '',
                arch.command_prefix.split('-')[0],
                self.major_minor_version_string
            ))

        self.compile_python_files(modules_build_dir)
        self.compile_python_files(join(self.get_build_dir(arch.arch), 'Lib'))
        self.compile_python_files(self.ctx.get_python_install_dir(arch.arch))

        modules_dir = join(dirn, 'modules')
        c_ext = self.compiled_extension
        ensure_dir(modules_dir)
        module_filens = (glob.glob(join(modules_build_dir, '*.so')) +
                         glob.glob(join(modules_build_dir, '*' + c_ext)))
        info("Copy {} files into the bundle".format(len(module_filens)))
        for filen in module_filens:
            shutil.copy2(filen, modules_dir)

        stdlib_zip = join(dirn, 'stdlib.zip')
        with current_directory(join(self.get_build_dir(arch.arch), 'Lib')):
            stdlib_filens = list(walk_valid_filens(
                '.', self.stdlib_dir_blacklist, self.stdlib_filen_blacklist))
            if 'SOURCE_DATE_EPOCH' in environ:
                stdlib_filens.sort()
                timestamp = int(environ['SOURCE_DATE_EPOCH'])
                for filen in stdlib_filens:
                    utime(filen, (timestamp, timestamp))
            shprint(sh.zip, '-X', stdlib_zip, *stdlib_filens)

        ensure_dir(join(dirn, 'site-packages'))
        ensure_dir(self.ctx.get_python_install_dir(arch.arch))
        with current_directory(self.ctx.get_python_install_dir(arch.arch)):
            filens = list(walk_valid_filens(
                '.', self.site_packages_dir_blacklist,
                self.site_packages_filen_blacklist))
            for filen in filens:
                ensure_dir(join(dirn, 'site-packages', dirname(filen)))
                shutil.copy2(filen, join(dirn, 'site-packages', filen))

        python_build_dir = join(self.get_build_dir(arch.arch), 'android-build')
        python_lib_name = 'libpython' + self.link_version
        shprint(
            sh.cp,
            join(python_build_dir, python_lib_name + '.so'),
            join(self.ctx.bootstrap.dist_dir, 'libs', arch.arch)
        )

        info('Renaming .so files to reflect cross-compile')
        self.reduce_object_file_names(join(dirn, 'site-packages'))
        return join(dirn, 'site-packages')


recipe = Python3Recipe()
