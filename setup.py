import setuptools


setuptools.setup(
    name='composerstoolkit',
    version='0.2.0',
    license='LICENSE',
    author='nickpeck',
    author_email='',
    description='',
    keywords=[],
    url='',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    scripts=[
        "src/composerstoolkit/scripts/initproject.py",
        "src/composerstoolkit/scripts/initproject.cmd"
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
    include_package_data=True,
)
