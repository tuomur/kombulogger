from setuptools import setup, find_packages

requires = (
    'kombu',
)

setup(
    name='kombulogger',
    version='0.1',
    packages=find_packages(),
    url='',
    install_requires=requires,
    license='MIT',
    author='Tuomas Mursu',
    author_email='tuomas.mursu@kapsi.fi',
    description=''
)
