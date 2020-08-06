from setuptools import setup, find_packages


PACKAGE_NAME = 'aicssegmentation'


"""
Notes:
We get the constants MODULE_VERSION from
See (3) in following link to read about versions from a single source
https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
"""

MODULE_VERSION = ""
exec(open(PACKAGE_NAME + "/version.py").read())


def readme():
    with open('README.md',encoding='utf-8') as f:
        return f.read()


test_deps = ['pytest', 'pytest-cov']
lint_deps = ['flake8']
interactive_dev_deps = [
    'matplotlib',
    'jupyter',
    'itkwidgets',
    'ipython',
    'ipywidgets'
]
# may need itkwidgets==0.12.2. if viewer keeps crashing

all_deps = [*test_deps, *lint_deps, *interactive_dev_deps]
extras = {
    'test_group': test_deps,
    'lint_group': lint_deps,
    'interactive_dev_group': interactive_dev_deps,
    'all': all_deps
}

setup(name=PACKAGE_NAME,
      version=MODULE_VERSION,
      description='Scripts for structure segmentation.',
      long_description=readme(),
      author='AICS',
      author_email='jianxuc@alleninstitute.org',
      license='Allen Institute Software License',
      packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
      entry_points={
          "console_scripts": [
              "batch_processing={}.bin.batch_processing:main".format(PACKAGE_NAME)
          ]
      },
      install_requires=[
          'numpy>=1.15.1',
          'scipy>=1.1.0',
          'scikit-image==0.15.0',
          'pandas>=0.23.4',
          'aicsimageio>=3.0.0',
          'aicsimageprocessing==0.7.1',
          'numba>=0.40.0',
          'itk'
      ],

      # For test setup. This will allow JUnit XML output for Jenkins
      setup_requires=['pytest-runner'],
      tests_require=test_deps,

      extras_require=extras,
      zip_safe=False
      )
