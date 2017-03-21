from setuptools import setup, find_packages

setup(
    author='Marcin Kurczewski',
    author_email='rr-@sakuya.pl',
    name='drillsrs',
    long_description='Spaced repetition learning in CLI',
    version='0.2',
    url='https://github.com/rr-/drill',
    packages=find_packages(),

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
    include_package_data=True,
    zip_safe=False,

    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Education',
    ])
