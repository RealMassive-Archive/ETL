from setuptools import setup

setup(
    name='ETL',
    version='1.0',
    install_requires=[
        'nose==1.3.7',
        'datadiff==2.0.0',
        'unicodecsv==0.14.1'
    ],
    description='ETL tools for API V2',
    packages=['ETL']
)
