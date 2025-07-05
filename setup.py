from setuptools import setup, find_packages

setup(
    name="infrahealth",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["click", "psutil", "docker",
                      "requests", "prometheus_client"],
    entry_points={
        "console_scripts": [
            "infrahealth = infrahealth.cli:main"
        ]
    },
    author="Usman Safder",
    description="A CLI for infrastructure health monitoring",
)
