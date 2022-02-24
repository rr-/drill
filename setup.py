from setuptools import find_packages, setup

setup(
    author="Marcin Kurczewski",
    author_email="rr-@sakuya.pl",
    name="drillsrs",
    long_description="Spaced repetition learning in CLI",
    version="0.3",
    url="https://github.com/rr-/drill",
    packages=find_packages(),
    entry_points={"console_scripts": ["drill-srs = drillsrs.__main__:main"]},
    install_requires=["xdg", "python-dateutil", "sqlalchemy", "jinja2"],
    extras_require={
        "anki": ["lxml", "anki-export"],
    },
    package_dir={"drillsrs": "drillsrs"},
    package_data={"drillsrs": ["data/*.*"]},
    classifiers=[
        "Environment :: Console",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Education",
    ],
)
