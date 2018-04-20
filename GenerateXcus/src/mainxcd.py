#!/opt/libreoffice5.4/program/python
# -*- coding: utf-8 -*-
# from xml.etree.ElementTree import ElementTree
from xml.etree import ElementTree
from xml.etree.ElementTree import Element	
def main():
	mainxcd = "/opt/libreoffice5.4/share/registry/main.xcd"
	ns = {"xs": "http://www.w3.org/2001/XMLSchema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
	tree = ElementTree.parse(mainxcd)
	root = tree.getroot()  # root.tag: '{http://openoffice.org/2001/registry}data'
	ns["oor"] = root.tag.split("}")[0][1:]
	createOptionsDialogXCU(root, ns)

	
	
	
def createOptionsDialogXCU(root, ns):
	name = "OptionsDialog"
	xpath = './/oor:component-schema[@oor:name="{}"]'.format(name)
	schema = root.find(xpath, ns)
	getAttrib = getAttribCreator(ns)
	attrib = {"oor:name": name, "oor:package": getAttrib(schema, "package"), "xmlns:oor": ns["oor"], "xmlns:xs": ns["xs"], "xmlns:xsi": ns["xsi"]}
	optionsdialogroot = createElem("oor:component-data", attrib)
	templates = schema[0]
	for componentchild in schema[1]:  # componentノードの子ノードについて。
		if componentchild.tag=="set":
# 			setnode = createElem("node", {"oor:name": getAttrib(componentchild, "name")})
			
			typenode =  getTypeNode(ns, templates, componentchild)
			
			
			pass
	
	

# 	optionsdialogroot = createElem("oor:component-data", attrib={},  **kwargs)
# 	for n in optionsdialog:
# 		if n.tag=="component":
# 			for m in n:
# 				pass
	
	
# 	component = optionsdialog[1]
# 	for child in component:
		
def getTypeNode(ns, templates, setnode):
	nodetype = getAttrib(setnode, "node-type")
	xpath = './*[@oor:name="{}"]'.format(nodetype)
	return templates.find(xpath, ns)	
def getAttribCreator(ns):
	def getAttrib(node, name):  # oorで始まる属性名を変換する。
		return node.get("".join(["{", ns["oor"], "}", name]))
	return getAttrib
def createElem(tag, attrib={},  **kwargs):  # ET.Elementのアトリビュートのtextとtailはkwargsで渡す。		
	txt = kwargs.pop("text", None)
	tail = kwargs.pop("tail", None)
	sub = kwargs.pop("sub", None)  # サブノードにするET.Elementを取得。
	subs = kwargs.pop("subs", None)  # サブノードにするET.Elementのタプルを取得。
	elem = Element(tag, attrib, **kwargs)
	if txt is not None:
		elem.text = txt
	if tail is not None:
		elem.tail = tail	
	if sub is not None:  # ET.Elementが入っていてもsubだけだとFalseになる。
		elem.append(sub)
	if subs is not None:
		elem.extend(subs)	
	return elem	 # Elementオブジェクトを返す。
if __name__ == "__main__":
	main()