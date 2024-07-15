from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name='connect4',
    version='0.1',
    packages=find_packages(include=['connect4', 'connect4.*']),
    install_requires=read_requirements(),
    author='Saahil Agrawal',
    author_email='saahil@alumni.stanford.edu',
    description='A simple AI Agent setup to play connect4 against a human through command line interface',
    # long_description=open('README.md').read(),
    # long_description_content_type='text/markdown',
    url='https://github.com/Saahil-Agr/connect4',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)