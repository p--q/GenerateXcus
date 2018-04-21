#!/opt/libreoffice5.4/program/python
# -*- coding: utf-8 -*-
import unohelper
import os, glob
from xml.etree import ElementTree
from xml.dom import minidom
def macro(documentevent=None):  # 引数は文書のイベント駆動用。
	ctx = XSCRIPTCONTEXT.getComponentContext()  # コンポーネントコンテクストの取得。
	smgr = ctx.getServiceManager()  # サービスマネージャーの取得。	
	pathsubstservice = smgr.createInstanceWithContext("com.sun.star.comp.framework.PathSubstitution", ctx)
	fileurl = pathsubstservice.substituteVariables("$(work)/schematrees", True)
	outfolder = os.path.normpath(unohelper.fileUrlToSystemPath(fileurl))
	if not os.path.exists(outfolder):
		os.makedirs(outfolder)
	fileurl = pathsubstservice.substituteVariables("$(inst)/share/registry", True)
	xcdpath = os.path.normpath(unohelper.fileUrlToSystemPath(fileurl))
	os.chdir(xcdpath)
	trees = {} 
	for filename in glob.iglob("*.xcd"):
		trees[filename] = ElementTree.parse(filename)
	ns = {"oor": "http://openoffice.org/2001/registry", "xs": "http://www.w3.org/2001/XMLSchema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
	ElementTree.register_namespace("oor", ns["oor"])  # 名前空間の設定。出力する時に使用される。
	names = "OptionsDialog", "ProtocolHandler", "Addons", "Jobs"
	root = trees["main.xcd"]
	for name in names:
		xpath = './/oor:component-schema[@oor:name="{}"]/templates'.format(name)  # テンプレートノードを取得するためのXPathを取得。
		templates = root.find(xpath, ns)  # テンプレートノードを取得。
		xpath = './/oor:component-schema[@oor:name="{}"]/component'.format(name)  # コンポーネントノードを取得するためのXPathを取得。
		component = root.find(xpath, ns)  # コンポーネントノードを取得。		
		x = expandComponentNode(templates, component, ns)
		with open("{}/{}.xcs".format(outfolder, name), "w", encoding="utf-8") as f:
			f.write(minidom.parseString(x).toprettyxml())
	apps = "Writer", "Calc"
	xpath = './/oor:component-schema[@oor:name="WindowState"]/templates'  # テンプレートノードを取得するためのXPathを取得。
	templates = root.find(xpath, ns)  # テンプレートノードを取得。main.xcdにある。
	for app in apps:
		name = "{}WindowState".format(app)
		root = trees["{}.xcd".format(app.lower())]
		xpath = './/oor:component-schema[@oor:name="{}"]/component'.format(name)  # コンポーネントノードを取得するためのXPathを取得。
		component = root.find(xpath, ns)  # コンポーネントノードを取得。		
		x = expandComponentNode(templates, component, ns)
		with open("{}/{}.xcs".format(outfolder, name), "w", encoding="utf-8") as f:
			f.write(minidom.parseString(x).toprettyxml())
def expandComponentNode(templates, component, ns):
	shematreeBuilder(templates, ns)(component)
	component.set("xmlns:xs", ns["xs"])
	component.set("xmlns:xsi", ns["xsi"])	
	return ElementTree.tostring(component, encoding="unicode")
def shematreeBuilder(templates, ns):
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
if __name__ == "__main__":  # オートメーションで実行するとき
	def automation():  # オートメーションのためにglobalに出すのはこの関数のみにする。
		import officehelper
		from functools import wraps
		import sys
		from com.sun.star.beans import PropertyValue
		from com.sun.star.script.provider import XScriptContext  
		def connectOffice(func):  # funcの前後でOffice接続の処理
			@wraps(func)
			def wrapper():  # LibreOfficeをバックグラウンドで起動してコンポーネントテクストとサービスマネジャーを取得する。
				try:
					ctx = officehelper.bootstrap()  # コンポーネントコンテクストの取得。
				except:
					print("Could not establish a connection with a running office.", file=sys.stderr)
					sys.exit()
				print("Connected to a running office ...")
				smgr = ctx.getServiceManager()  # サービスマネジャーの取得。
				print("Using {} {}".format(*_getLOVersion(ctx, smgr)))  # LibreOfficeのバージョンを出力。
				return func(ctx, smgr)  # 引数の関数の実行。
			def _getLOVersion(ctx, smgr):  # LibreOfficeの名前とバージョンを返す。
				cp = smgr.createInstanceWithContext('com.sun.star.configuration.ConfigurationProvider', ctx)
				node = PropertyValue(Name = 'nodepath', Value = 'org.openoffice.Setup/Product' )  # share/registry/main.xcd内のノードパス。
				ca = cp.createInstanceWithArguments('com.sun.star.configuration.ConfigurationAccess', (node,))
				return ca.getPropertyValues(('ooName', 'ooSetupVersion'))  # LibreOfficeの名前とバージョンをタプルで返す。
			return wrapper
		@connectOffice  # createXSCRIPTCONTEXTの引数にctxとsmgrを渡すデコレータ。
		def createXSCRIPTCONTEXT(ctx, smgr):  # XSCRIPTCONTEXTを生成。
			class ScriptContext(unohelper.Base, XScriptContext):
				def __init__(self, ctx):
					self.ctx = ctx
				def getComponentContext(self):
					return self.ctx
				def getDesktop(self):
					return ctx.getByName('/singletons/com.sun.star.frame.theDesktop')  # com.sun.star.frame.Desktopはdeprecatedになっている。
				def getDocument(self):
					return self.getDesktop().getCurrentComponent()
			return ScriptContext(ctx)  
		XSCRIPTCONTEXT = createXSCRIPTCONTEXT()  # XSCRIPTCONTEXTの取得。
		doc = XSCRIPTCONTEXT.getDocument()  # 現在開いているドキュメントを取得。
# 		doctype = "scalc", "com.sun.star.sheet.SpreadsheetDocument"  # Calcドキュメントを開くとき。
		doctype = "swriter", "com.sun.star.text.TextDocument"  # Writerドキュメントを開くとき。
		if (doc is None) or (not doc.supportsService(doctype[1])):  # ドキュメントが取得できなかった時またはCalcドキュメントではない時
			XSCRIPTCONTEXT.getDesktop().loadComponentFromURL("private:factory/{}".format(doctype[0]), "_blank", 0, ())  # ドキュメントを開く。ここでdocに代入してもドキュメントが開く前にmacro()が呼ばれてしまう。
		flg = True
		while flg:
			doc = XSCRIPTCONTEXT.getDocument()  # 現在開いているドキュメントを取得。
			if doc is not None:
				flg = (not doc.supportsService(doctype[1]))  # ドキュメントタイプが確認できたらwhileを抜ける。
		return XSCRIPTCONTEXT
	XSCRIPTCONTEXT = automation()  # XSCRIPTCONTEXTを取得。 
	macro()  # マクロの実行。