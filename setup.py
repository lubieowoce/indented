from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name     = 'indented',
	version  = '0.9.0',
	packages = find_packages(),
	
	description      = 'Tools for generating Python code and other indented text.',
	long_description = long_description,
	long_description_content_type = "text/markdown",
	keywords    = 'codegen code generation indented macro',

	author       = 'J Uryga',
	author_email = 'lolzatu2@gmail.com',
	project_urls = {
		'Source': 'https://github.com/lubieowoce/indented',
	},
)
