import os
import json
from collections import OrderedDict, MutableMapping
import mimetypes
from copy import deepcopy

def flattenDict(dictToFlatten,separator=':',dictConstructor=OrderedDict):
	'''
	[Description]
		Flatten nested dict-like object.
	[Arguments]
		dictToFlatten (dict): Nested dictionary-like object to flatten.
		*separator (str): Parent-child key separator.
		*dictConstructor (class): Class to create flat dict (dict, OrderedDict or custom).
		->return (dictConstructor.__class__): Flat dictionary-like object of dictConstructor type.
	'''
	new_dict = dictConstructor()
	for key,value in dictToFlatten.items():
		if isinstance(value,dict):
			new_dict[key] = value
			_dict = dictConstructor()
			for _key, _value in flattenDict(value).items():
				_dict[separator.join([key,_key])] = _value
			new_dict.update(_dict)
		elif isinstance(value, list):
			if value == []:
				new_dict[key] = value
			elif isinstance(value[0], dict):
				new_dict[key] = value
				listElementCounter = 0
				for dictElement in value:
					_dict = dictConstructor()
					for _subKey, _subValue in flattenDict(dictElement).items():
						_dict[separator.join([key,str(listElementCounter),_subKey])] = _subValue
					new_dict.update(_dict)
					listElementCounter += 1
			else:
				new_dict[key] = value
		else:
			new_dict[key] = value
	return new_dict

def unflattenDict(dictToUnflatten,separator=':',dictConstructor=OrderedDict):
	'''
	[Description]
		Nest dict-like object.
	[Arguments]
		dictToFlatten (dict): Dictionary-like object to nest.
		*separator (str): Parent-child key separator.
		*dictConstructor (class): Class to create flat dict (dict, OrderedDict or custom).
		->return (dictConstructor.__class__): Nested dictionary-like object of dictConstructor type.
	'''
	resultDict = dictConstructor()
	for key, value in dictToUnflatten.iteritems():
		parts = key.split(separator)
		d = resultDict
		for part in parts[:-1]:
			if part not in d:
				d[part] = dictConstructor()
			d = d[part]
		d[parts[-1]] = value
	return resultDict

def byteify(dictToByteify,dictConstructor=OrderedDict):
	'''
	[Description]
		Convert dict-like object unicode to string.
	[Arguments]
		dictToByteify (dict): Dictionary-like object to convert its unicode characters to string.
		*dictConstructor (class): Class to create flat dict (dict, OrderedDict or custom).
		->return (dictConstructor.__class__): Dictionray-like object of dictConstructor class with unicode converted to string.
	'''
	if isinstance(dictToByteify, dict):
		oDict = dictConstructor()
		for key,value in dictToByteify.iteritems():
			oDict[byteify(key)] = byteify(value)
		return oDict
	elif isinstance(dictToByteify, list):
		return [byteify(element) for element in dictToByteify]
	elif isinstance(dictToByteify, unicode):
		return dictToByteify.encode('utf-8')
	else:
		return dictToByteify

def floatify(dictToFloatify,dictConstructor=OrderedDict):
	'''
	[Description]
		Convert dict-like object numbers to float.
	[Arguments]
		dictToFloatify (dict): Dictionary-like object to convert its numbers characters to float.
		*dictConstructor (class): Class to create flat dict (dict, OrderedDict or custom).
		->return (dictConstructor.__class__): Dictionray-like object of dictConstructor class with numbers converted to float.
	'''
	if isinstance(dictToFloatify, dict):
		oDict = dictConstructor()
		for key,value in dictToFloatify.iteritems():
			oDict[floatify(key)] = floatify(value)
		return oDict
	elif isinstance(dictToFloatify, list):
		return [floatify(element) for element in dictToFloatify]
	# bools are instance of int in python so this must be checked first.
	elif isinstance(dictToFloatify, bool):
		return dictToFloatify
	elif isinstance(dictToFloatify, int):
		return float(dictToFloatify)
	else:
		return dictToFloatify

