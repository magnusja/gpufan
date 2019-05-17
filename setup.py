from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nvfan',
    version='0.3.0',
    url='https://github.com/magnusja/nvfan',
    description='Control Nvidia GPU fan in your python script.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Magnus Jahnen',
    author_email='magnus@jahnen.me',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3',
    keywords='machinelearning ai pytorch tensorflow torch nvidia gpu fan',
    packages=find_packages(exclude=['docs', 'tests']),
    setup_require=['pytest-runner'],
    tests_require=['pytest', 'sure'],
    scripts=['bin/nvfan'],
    project_urls={
        'Bug Reports': 'https://github.com/magnusja/nvfan/issues',
        'Home Page': 'https://github.com/magnusja/nvfan'
    }
)
