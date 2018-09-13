from setuptools import setup

setup(
    name='django-parsed-field',
    version='1.0.1',
    packages=['parsedfield'],
    url='https://github.com/achievement008/django-parsed-field',
    license='MIT',
    include_package_data=True,
    author='Sergei Korotko',
    author_email='achievement008@gmail.com',
    description='A reusable Django field that allows you to store parsed JSON in your model.',
    long_description=open("README.rst").read(),
    install_requires=['jsonfield'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
    ],
)
