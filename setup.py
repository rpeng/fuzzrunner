from setuptools import setup

setup(
    name='fuzzrunner',
    version='1.0',
    packages=['fuzzrunner'],
    install_requires=['fuzzywuzzy', 'pyyaml', 'path.py', 'python-Levenshtein', 'ngram'],
    url='',
    license='GPLv3',
    author='rpeng',
    scripts=['bin/fuzzrunner'],
    author_email='',
    description='A fuzzywuzzy shell script launcher'
)
