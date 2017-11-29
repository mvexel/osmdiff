from distutils.core import setup

setup(
    name='osmdiff',
    url='https://github.com/osmlab/osmdiff',
    version='0.1.5',
    packages=['osmdiff'],
    description="Interact with OpenStreetMap (Augmented) Diff files.",
    long_description="Read the README.md",
    license='Apache 2.0',
    author="Martijn van Exel",
    author_email="m@rtijn.org",
    download_url="",
    keywords=["osm", "openstreetmap", "diff", "augmented diff"],
    classifiers=[],
    install_requires=[
        'requests',
    ],
)
