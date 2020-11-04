import xml.etree.ElementTree as ET
# TODO: This is a work in progress and probably doesnt work as advertised yet. For anyone interested in working on this
#  requiring more info, please log an issue
#  you could add a search term here to return a property type - i.e. command / enum / etc
#  First pass - get the root group, and all the pFeatures
tree = ET.parse("general_25317_20170510110658.xml")
pf = '{http://www.genicam.org/GenApi/Version_1_1}'
root = tree.getroot()
base = root.findall(f"./{pf}Group[@Comment='Root']/{pf}Category[@Name='Root']/{pf}pFeature")
for target in base:
	# these are the headings
	allheadings = root.findall(f"./{pf}Group[@Comment='{target.text}']/{pf}Category[@Name='{target.text}']/{pf}pFeature")
	for heading in allheadings:
		#print(f"Headings -> {target.text} Property -> {heading.text}")
		floatheadings = root.findall(f"./{pf}Group[@Comment='{target.text}']/{pf}Float[@Name='{heading.text}']/{pf}Visibility")
		for isvisible in floatheadings:
			if isvisible.text == "Beginner" or isvisible.text == "Expert" or isvisible.text == "Guru":
				print(f"{target.text}")
				print(f"    Property -> {heading.text} | Visibility -> {isvisible.text} Type -> Float")
		intheadings = root.findall(f"./{pf}Group[@Comment='{target.text}']/{pf}Integer[@Name='{heading.text}']/{pf}Visibility")
		for isvisible in intheadings:
			if isvisible.text == "Beginner" or isvisible.text == "Expert" or isvisible.text == "Guru":
				print(f"Heading {target.text}")
				print(f"    Property -> {heading.text} | Visibility -> {isvisible.text} | Type -> Integer")
		boolheadings = root.findall(f"./{pf}Group[@Comment='{target.text}']/{pf}Boolean[@Name='{heading.text}']/{pf}Visibility")
		for isvisible in boolheadings:
			if isvisible.text == "Beginner" or isvisible.text == "Expert" or isvisible.text == "Guru":
				print(f"Heading {target.text}")
				print(f"    Property -> {heading.text} | Visibility -> {isvisible.text} | Type -> Boolean")
		enumheadings = root.findall(f"./{pf}Group[@Comment='{target.text}']/{pf}Enumeration[@Name='{heading.text}']/{pf}Visibility")
		for isvisible in enumheadings:
			if isvisible.text == "Beginner" or isvisible.text == "Expert" or isvisible.text == "Guru":
				print(f"Heading {target.text}")
				print(f"    Property -> {heading.text} | Visibility -> {isvisible.text} | Type -> Enumeration")
		stringheadings = root.findall(f"./{pf}Group[@Comment='{target.text}']/{pf}StringReg[@Name='{heading.text}']/{pf}Visibility")
		for isvisible in stringheadings:
			if isvisible.text == "Beginner" or isvisible.text == "Expert" or isvisible.text == "Guru":
				print(f"Heading {target.text}")
				print(f"    Property -> {heading.text} | Visibility -> {isvisible.text} | Type -> StringReg")
		commandheadings = root.findall(f"./{pf}Group[@Comment='{target.text}']/{pf}Command[@Name='{heading.text}']/{pf}Visibility")
		for isvisible in commandheadings:
			if isvisible.text == "Beginner" or isvisible.text == "Expert" or isvisible.text == "Guru":
				print(f"Heading {target.text}")
				print(f"    Property -> {heading.text} | Visibility -> {isvisible.text} | Type -> Command")
# add all of the above to a list and then return that list so that you can use it
# Nested Dictionary -> Nest -> Heading:Name ->Property:Name, Visibility:Name Type:Name,



# Second pass - get the Groups where the names are from the root group

# tree = Et.parse("general_25317_20170510110658.xml")
# print(tree)
# root = tree.getroot()

#with open('general_25317_20170510110658.xml') as tmpfile:
#	doc = ET.iterparse(tmpfile, events=("start", "end"))
#	doc = iter(doc)
#	event, root = doc.__next__()
#	num = 0
#	for event, elem in doc:
#		# print('event -> {}\n elem -> {}\n contents-> {}\n'.format(event, elem.tag, elem.attrib))
#		if event == 'end' and str(elem.tag).__contains__('Category'):
#			break
# print("tag is {}".format(root.tag))
# print("tag is {}".format(root.attrib))

# root = Et.fromstring("general_25317_20170510110658.xml")

# print(root.attrib)

# get the target groups
# for node in root.iter():
#	print(node.tag, node.attrib)
#print('moving on')
#tree = ET.parse("general_25317_20170510110658.xml")

# for node in root.iter(): #find('.//Group/Category'):
#    print(node.tag, node.attrib)

#print("second")
#root = tree.getroot()
# print(root.tag)
# print('\n')

#stringitem = "StringReg"
#intitem = "Integer"
#floatitem = "Float"
#boolitem = "Boolean"
#enumitem = "Enumeration"

#heading = "AcquisitionControl"

#targetsearch = "ReverseY"  # this will come from search
#targetsearchlocation = intitem
# locate the Property you want
#print(f"{heading}")
#targets = root.findall(f"./{pf}Group[@Comment='{heading}']/{pf}{enumitem}")
#for target in targets:
	# print(target.attrib)  # Dictionary of the Name we want
#	for key, value in target.items():
#		if key == "NameSpace" and value == "Standard":
			#print("NS Key {} -> NS Value {}".format(key, value))
#			pass
#		else:
#			print("Key {} -> Value {}".format(key, value))
#			pass
#targets = root.findall("./{}Group/{}{}/[{}Visibility='Guru']".format(pf, pf, targetsearchlocation, pf, pf))




# print('found {} in {} -> {}'.format(targetsearch, group.tag, group.attrib))
# for group_comment, feature in group.attrib.items():
#	if feature == targetsearch:
#		print('found {} in {} -> {}'.format(targetsearch, group.tag, group.attrib))
# print("gc is {}".format(group_comment))
# print("f is {}".format(feature))
# if targetsearchlocation is not None:
#	for upgroup in root.findall("./{}Group/{}Category='{}')".format(pf, pf, targetsearch)):
#		print('found {} in {} -> {}'.format(targetsearch, upgroup.tag, upgroup.attrib))

# for group in root.findall("./{}Group/{}Enumeration/[{}Visibility='Beginner']".format(pf, pf, pf)):
#	print('{} -> {}'.format(group.tag, group.attrib))


# for group in root.findall("./{}Group/{}Enumeration/{}Visibility".format(pf, pf, pf)):
#	print('{} -> {}'.format(group.tag, group.attrib))
#	for comment, camproperty in group.attrib.items():
#	#	if camproperty == "DeviceControl":
#		print("comment -> /n".format(comment))
#		print("camproperty -> /n".format(camproperty))


# for group in root.iter(pf+'RegisterDescription'):
# print(group.tag)


# for node in root.iter('RegisterDescription'):
#    print(node)
#    print(node.tag, node.attrib)

# print("Done")
