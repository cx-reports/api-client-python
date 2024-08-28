from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="cxreports_api_client",
    description="Connect to CxReports API from your application.",
    version="0.0.1",
    package_dir={"": "cxreports_api_client"},
    packages=find_packages(where="cxreports_api_client"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cx-reports/api-client-python",
    install_requires=['requests'],
    author="Codaxy",
    license="MIT",
    author_email="support@cx-reports.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)