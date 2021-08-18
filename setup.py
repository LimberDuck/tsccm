import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

about = {}
with open("tsccm/_version.py") as f:
    exec(f.read(), about)

setuptools.setup(
    name="tsccm",
    version=about["__version__"],
    author="Damian Krawczyk",
    author_email="damian.krawczyk@limberduck.org",
    description="TSCCM (Tenable.SC CLI Manager) by LimberDuck",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LimberDuck/tsccm",
    packages=setuptools.find_packages(),
    install_requires=required,
    entry_points={
        "console_scripts": [
            "tsccm = tsccm.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
    ],
)
