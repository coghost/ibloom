from setuptools import setup
ext_files = ['ibloom/bloom.c']
kwargs = {}

from Cython.Distutils import build_ext
from Cython.Distutils import Extension
ext_files.append('ibloom/ibloom.pyx')
kwargs['cmdclass'] = {'build_ext': build_ext}

ext_modules = [
    Extension(
        "ibloom",
        ext_files,
        libraries=['hiredis'],
        library_dirs=['/usr/local/lib'],
        include_dirs=['/usr/local/include']
    )]

setup(
    name='ibloom',
    version='0.0.1',
    url='https://github.com/coghost/ibloom',
    license='MIT',
    author='Hex.Li',
    author_email='imanux@sina.com',
    keywords='cython bloom filter redis',
    description='Python library which implements a Redis-backed Bloom filter.',
    ext_modules=ext_modules,
    install_requires=['cython'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Programming Language :: C',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    **kwargs
)
