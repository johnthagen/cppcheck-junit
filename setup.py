from setuptools import setup

import cppcheck_junit


setup(
    name='cppcheck-junit',
    version=cppcheck_junit.__version__,

    description='Converts Cppcheck XML output to JUnit format.',
    long_description=open('README.rst').read(),
    keywords='Cppcheck C++ JUnit',

    author='John Hagen',
    author_email='johnthagen@gmail.com',
    url='https://github.com/johnthagen/cppcheck-junit',
    license='MIT',

    py_modules=['cppcheck_junit'],
    zip_safe=False,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],

    scripts=['cppcheck_junit.py'],

    entry_points={
        'console_scripts': [
            'cppcheck_junit = cppcheck_junit:main',
        ],
    }
)
