import io
from setuptools import setup, find_packages


setup(
    name="sota-extractor",
    version="0.0.17",
    description="Automatic SOTA (state-of-the-art) extraction.",
    long_description=io.open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    platforms=["Windows", "POSIX", "MacOS"],
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
    ],
    keywords="sota table",
    author="Robert Stojnic",
    author_email="robert@atlasml.io",
    maintainer="Viktor Kerkez",
    maintainer_email="viktor@atlasml.io",
    url="https://github.com/paperswithcode/sota-extractor",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=io.open("requirements.txt").read().splitlines(),
    include_package_data=True,
    scripts=[],
    entry_points="""
        [console_scripts]
        sota-extractor=sota_extractor.__main__:cli
    """,
)
