from distutils.core import setup

setup(
    name='osmdiff',
    url='https://github.com/osmlab/osmdiff',
    version='0.1.9',
    packages=['osmdiff', 'osmdiff.osm'],
    description="Interact with OpenStreetMap (Augmented) Diff files.",
    long_description="Read the README.md",
    license='Apache 2.0',
    author="Martijn van Exel",
    author_email="m@rtijn.org",
    download_url="",
    keywords=["osm", "openstreetmap", "diff", "augmented diff"],
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        'requests',
        'python-dateutil'
    ],
)
