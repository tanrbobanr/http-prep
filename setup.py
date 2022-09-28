import setuptools
from webfetch import (
    __title__,
    __version__,
    __author__,
    __email__,
    __description__,
    __url__,
    __download_url__
)


with open("README.md", "r") as infile:
    long_description = infile.read()


setuptools.setup(
    name                          = __title__,
    version                       = __version__,
    author                        = __author__,
    author_email                  = __email__,
    description                   = __description__,
    long_description              = long_description,
    long_description_content_type = "text/markdown",
    url                           = __url__,
    download_url                  = __download_url__,
    install_requires              = [
        "requests"
    ],
    packages                      = setuptools.find_packages("webfetch"),
    package_dir                   = {"": "webfetch"},
    classifiers                   = [
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
