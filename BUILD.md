# Build Steps

The build process is setup so that you can develop in a pure python manner. 

We additionally support a gradle setup that wraps these steps in gradle tasks, and additionally provides tooling to setup the build environment. The version updates are handled primarily in our CI builds.

- [Python Builds](#python_builds)
- [Gradle Builds](#gradle_builds)

## Python Builds<a name="python_builds"></a>

### Environment setup 

Create your virtual environment. Before any of the subsequent tasks ensure it is activated.
```bash
export venvdir=~/venvs/buildproject
virtualenv -p python3 ${venvdir}
source ${venvdir}/bin/activate
```

Now install the developer requiremnts
```bash
# Install modules for development
pip install -e .[test_group] -e .[lint_group]
```

If you plan to locally test with jupyter notebooks, you can add the `jupyter_group`.
Replace the above `pip` call with the following.

```bash
# Install modules for development, and manual testing in a jupyter environment
pip install -e .[test_group] -e .[lint_group] -e .[jupyter_group]
```

## Gradle Builds<a name="gradle_builds"></a>

### Environment setup 

First ensure you have a clean setup. This will remove all generated files and folders as well as the virtual environment.

```bash
./gradlew cleanAll 
```

To setup your environment you need to run only one of the following tasks. Note that calling that calling 
the `build` task, discussed later, will automatically call one of these tasks.

```bash
# Option 1
# Install what is requirement by the module itself, and the development dependencies, i.e. testing and linting. 
./gradlew installDependencies
# or in short    $> ./gradlew iD

# Option 2
# Install everything from option 1, as well as a jupyter notebook tooling.
./gradlew installJupyterDependencies
# or in short    $> ./gradlew iJD

# Option 3
# Install everything from option 1, as well as tools for version management and uploads to python artifact repos.
./gradlew installCIDependencies
# or in short    $> ./gradlew iCID
```