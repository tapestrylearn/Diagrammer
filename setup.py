import setuptools


setuptools.setup(
    name='diagrammer',
    version='0.0.14',

    author='Tapestry',
    author_email='tech@tapestrylearn.com',

    description="Tapestry's proprietary diagram generation system", 
    url='https://github.com/tapestrylearn/Diagrammer',

    packages=setuptools.find_packages(),

    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],

    python_requires='>=3.6',
)
