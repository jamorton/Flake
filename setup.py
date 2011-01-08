from setuptools import setup, find_packages
import flake
import shutil
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
		"flake": ["config/*.yaml"]
	}
)

shutil.rmtree("dist")
shutil.rmtree("Flake.egg-info")
shutil.rmtree("build")