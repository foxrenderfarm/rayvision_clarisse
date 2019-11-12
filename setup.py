"""Describe our module distribution to Distutils."""

# Import third-party modules
from setuptools import find_packages
from setuptools import setup


def parse_requirements(filename):
    with open(filename, 'r') as f:
        for line in f:
            yield line.strip()


setup(
    name='rayvision_clarisse',
    author='RayVision',
    author_email='developer@rayvision.com',
    url='',
    package_dir={'': '.'},
    packages=find_packages('.'),
    description='',
    entry_points={},
    install_requires=[
        "rayvision_log",
        "rayvision_utils",
    ],
    package_data={
        'rayvision_clarisse': ["./tool/*"],
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    use_scm_version=True,
    setup_requires=['setuptools_scm'],

)
