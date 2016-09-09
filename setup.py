from setuptools import setup

setup(name='bomtool',
      version= '0.0.0',
      packages=['bomtool'],
      entry_points={
          'console_scripts': [
              'bomtool = bomtool.__main__:main'
          ]
      },
)