def insertComments(jsonString,commentsDict,emptyComments=False):
	'''
	[Description]
		Insert comments to JSON string.
	[Arguments]
		jsonString (str): String representation of JSON to insert comments into.
		commentsDict (dict): Flat dictionary relating each field with its corresponding comment.
		*emptyComments (bool): Set to True for including empty comments '//' for fields that do not have a comment assigned.
		->return (str): JSON string with comments.
	'''
	flatDict = flattenDict(json.loads(jsonString,object_pairs_hook=OrderedDict))
	commentJsonString = []
	commentedFieldsLog = []
	for row in jsonString.split('\n'):
		if isJsonField(row):
			key = row.strip().split(':')[0].split('"')[1]
			# look up if field has a comment.
			possiblePaths = [keys for keys in flatDict if key in keys.split(':') if keys not in commentedFieldsLog]
			path = possiblePaths[0]
			commentedFieldsLog.append(path)
			tab = ''.join(['\t' for i in range(len(row.split('\t'))-1)])
			if commentsDict.get(path,None) != '//' or emptyComments == True:
				if path in commentsDict.keys():
					commentJsonString.append(tab+commentsDict[path])
			commentJsonString.append(row)
		else:
			commentJsonString.append(row)
	return '\n'.join(commentJsonString)

def parseComments(jsonString):
	'''
	[Arguments]
		Remove comments from JSON string and create a separated dict that relates each JSON field with its corresponding comment.
		An empty comment is associated to uncommented fields.
	[Arguments]
		jsonString (str): String represenation of JSON.
		->return (tuple[str/dict]): Return a tuple containing the jsonString without comments and the dict relating fields to comments.
	'''
	flatDict = flattenDict(json.loads(''.join([row for row in jsonString.split('\n') if len(row.split('//')) == 1]),object_pairs_hook=OrderedDict))
	jsonAsList = jsonString.split('\n')
	cleanJson = []
	commentsDict = OrderedDict()
	hasCommentFlag = False
	for i,row in enumerate(jsonAsList):
		# row is a comment.
		if len(row.split('//')) > 1:
			key = jsonAsList[i+1].strip().split(':')[0].split('"')[1]
			comment = row.strip()
			possiblePaths = [kk for kk in flatDict if key in kk.split(':')]
			if len(possiblePaths) > 1:
				for p in possiblePaths:
					if p not in commentsDict.keys():
						path = p
						break
			else:
				path = possiblePaths[0]
			commentsDict[path] = row.strip()
			hasCommentFlag = True
		# row is a field.
		else:
			if hasCommentFlag == True:
				cleanJson.append(row)
			else:
				if isJsonField(row):
					cleanJson.append(row)
					key = jsonAsList[i].strip().split(':')[0].split('"')[1]
					possiblePaths = [keys for keys in flatDict if key in keys.split(':')]
					if len(possiblePaths) > 1:
						for p in possiblePaths:
							if p not in commentsDict.keys():
								path = p
								break
					else:
						path = possiblePaths[0]
					commentsDict[path] = '//'
				else:
					cleanJson.append(row)
			hasCommentFlag = False
	return '\n'.join(cleanJson),commentsDict

def isJsonField(s):
	'''
	[Description]
		Determine if string is a JSON field by checking if it of
		the form "fieldName": or "fieldName":fieldValue.
	[Arguments]
		s (str): String to be checked.
		->return (bool): True if string is a JSON field or False otherwise.
	'''
	if s.strip()[-2:] == '":':
		return True
	elif len(s.split(':')) > 1:
		if s[s.index(':')-1:s.index(':')+1] == '":':
			return True
		else:
			return False
	else:
		return False

