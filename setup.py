from setuptools import setup, find_packages

setup(
    name='xpoint',
    version='0.0.0',
    url='https://github.com/rdemaria/xpoint',
    author='Riccardo De Maria',
    author_email='riccardodemaria@gmail.com',
    description='Library for 3D geometry',
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib'],
)
