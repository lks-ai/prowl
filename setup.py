from setuptools import setup, find_packages

setup(
    name='prowl',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests>=2.31.0',
        'aiohttp>=3.9.1',
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'prowl=prowl.cli:main',
        ],
    },
    # Additional metadata
    author='Nathaniel',
    author_email='nathaniel@example.com',
    description='A Declarative Prompting Language for LLMs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/lks-ai/prowl',
    license='MIT',
    classifiers=[
        # Classifiers help users find your project by categorizing it.
        # For a list of valid classifiers, see https://pypi.org/classifiers/
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)