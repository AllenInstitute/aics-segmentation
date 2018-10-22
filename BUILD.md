# Build Steps

The build process is setup so that you can develop in a pure python manner or use the gradle build setup, which calls the python setup. We use the gradle setup in conjunction with our CI process and Jenkins since it encapsulates the build tool chain.

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

If you plan to locally test with jupyter notebooks, you can add the `interactive_dev_group`.
Replace the above `pip` call with the following.

```bash
# Install modules for development, and manual(interactive) testing in a jupyter environment
pip install -e .[test_group] -e .[lint_group] -e .[interactive_dev_group]
```

## Gradle Builds<a name="gradle_builds"></a>

### Environment setup 

First ensure you have a clean setup. This will remove all generated files and folders as well as the virtual environment.

```bash
# Use this to completely reset your environment. This will need to be followed by one of the installXXXDependencies tasks.
./gradlew cleanAll 
```

To setup your environment you need to run only one of the following tasks. Note that calling that calling 
the `build` task, discussed later, will automatically call one of these tasks.

```bash
# Option 1
# Install what is requirement by the module itself, and the development dependencies, i.e. testing and linting. 
./gradlew installDependencies
# Initial-based short form: 
# $>   ./gradlew iD

# Option 2
# Install everything from option 1, as well as a jupyter notebook tooling.
./gradlew installInteractiveDevDependencies
# Initial-based short form: 
# $>   ./gradlew iIDD

# Option 3
# Install everything from option 1, as well as tools for version management and uploads to python artifact repos.
./gradlew installCIDependencies
# Initial-based short form: 
# $>   ./gradlew iCID
```

# Version Management

The version management happens in the continuous integration process. This relies on using semantic versioning 
combined with specifications in PEP-440.

The development version is of the form `<major>.<minor>.<patch>.dev<devbuild>`, where each component is an integer. When changes are merged into the master branch, the CI process will increment the `<devbuild>`. 

For a release, the CI process will drop the last component, creating version `<major>.<minor>.<patch>`. Upon publishing and tagging, it will increment the `<patch>` number. 

If your next release requires an increase in the `<major>` or `<minor>` versions, You can use the gradle tasks to increment the
version using the `bumpVersionPostRelease` task with an additional parameter
```bash
# To increment the major part
./gradlew bumpVersionPostRelease -PbumpPartOverride=major

# To increment the minor part
./gradlew bumpVersionPostRelease -PbumpPartOverride=minor
```

Note that the gradlew tasks calls the Python `bumpversion` module as part of the task, but it also provides a number of checks to avoid complications from certain `bumpversion` behavior.



