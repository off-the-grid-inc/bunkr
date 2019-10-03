import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='bunkrwallet',
    version='0.1.2',
    author="off-the-grid-inc",
    author_email="accounts@off-the-grid.io",
    description="Lite bitcoin bunkrwallet working on top of Bunkr secrets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    py_modules=['bunkrwallet'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "ecdsa>=0.13.2",
        "python-bitcoinlib>=0.10.1",
        "requests>=2.22.0",
        "punkr>0.1"
    ]
 )
