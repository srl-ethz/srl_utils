import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='srl-utils',
    version='0.0.1',
    author='Soft Robotics Lab',
    author_email='gavin.cangan@srl.ethz.ch',
    description='A collection of shared utilities for SRL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/srl-ethz/srl-utils',
    project_urls = {
        "Bug Tracker": "https://github.com/srl-ethz/srl-utils/issues"
    },
    license='MIT',
    packages=['srl-utils'],
    install_requires=['click==8.1.2', 'opencv-python==4.6.0.66', 'pyserial==3.5'],
)