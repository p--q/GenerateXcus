#!/opt/libreoffice5.4/program/python
# -*- coding: utf-8 -*-
from xml.etree import ElementTree
from xml.etree.ElementTree import Element	
from xml.dom import minidom
def main():
	mainxcd = "/opt/libreoffice5.4/share/registry/main.xcd"
	ns = {"xs": "http://www.w3.org/2001/XMLSchema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
	tree = ElementTree.parse(mainxcd)
	root = tree.getroot()  # root.tag: '{http://openoffice.org/2001/registry}data'
	ns["oor"] = root.tag.split("}")[0][1:]  # oorのuriを名前空間の辞書に取得。
	ElementTree.register_namespace("oor", ns["oor"])  # 名前空間の設定。出力する時に使用される。
	
	
# 	name = "OptionsDialog"  # OptionsDialog.xcu
# 	name = "ProtocolHandler"  # ProtocolHandler.xcu
# 	name = "Addons"  # Addons.xcu
	name = "Jobs"  # Jobs.xcu
	xpath = './/oor:component-schema[@oor:name="{}"]'.format(name)  # コンポーネントスキーマノードを取得するためのXPathを取得。
	schema = root.find(xpath, ns)  # コンポーネントスキーマノードを取得。
	buildSchemaTree = shematreeBuilder(schema, ns)
	component = schema.find('./component')  # コンポーネントノードを取得。
	buildSchemaTree(component)
	component.set("xmlns:xs", ns["xs"])
	component.set("xmlns:xsi", ns["xsi"])
	printTree(component)
def shematreeBuilder(schemanode, ns):
	templates = schemanode.find('./templates')  # テンプレートノードを取得。
	parentmap = {}  # キー: 子ノード、値: 親ノード、の辞書。再帰をチェックするため。
	def buildSchemaTree(node):  # component-schemaノードのtempaltesをcomponentに展開する。
		tag = node.tag  # タグを取得。
		nodetype = node.get("{{{}}}node-type".format(ns["oor"]))  # node-type属性があれば取得。
		if tag in ("group", "component", "prop"):  # グループノードの時。valueノードは子要素がないはず。
			for child in node:  # 各子ノードについて。
				parentmap[child] = node
				buildSchemaTree(child)  # 子ノードについて調べる。
		elif nodetype is not None:  # node-type属性があるノードの時。
			typenode = templates.find('./*[@oor:name="{}"]'.format(nodetype), ns)  # templatesノードからnode-typeを取得。		
			c = node
			while c in parentmap:  # 親ノードがある間。
				if c==typenode:  # 既出のtype-nodeの時。
					break  # それ以上深くは探索しない。				
				c = parentmap[c]  # 親ノードを取得。
			else:  # type-nodeが既出でない時のみ。
				if tag=="set":  # セットノードの時。
					parentmap[typenode] = node
					node.append(typenode)  # type-nodeを追加。
					buildSchemaTree(typenode)  # type-nodeについて調べる。		
				elif tag=="node-ref":  # node-refノードの時。
					for subnode in typenode:  # node-typeノードの各サブノードのついて。
						parentmap[subnode] = node
						node.append(subnode)  # サブノードを追加。
						buildSchemaTree(subnode)  # サブノードについて調べる。
	return buildSchemaTree




# def createSchemaTree(ns, templates, node):  # component-schemaノードのtempaltesをcomponentに展開する。
# 	tag = node.tag  # タグを取得。
# 	nodetype = node.get("{{{}}}node-type".format(ns["oor"]))  # node-type属性があれば取得。
# 	if tag in ("group", "component", "prop"):  # グループノードの時。
# 		for child in node:  # 各子ノードについて。
# 			createSchemaTree(ns, templates, child)  # 子ノードについて調べる。		
# 	elif nodetype is not None:  # node-type属性があるノードの時。
# 		typenode = templates.find('./*[@oor:name="{}"]'.format(nodetype), ns)  # templatesノードからnode-typeを取得。		
# # 		if node==typenode:  # MenuItemのときなど再帰的なノードのときはそこで探索をやめる。
# # 			pass		
# 		if tag=="set":  # セットノードの時。
# 			node.append(typenode)  # type-nodeを追加。
# 			createSchemaTree(ns, templates, typenode)  # type-nodeについて調べる。		
# 		elif tag=="node-ref":  # node-refノードの時。
# 			for subnode in typenode:  # node-typeノードの各サブノードのついて。
# 				child.append(subnode)  # サブノードを追加。
# 				createSchemaTree(ns, templates, subnode)  # サブノードについて調べる。	
	
	
	
# 	for child in node:  # 各子ノードについて。
# 		tag = child.tag  # タグを取得。
# 		nodetype = child.get("{{{}}}node-type".format(ns["oor"]))  # node-type属性があれば取得。
# 		if tag=="group":  # グループノードの時。
# 			createSchemaTree(ns, templates, child)  # 子ノードについて調べる。		
# 		elif nodetype is not None:  # node-type属性がある時。
# 			typenode = templates.find('./*[@oor:name="{}"]'.format(nodetype), ns)  # templatesノードからnode-typeを取得。		
# 			if node==typenode:  # MenuItemのときなど再帰的なノードのときはそこで探索をやめる。
# 				pass
# 			elif tag=="set":  # セットノードの時。
# 				child.append(typenode)  # type-nodeを追加。
# 				createSchemaTree(ns, templates, typenode)  # type-nodeについて調べる。	
# 			elif tag=="node-ref":  # node-refノードの時。
# 				for subnode in typenode:  # node-typeノードの各サブノードのついて。
# 					child.append(subnode)  # サブノードを追加。
# 					createSchemaTree(ns, templates, subnode)  # サブノードについて調べる。	
	


	
	
	
def printTree(node):	
	x = ElementTree.tostring(node, encoding="unicode")
	print(minidom.parseString(x).toprettyxml())
	
# 	print(ElementTree.tostring(schema, encoding="unicode"))
	
	
# 	createOptionsDialogXCU(root, ns)





	
	
	
# def createOptionsDialogXCU(root, ns):
# 	name = "OptionsDialog"
# 	xpath = './/oor:component-schema[@oor:name="{}"]'.format(name)
# 	schema = root.find(xpath, ns)
# 	getAttrib = getAttribCreator(ns)
# 	attrib = {"oor:name": name, "oor:package": getAttrib(schema, "package"), "xmlns:oor": ns["oor"], "xmlns:xs": ns["xs"], "xmlns:xsi": ns["xsi"]}
# 	optionsdialogroot = createElem("oor:component-data", attrib)
# 	templates = schema[0]
# 	for componentchild in schema[1]:  # componentノードの子ノードについて。
# 		if componentchild.tag=="set":
# # 			setnode = createElem("node", {"oor:name": getAttrib(componentchild, "name")})
# 			
# 			typenode =  getTypeNode(ns, templates, componentchild)
# 			
# 			
# 			pass
	
	

# 	optionsdialogroot = createElem("oor:component-data", attrib={},  **kwargs)
# 	for n in optionsdialog:
# 		if n.tag=="component":
# 			for m in n:
# 				pass
	
	
# 	component = optionsdialog[1]
# 	for child in component:
		
# def getTypeNode(ns, templates, setnode):
# 	nodetype = getAttrib(setnode, "node-type")
# 	xpath = './*[@oor:name="{}"]'.format(nodetype)
# 	return templates.find(xpath, ns)	
# def getAttribCreator(ns):
# 	def getAttrib(node, name):  # oorで始まる属性名を変換する。
# 		return node.get("".join(["{", ns["oor"], "}", name]))
# 	return getAttrib


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