def dictToJsonString(jsonDict,pretty=True,tabIndex=1,init=True):
	'''
	[Description]
		Convert dict or OrderedDict into its JSON string representation.
	[Arguments]
		jsonDict (dict): JSON dictionary.
		pretty (bool): Tabulate rows for better readability.
		*tabIdenx (int): Current tabulate depth level.
		*init (bool): Set to True on first call so that no commas are added to last closing bracket.
		->return (str): JSON string representation of dictionary-like object.
	'''
	def parseString(s):
		if type(s) == str or type(s) == unicode:
			return '"'+str(s).strip()+'"'
		elif s == None:
			return 'null'
		elif type(s) == bool:
			return str(s).lower().strip()
		else:
			return str(s).strip()
	jsonString = '{\n'
	# string to prepend to all fields inside current section so that they have corresponding tab depth.
	if pretty == True:
		tab = ''.join(['\t' for i in range(tabIndex)])
		tab_next = ''.join(['\t' for i in range(tabIndex+1)])
		tab_prev = ''.join(['\t' for i in range(tabIndex-1)])
	else:
		tab = tab_next = tab_prev = ''
	for field in jsonDict:
		if isinstance(jsonDict[field],dict):
			jsonString += tab+'"'+field+'":\n'
			jsonString += tab+dictToJsonString(jsonDict[field],pretty,tabIndex+1,init=False)
		elif type(jsonDict[field]) == list:
			if len(jsonDict[field]) > 0:
				if isinstance(jsonDict[field][0],dict):
					jsonString += tab+'"'+field+'":\n'
					jsonString += tab+'[\n'
					for i,listElement in enumerate(jsonDict[field]):
						jsonString += tab_next+dictToJsonString(jsonDict[field][i],pretty,tabIndex+2,init=False)
					jsonString = jsonString[:-2]+'\n' # remove last comma.
					jsonString += tab+'],\n'
				else:
					jsonString += tab+'"'+field+'":\n'
					jsonString += tab+'[\n'
					for element in jsonDict[field]:
						jsonString += tab_next+parseString(element)+',\n'
					jsonString = jsonString[:-2]+'\n'
					jsonString += tab+'],\n'
			else:
				jsonString += tab+'"'+field+'":[],\n'
		else:
			jsonString += tab+'"'+field+'":'+parseString(jsonDict[field])+',\n'
	# remove last comma of las element of each group of fields.
	if jsonString[-2] == ',':
		jsonString = jsonString[:-2]+'\n'
	# close section.
	jsonString += tab_prev+'}\n'
	if init == False:
		jsonString = jsonString[:-1]+',\n'
	return jsonString

