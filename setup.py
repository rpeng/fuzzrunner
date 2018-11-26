from setuptools import setup, find_packages

setup(
    name='fuzzrunner',
    version='1.0',
    packages=['fuzzrunner'],
    install_requires=['fuzzywuzzy', 'pyyaml'],
    url='',
    license='GPLv3',
    author='rpeng',
    scripts=['bin/fuzzrunner'],
    author_email='',
    description='A fuzzywuzzy shell script launcher'
)
