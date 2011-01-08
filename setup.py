from setuptools import setup
import flake

setup(
	name = "Flake",
	description = "AS3 building and testing system",
	version = flake.__version__,
	author = flake.__author__,
	author_email = flake.__email__,
	url = flake.__url__,
	
	packages = find_packages(),
	
	entry_points = dict(
		console_scripts = ["flake = flake.flake:start"]
	),
	
	package_data = {
		"flake": ["*.yaml"]
	}
)