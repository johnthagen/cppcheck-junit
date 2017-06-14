from setuptools import setup


setup(
    name='cppcheck-junit',
    version='1.4.0',

    description='Converts Cppcheck XML output to JUnit format.',
    long_description=open('README.rst').read(),
    keywords='Cppcheck C++ JUnit',

    author='John Hagen',
    author_email='johnthagen@gmail.com',
    url='https://github.com/johnthagen/cppcheck-junit',
    license='MIT',

    py_modules=['cppcheck_junit'],
    install_requires=open('requirements.txt').readlines(),
    zip_safe=False,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: C++',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
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
