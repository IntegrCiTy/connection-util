from setuptools import setup, find_packages
import platform


setup(name="connection-util",
      maintainer="The OBNL Team",
      maintainer_email="gillian.basso@hevs.ch",
      url="https://github.com/IntegrCiTy/connection-util",
      version="0.2.0",
      platforms=[platform.platform()],  # TODO indicate really tested platforms

      packages=find_packages(),
      install_requires="pika",

      # metadata

      description="An open tool for co-simulation",
      long_description="README.md",

      license="Apache License 2.0",

      keywords="RabbitMQ, JSON",

      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Console",
                   "Intended Audience :: Science/Research",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Apache License 2.0",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.5",
                   "Topic :: Software Development :: Code Generators",
                   "Topic :: Utilities"]
      )
