import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="uniulm_mensaparser",
    version="0.2.2",
    author="Tanikai",
    author_email="kai@anter.dev",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tanikai/uniulm_mensaparser",
    project_urls={
        "Bug Tracker": "https://github.com/Tanikai/uniulm_mensaparser/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=["uniulm_mensaparser"],
    python_requires=">=3.7",
    install_requires=[
        "beautifulsoup4",
        "pymupdf",
        "requests"
    ]
)
