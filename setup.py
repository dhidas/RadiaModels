from setuptools import setup

setup(
    name = 'radiamodels',
    version = '0.4',
    packages = ['radiamodels'],
    package_dir={'radiamodels': 'radiamodels'},
    package_data = {'radiamodels': ['data/*.dat', 'data/*.txt']},
)
