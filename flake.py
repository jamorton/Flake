#!/usr/bin/python

import os, sys, options, subprocess, shlex

# only python 2.7+ has argparse builtin, so we provide our own
try:
	import argparse
except ImportError:
	import myargparse as argparse
	
class SystemExit(Exception):
	pass

def error(msg):
	print "ERROR: %s" % msg
	raise SystemExit(msg)

class FlakeProject(object):
	def __init__(self):
		self.flex_path = ""
		self.mxmlc_flags = set()
		self.load_config()
		
	def load_config(self):
		# load user options
		self.uopts = options.UserOptions()
		self.uopts.load()
		# load project options (flakefile)
		self.popts = options.ProjectOptions()
		if not self.popts.load(self.uopts.get("flake-files")):
			error("No flake project file found")
		fp = self.uopts.get("flex-path")
		if not isinstance(fp, str) or not len(fp):
			error("You have not set the path to your Flex SDK. Please do so by editing" +
			"the .flakeconfig file in your home directory")
		self.flex_path = fp
		if not os.path.isfile(self.get_flex_path("frameworks", "flex-config.xml")):
			error("The flex SDK path you specified is invalid; a proper SDK was not found there")
		
	def get_flex_path(self, *args):
		return os.path.join(self.flex_path, *args)
		
	def flag(self, f):
		self.mxmlc_flags.add(f)
		
	def invoke_mxmlc(self, entry):
		mxmlc_bin = self.get_flex_path("bin", "mxmlc")
		flags = ""
		if len(self.mxmlc_flags):
			flags = " ".join(self.mxmlc_flags) + " "
		cmd = "%s %s-- %s" % (mxmlc_bin, flags, entry)
		print cmd
		popen = subprocess.Popen(shlex.split(cmd), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		return popen.communicate()
		
	def build(self):
		opts = self.popts
		entry = opts.get("build", "entry")
		self.flag("-output " + opts.get("build","output",type=str))
		self.flag("-target-player=" + opts.get("build","flash-version",type=str))
		self.flag("-debug=" + str(opts.get("build","debug",type=bool)).lower())
		self.flag("-default-size %d %d" % (
			opts.get("build", "movie", "width",  type=int),
			opts.get("build", "movie", "height", type=int)))
		self.flag("-default-frame-rate %d" % opts.get("build", "movie", "fps", type=int))
		self.flag("-default-background-color " + opts.get("build", "movie", "bg", type=str))
		# fixes some weird issue with the Flex SDK 4.0
		self.flag("-static-link-runtime-shared-libraries=true")
		self.flag(opts.get("build", "mxmlc-options", type=str))
		
		ret = self.invoke_mxmlc(entry)
		print ret[0]
		if len(ret[1]):
			print ret[1]
			return False
		return True
		
	def run(self):
		pass
		
	def test(self):
		if (self.build()):
			self.run()
			
	def create_mxmlc_flags(self):
		pass
		
def run():
	parser = argparse.ArgumentParser(description="Build and/or test a flash project using a Flakefile")
	parser.add_argument("action", metavar = "ACTION", type = str, nargs = "?", default = "test",
	                    help = "Command to execute")
	parser.add_argument("target", metavar = "TARGET", type = str, nargs = "?", default = None,
	                    help = "Build target, defaults are release and debug")
	                    
	commands = parser.parse_args()
	
	if commands.action not in ("build", "test", "run"):
		error("Invalid action, options are: build, test, run")
	
	project = FlakeProject()
	
	{ "build": project.build,
	  "test": project.test,
	  "run": project.run
	}[commands.action]()
	

if __name__ == "__main__":
	try:
		run()
	except SystemExit:
		print "Exiting..."

