from setuptools import setup, find_packages
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
    version='0.0.2.1',
    packages=find_packages(),
    ext_modules=ext_modules,
    install_requires=['Cython'],
    url='https://github.com/coghost/ibloom',
    license='MIT',
    author='Hex.Li',
    author_email='imanux@sina.com',
    keywords='Cython bloom filter redis',
    description='Python library which implements a Redis-backed Bloom filter.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
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
