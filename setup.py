from setuptools import setup

setup(
    name = 'radiamodels',
    version = '0.1',
    packages = ['radiamodels'],
    package_data = {'radiamodels': ['data/*.dat', 'data/*.txt']},
    data_files=[('radiamodels/data', ['data/PermendurNEOMAX.txt',])],
)
