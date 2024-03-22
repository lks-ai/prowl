from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='prompt-owl',
    version='0.1.7',
    packages=find_packages(where='.'),
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
    author='LoreKeeper Ltd',
    author_email='nathaniel@lorekeeper.co.uk',
    description='A Declarative Prompting Language for LLMs',
    long_description=long_description,
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
