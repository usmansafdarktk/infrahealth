from setuptools import setup, find_packages

setup(
    name="infrahealth",
    version="0.1.0",  # Update this for each release
    packages=find_packages(),
    install_requires=["click", "psutil", "docker",
                      "requests", "prometheus_client"],
    entry_points={
        "console_scripts": [
            "infrahealth=infrahealth.cli:cli",
        ],
    },
    author="Muhammad Usman Safder",
    author_email="usmansafderktk@gmail.com",
    description="A CLI for monitoring server and Docker container health",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/usmansafdarktk/infrahealth.git",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
