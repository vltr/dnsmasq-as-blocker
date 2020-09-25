import codecs
import os
import re

from distutils import log
from distutils.cmd import Command
from distutils.dist import Distribution
from setuptools import find_packages, setup


TESTS_REQUIRE = []
DOCS_REQUIRE = ["Sphinx"]


def open_local(paths, mode="r", encoding="utf8"):
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), *paths)
    return codecs.open(path, mode, encoding)


def get_version(*args):
    with open_local(args, encoding="latin1") as fp:
        try:
            version = re.findall(
                r"^__VERSION__ = \"([\d\.]+)\"\r?$", fp.read(), re.M
            )[0]
            return version
        except IndexError:
            raise RuntimeError("Unable to determine version.")


def get_requirements(*args, is_lib=None):
    requirements = []
    with open_local(args, encoding="latin1") as fp:
        for ln in fp:
            if ln.startswith("#"):
                continue
            if ln.find("==") > -1:
                # requirements found, let's check if there's any comments
                if ln.find("#") > -1:
                    # we need to check if this comes from requirements or not
                    dep, annotation = ln.split("#")
                    if annotation.find("via -r requirements.in") > -1:
                        pkg = dep
                    else:
                        # dependency of a dependency
                        continue
                pkg = ln.strip()  # clean up any whitespace in there
                # need to strip version as we don't pin them
                pkg = pkg.split("==")[0]
                if pkg not in requirements:
                    requirements.append(pkg)
    return requirements


class RequirementsCommand(Command):
    """A custom command to show the current requirements of this module."""

    description = "shows the current requirements of this module"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run command."""
        version = self.distribution.get_version()
        name = self.distribution.get_name()
        self.announce(
            f"\n\nRequirements for {name} version {version}:\n",
            level=log.INFO,
        )
        for req in self.distribution.install_requires:
            self.announce(f" * {req}", level=log.INFO)


version = get_version("src", "dnsmasq_as_blocker", "__init__.py")
long_description = ""

with open_local(["README.rst"]) as fp:
    long_description += fp.read()
    long_description += "\n"

with open_local(["CHANGES.rst"]) as fp:
    long_description += fp.read()

setup(
    cmdclass={"requirements": RequirementsCommand},
    name="dnsmasq_as_blocker",
    version=version,
    url="https://github.com/vltr/dnsmasq-as-blocker",
    license="MIT",
    description=(
        "Some custom scripts to generate a custom blacklist configuration for "
        "dnsmasq to prevent that some domains try and (ocasionally) take "
        "your personal data."
    ),
    author="Richard Kuesters",
    author_email="rkuesters@gmail.com.com",
    long_description=long_description,
    keywords="dnsmasq blacklist websites",
    packages=find_packages("src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    tests_require=TESTS_REQUIRE,
    install_requires=get_requirements("requirements.txt"),
    include_package_data=True,
    zip_safe=False,
    extras_require={"test": TESTS_REQUIRE, "docs": ["Sphinx"]},
    entry_points={
        'console_scripts': ['dnsmasq-as-blocker=dnsmasq_as_blocker.cli:cli'],
    }
)
