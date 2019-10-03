import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='punkr',
    version='0.2.0',
    author="off-the-grid-inc",
    author_email="accounts@off-the-grid.io",
    description="Bunkr operations wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    py_modules=['punkr'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "parse"
    ]
 )
