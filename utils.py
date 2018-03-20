def dynamicTyped(s,forceFloat=True):
	'''
	[Description]
		Converts string to appropiate type: int, float, bool, string, dict or list (of homogeneous or heterogeneous type elements).
		Currently does not support dicts inside lists.
	[Arguments]
		s (str): String to convert to appropiate type.
	'''
	#utility functions
	def isNone(s):
		if s == 'None':
			return True
		return False

	def asBool(s):
		if s.lower() == "true":
			return True
		elif s.lower() == "false":
			return False

	def isBool(s):
		if s.lower() == "true" or s.lower() == "false":
			return True
		return False

	def isDict(s):
		if len(s) > 0:
			if s[0] == '{' and s[-1] == '}' and len(s.split(':')) > 1:
				return True
		return False

	def isList(s):
		if isDict(s) == False and ',' in s:
			return True
		return False

	def isInt(s):
		if '.' not in s:
			try:
				int(s)
				return True
			except:
				return False
		else:
			return False

	def isFloat(s):
		if '.' in s:
			try:
				float(s)
				return True
			except:
				return False
		else:
			return False

	def asString(s):
		try:
			if s[0] == '"':
				s = max(s.split('"'), key=len)
			if s[0] == "'":
				s = max(s.split("'"), key=len)
			if len(s.split('\n')) > 1:
				s = max(s.split('\n'), key=len)
			return s
		except IndexError:
			return s
	#check that given variable is a string
	if type(s) == str:
		#check if string is None, bool, float or int
		if isNone(s):
			return None
		if isBool(s):
			return asBool(s)
		elif isFloat(s):
			return float(s)
		elif isInt(s):
			if forceFloat == False:
				return int(s)
			else:
				return float(s)
		# #if string is a dict, determine type of each key-val pair
		# elif isDict(s):
		# 	keyVals = s[1:-1].split(',')
		# 	dict_temp = OrderedDict()
		# 	for keyVal in keyVals:
		# 		print 'kv-->',keyVal,keyVal.split(':')
		# 		key,val = keyVal.split(':')
		# 		print key,val
		# 		dict_temp[dynamicTyped(key)] = dynamicTyped(val)
		# 	return dict_temp
		#if string is a list list, determine type of each element
		elif isList(s):
			elements = s.split(',')
			s_temp = []
			for item in elements:
				s_temp.append(dynamicTyped(item))
			return s_temp
		else:
			return asString(s)
	elif type(s) == list:
		return [dynamicTyped(i) for i in s]
	else:
		return s