class SmartJson(object):
	'''
	Advanced functionality for handling JSON files.
	'''
	def __init__(self, path, byteifyDict=True, floatifyDict=True, files=[], binaries=[]):
		'''
		[Arguments]
			path (str): Python dict, path to JSON file, string containing JSON or path to folder.
			*byteifyDict (bool): Convert JSON unicode to string.
			*floatifyDict (bool): Convert JSON numbers to float.
			*files (list[str]): Text file extensions valid for reading to / writting from folder.
			*binaries (list[str]): Binary file extensions valid for reading to / writting from folder.
		'''
		self.files = files
		self.binaries = binaries
		if isinstance(path, dict):
			self.dict = path
			self.comments = {}
		elif os.path.isdir(path):
			print '[SmartJson|__init__]: Loading JSON from folder:',path
			self.dict, self.comments = self._loadFromFolder(path)
		elif os.path.isfile(path):
			print '[SmartJson|__init__]: Loading JSON from file:',path
			self.dict, self.comments = self._loadFromFile(path)
		elif type(path) == str:
			print '[SmartJson|__init__]: Loading JSON from string.'
			self.dict, self.comments = self._loadFromString(path)
		else:
			raise TypeError('[SmartJson|__init__]: File type not supported:'+str(type(path)))
		#
		if byteifyDict ==  True:
			self.dict = byteify(self.dict)
		if floatifyDict == True:
			self.dict = floatify(self.dict)

	def __getitem__(self,field):
		'''
		Treat SmartJson as a dict.
		'''
		return self.dict[field]

	def __setitem__(self,field,value):
		'''
		Treat SmartJson as a dict.
		'''
		self.dict[field] = value

	def __iter__(self):
		'''
		Treat SmartJson as a dict.
		'''
		return self.dict.keys().__iter__()

	def __repr__(self):
		'''
		Return self.dict key-value paris.
		'''
		keyVals = []
		for key in self:
			keyVals.append(key)
		return '\n'.join(keyVals)

	def keys(self):
		'''
		Treat SmartJson as a dict.
		'''
		return self.dict.keys()

	# Loaders

	def _loadFromFolder(self,basePath,_path=None):
		'''
		[Description]
			Create a json dict from folder structue.
		[Arguments]
			basePath (str): Path to folder to load.
			*_path (str): Path to subfolder to load (called recursively).
			->return (dict/dict): Parsed JSON dict and dictionary relating each JSON dict field to its associated comment.
		'''
		jsonDict = OrderedDict()
		commentsDict = OrderedDict()
		if _path != None:
			fullPath = os.path.join(basePath,_path)
		else:
			fullPath = basePath
		for file in os.listdir(fullPath):
			filePath = fullPath+os.path.sep+file
			if os.path.isdir(filePath):
				jsonDict[file],cDict = self._loadFromFolder(basePath,filePath)
				commentsDict.update(cDict)
			elif os.path.isfile(filePath):
				# determine file extension.
				if len(file.split('.')) > 1:
					extension = file.split('.')[-1]
				else:
					extension = None
				# append directly as JSON.
				if extension == 'json':
					print '[SmartJson|_loadFromFolder]: Reading JSON file',file
					jsonString,cDict = parseComments(''.join(open(filePath).readlines()))
					jsonDict[file] = json.loads(jsonString,object_pairs_hook=OrderedDict)
					parentCDict = OrderedDict()
					parent = ':'.join(filePath.split(basePath)[-1].split(os.path.sep))[1:]
					for key in cDict:
						parentCDict[parent+':'+key] = cDict[key]
					commentsDict.update(parentCDict)
				else:
					# append directly as text.
					if extension in self.files:
						print '[SmartJson|_loadFromFolder]: Reading text file',file
						with open(filePath,'r') as f: text = [row.strip() for row in f.readlines()]
						jsonDict[file] = text
					elif extension != None:
						# convert binary to base64 string.
						if extension in self.binaries:
							with open(filePath, "rb") as imageFile: imageAsString = base64.b64encode(imageFile.read())
							jsonDict[file] = imageAsString
						else:
							print '[SmartJson|_loadFromFolder]: Skipping file',file
					else:
						print 'WARNING [SmartJson|_loadFromFolder]: File',file,'has no extension and will be parsed as text and converted to .txt.'
						# parse as normal text.
						with open(filePath,'r') as f: text = f.readlines()
						jsonDict[file] = text
		return jsonDict,commentsDict

	def _loadFromFile(self,path):
		'''
		[Description]
			Load from JSON file.
		[Argumnets]
			path (str): Path to file.
			->return (dict/dict): Parsed JSON dict and dictionary relating each JSON dict field to its associated comment.
		'''
		jsonString,commentsDict = parseComments(''.join(open(path).readlines()))
		jsonDict = json.loads(jsonString,object_pairs_hook=OrderedDict)
		return jsonDict,commentsDict

	def _loadFromString(self,jsonString):
		'''
		[Description]
			Load from JSON string.
		[Arguments]
			jsonString (str): String containing JSON data.
			->return (dict/dict): Parsed JSON dict and dictionary relating each JSON dict field to its associated comment.
		'''
		jsonString,commentsDict = parseComments(jsonString)
		jsonDict = json.loads(jsonString,object_pairs_hook=OrderedDict)
		return jsonDict,commentsDict

	# Savers

	def dump(self,path,mode='file',comments=True, pretty=True):
		'''
		[Description]
			Save JSON. Interfaces all save methods.
		[Arguments]
			path (str): Path to save JSON.
			*mode (str): File or Folder.
			*comments (bool): Write comments to JSON.
			*pretty (bool): Tabulate rows for better readability.
		'''
		if mode.lower() == 'file':
			print '[SmartJson|dump]: Saving as file'
			self._saveAsFile(path,comments,pretty)
		else:
			print '[SmartJson|dump]: Saving as folder'
			self._saveAsFolder(path,comments=comments,pretty=pretty)

	def _saveAsFolder(self,basePath,_path=None,_jsonDict=None,overwrite=True,comments=True,pretty=True):
		'''
		[Description]
			Save project as different separated folders based on its JSON representation.
		[Arguments]
			basePath (str): Path to folder to load.
			*_path (str): Path to subfolder to load (called recursively).
			*_jsonDict (dict): JSON dictionary to save (called recursively)
			*overwrite (bool): Overwrite JSON file / folder if it already exists.
			*comments (bool): Write comments to JSON.
			*pretty (bool): Tabulate rows for better readability.
		'''
		if _jsonDict == None:
			_jsonDict = deepcopy(self.dict)
			if not os.path.exists(basePath):
				os.mkdir(basePath)

		for key in _jsonDict:
			if _path != None:
				filePath = os.path.join(basePath,_path,key)
			else:
				filePath = basePath + os.path.sep + key			
			# determine extension.
			if len(key.split('.')) > 1:
				extension = key.split('.')[-1]
			else:
				extension = None
			# if key has no extension, it is a folder.
			if extension ==  None:
				if not os.path.exists(filePath):
					os.mkdir(filePath)
				print '[SmartJson|_saveAsFolder]: Creating folder',key
				self._saveAsFolder(basePath,filePath,_jsonDict=_jsonDict[key],overwrite=overwrite,comments=comments,pretty=pretty)
			# if key has extension, it is a file.
			else:
				if overwrite ==  False and os.path.exists(basePath):
					print '[SmartJson|_saveAsFolder]: File',key,'already exists, skipping'
				else:
					print '[SmartJson|_saveAsFolder]: Saving file',key
					# convert dict to JSON string, insert comments and write file.
					if extension == 'json':
						jsonString = dictToJsonString(_jsonDict[key],pretty)
						currentJsonCommentsDict = {}
						parent = ':'.join(filePath.split(basePath)[-1].split(os.path.sep))[1:]			
						for commentKey in self.comments:
							if parent in commentKey:
								currentJsonCommentsDict[commentKey.split(parent)[-1][1:]] = self.comments[commentKey]
						if comments == True:
							jsonString = insertComments(jsonString,currentJsonCommentsDict)
						with open(filePath, 'w') as f: f.write(jsonString)
					elif extension in self.files:
						with open(filePath, 'w') as f: f.write('\n'.join(_jsonDict[key]))
					elif extension in self.binaries:
						with open(key, "wb") as f: f.write(_jsonDict[key].decode('base64'))
					else:
						print ['WARNING [SmartJson|_saveAsFolder]: Unknown file type',key,', skipping.']

	def _saveAsFile(self,path,comments=True,pretty=True):
		'''
		[Description]
			Save dict to JSON file.
		[Arguments]
			path (str): Path to save JSON.
			*comments (bool): Write comments to JSON.
			*pretty (bool): Tabulate rows for better readability.
		'''
		text = self.asString(comments,pretty)
		with open(path, 'w') as f: f.write(text)

	# Utils

	def asString(self,comments=True,pretty=True):
		'''
		[Description]
			Returns a JSON string representation of self.dict.
		[Arguments]
			*comments (bool): Write comments to JSON.
			*pretty (bool): Tabulate rows for better readability.
			->return (str): JSON string representation of self.dict.
		'''
		jsonString = dictToJsonString(self.dict,pretty)
		if comments == True:
			jsonString = insertComments(jsonString,self.comments)
		return jsonString
