from setuptools import setup, find_packages

setup(
    name='ArangoDjango',
    version= '0.0.3',
    packages=find_packages(),
    requires=[
        'Django',
        'djangorestframework',
        'ArangoPy',
    ],
    url='https://github.com/saeschdivara/ArangoDjango',
    license='MIT',
    author='saskyrardisaskyr',
    author_email='saeschdivara@gmail.com',
    description='Bridge between the django and the arangodb world'
)
