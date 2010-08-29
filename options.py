
import yaml, os

def from_string(string):
	return yaml.load(string)
		
def from_file(filename):
	with open(filename, "r") as f:
		return from_string(f.read())
		
def from_data(name):
	"""
	from_data loads data files provided within the flake program itself
	"""
	try:
		from pkg_resources import resource_string
		return from_string(resource_string(__name__, name))
	except ImportError:
		fn = os.path.join(os.path.dirname(__file__), name)
		if os.path.isfile(fn):
			return from_file(fn)
		raise IOError("File not found")


class YamlOptions(object):
	def __init__(self, o = dict(), d = dict()):
		self.options =  o
		self.defaults = d
		
	def load(self):
		pass
		
	def walk(self, context, keys):
		"""
		Walk through a YAML-loaded dict tree to find a config var, if not, return None
		i.e. if keys is ('one', 'two', 'three') then it will try to find
		context['one']['two']['three']
		"""
		for key in keys:
			if isinstance(context, dict) and key in context:
				context = context[key]
				continue
			return None
		return context
		
	def get_default(self, args):
		return self.walk(self.defaults, args)
		
	def get(self, *args, **kwargs):
		"""
		Try to find the keys specified in args by walking through the dict tree,
		if it fails, return the value from the default tree
		"""
		ret = self.walk(self.options, args)
		if ret is None:
			ret = self.get_default(args)
		if "type" in kwargs:
			try:
				ret = kwargs["type"](ret)
			except:
				return self.get_default(args)
		return ret

class ProjectOptions(YamlOptions):
	"""
	Provides options for project files (Flakefiles),
	through the defaults provided with flake and through
	the ones defined in the project file
	"""
	def load(self, filenames):
		self.defaults = from_data("config/project_defaults.yaml")
		use_file = None
		for fn in filenames:
			if os.path.isfile(fn):
				use_file = fn
				break
		if use_file:
			self.options = from_file(use_file)
			return True
		return False
	
class UserOptions(YamlOptions):
	"""
	Provides options for the user that are global throughout flake.
	There are defaults provided, but they can also be changed through
	a flakeconfig file in the home folder.
	"""
	def load(self):
		self.defaults = from_data("config/user_defaults.yaml")
		optpath = os.path.expanduser("~/.flakeconfig")
		if os.path.isfile(optpath):
			self.options = from_file(optpath)
		else:
			try:
				with open(optpath, "w") as f:
					f.write("\n# Please set this value to the location of your Flex SDK\n")
					f.write("flex-path: \n\n")
			except:
				pass
		

