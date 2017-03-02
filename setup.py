from setuptools import setup, find_packages

setup(
    name='drillsrs',
    version='0.1',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'drill-srs = drillsrs.__main__:main'
        ]
    },
    install_requires=[
        'python-dateutil',
        'sqlalchemy',
        'jinja2',
    ],
    package_dir={'drillsrs': 'drillsrs'},
    package_data={'drillsrs': ['data/*.*']},
)
