from setuptools import setup, find_packages

setup(
    name='magiccode',
    version='0.1.0',
    description='Problem solving agent for Plitka Game\'s "Brain Code" levels, on the Nintendo Switch store',
    author='David Golembiowski',
    author_email='dmgolembiowski@gmail.com',
    url='https://github.com/dmgolembiowski/MagicCodeGame-Solver',
    packages=['magic'],
    install_requires=[], # No dependencies required! It's all from scratch! 
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['my-command=magiccode.cli:main']
    },
    package_data={'magiccode': ['data/*']}
)
