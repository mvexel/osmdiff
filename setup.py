from distutils.core import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='osmdiff',
    url='https://github.com/osmlab/osmdiff/archive/0.1.2.tar.gz',
    version='0.1.2',
    packages=['osmdiff'],
    description="Interact with OpenStreetMap (Augmented) Diff files.",
    license='Apache 2.0',
    author="Martijn van Exel",
    author_email="m@rtijn.org",
    download_url="",
    keywords=["osm", "openstreetmap", "diff", "augmented diff"],
    classifiers=[]
)
