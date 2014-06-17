from setuptools import setup, find_packages
import re


module_file = open("pecan_notario/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))

setup(
    name='pecan-notario',
    version=metadata['version'],
    description="""
    """,
    long_description=None,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python'
    ],
    keywords='pecan validation decorator',
    url='https://github.com/alfredodeza/pecan-notario',
    author='Alfredo Deza',
    author_email='contact at deza.pe',
    license='MIT',
    install_requires=['pecan', 'notario'],
    tests_require=['WebTest >= 1.3.1'],  # py3 compat
    zip_safe=False,
    packages=find_packages(exclude=['ez_setup']),
    entry_points="""
    [pecan.extension]
    notario = pecan_notario
    """
)
