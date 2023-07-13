"""setup module."""

import re
from pathlib import Path

from setuptools import find_packages, setup

name = "mse_cli"

version = re.search(
    r"""(?x)
    __version__
    \s=\s
    \"
    (?P<number>.*)
    \"
    """,
    Path(f"{name}/__init__.py").read_text(),
)

setup(
    name=name,
    version=version["number"],
    url="https://cosmian.com",
    license="MIT",
    project_urls={
        "Documentation": "https://docs.cosmian.com",
        "Source": "https://github.com/Cosmian/mse-cli",
    },
    author="Cosmian Tech",
    author_email="tech@cosmian.com",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8.0",
    description="Python CLI for Microservice Encryption",
    packages=find_packages(),
    zip_safe=True,
    install_requires=[
        "cryptography>=41.0.1,<42.0.0",
        "docker>=6.0.1,<7.0.0",
        "intel-sgx-ra>=2.0.1,<3.0",
        "jinja2>=3.0,<3.1",
        "mse-lib-crypto>=1.3,<1.4",
        "pydantic>=1.10.2,<2.0.0",
        "pyjwt>=2.6.0,<2.7.0",
        "requests>=2.31.0,<3.0.0",
        "toml>=0.10.2,<0.11.0",
        "urllib3>=1.26.13,<1.27.0",
    ],
    entry_points={
        "console_scripts": ["mse = mse_cli.main:main"],
    },
    package_data={"mse_cli": ["template/*", "template/**/*"]},
    tests_require=["pytest>=7.2.0,<7.5.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
