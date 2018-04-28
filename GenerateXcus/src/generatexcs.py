#!/opt/libreoffice5.4/program/python
# -*- coding: utf-8 -*-
import unohelper
import os, glob, re
from xml.etree import ElementTree
from xml.dom import minidom
def macro(documentevent=None):  # 引数は文書のイベント駆動用。
	modulepath = __file__ 
	filepath = unohelper.fileUrlToSystemPath(modulepath) if modulepath.startswith("file://") else modulepath # オートメーションの時__file__はシステムパスだが、マクロセレクターから実行するとfileurlが返ってくる。
	pwd = os.path.dirname(os.path.abspath(filepath))  # このスクリプトのあるフォルダのパスを取得。
	outfolder = os.path.join(pwd, "xcs")  # 出力先フォルダのパスの取得。
	if not os.path.exists(outfolder):  # 出力先フォルダが存在しない時。
		os.makedirs(outfolder)  # 出力先フォルダを作成。	
	ctx = XSCRIPTCONTEXT.getComponentContext()  # コンポーネントコンテクストの取得。
	smgr = ctx.getServiceManager()  # サービスマネージャーの取得。	
	pathsubstservice = smgr.createInstanceWithContext("com.sun.star.comp.framework.PathSubstitution", ctx)
	fileurl = pathsubstservice.substituteVariables("$(inst)/share/registry", True)  # xcdファイルのあるフォルダのfileurlを取得。
	xcdpath = os.path.normpath(unohelper.fileUrlToSystemPath(fileurl))  # xcdファイルのあるフォルダのパスを出力。
	os.chdir(xcdpath)  # xcdファイルのあるフォルダに移動。
	trees = {i:ElementTree.parse(i) for i in glob.iglob("*.xcd")}  # キー:xcdファイル名、値: 各ファイルのElementTreeオブジェクト。使用するのはmain.xcdとwriter.xcd、calc.xcdだけだが面倒なのですべてのxcdファイルについてElementTreeを作成している。
	ns = {"oor": "http://openoffice.org/2001/registry", "xs": "http://www.w3.org/2001/XMLSchema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
	ElementTree.register_namespace("oor", ns["oor"])  # 名前空間の設定。出力する時に使用される。
	names = "OptionsDialog", "ProtocolHandler", "Addons", "Jobs"  # main.xcdにテンプレートノードもコンポーネントノードもあるコンポーネントスキーマノード名。
	for name in names:
		xpath = './/oor:component-schema[@oor:name="{}"]'.format(name)  # コンポーネントスキーマノードを取得するためのXPath。
		schema = trees["main.xcd"].find(xpath, ns)  # コンポーネントスキーマノードを取得。
		writeXCS(schema, outfolder, name, ns)
	apps = "Writer", "Calc"  # WindowState.xcuを作成するアプリ名。
	xpath = './/oor:component-schema[@oor:name="WindowState"]/templates'  # テンプレートノードを取得するためのXPathを取得。
	templates = trees["main.xcd"].find(xpath, ns)  # テンプレートノードを取得。main.xcdにある。
	for app in apps:
		name = "{}WindowState".format(app)
		tree = trees["{}.xcd".format(app.lower())]  # writer.xcd、calc.xcdのElementTreeを取得。
		xpath = './/oor:component-schema[@oor:name="{}"]'.format(name)  # コンポーネントスキーマノードを取得するためのXPathを取得。
		schema = tree.find(xpath, ns)  # コンポーネントスキーマノードを取得。
		schema.remove(schema.find("templates", ns))  # 既存のテンプレートノードを削除。
		xpath = './component//*[@oor:component]'.format(name)
		for n in schema.iterfind(xpath, ns):
			n.attrib.pop("{{{}}}component".format(ns["oor"]))
		schema.insert(0, templates)  # main.xcdにあったtemplatesノードを挿入する。
		writeXCS(schema, outfolder, name, ns)  # xcsファイルとして書き出す。		
def writeXCS(schema, outfolder, name, ns):
	schema.set("xmlns:xs", ns["xs"])
	schema.set("xmlns:xsi", ns["xsi"])	
	filename = os.path.join(outfolder, "{}.xcs".format(name))
	writeFile(schema, outfolder, filename)	
def writeFile(schema, outfolder, filename, *, reset=None):  # xcsファイルとして書き出す。			
	x = ElementTree.tostring(schema, encoding="unicode")  # ElementTreeをXML文字列に変換。
	if reset is not None:  # reset引数がある時。
		x = re.sub(r'(?<=>)\s+?(?=<)', "", x)  # 空文字だけのtextとtailを削除してすでにあるインデントをリセットする。
	with open(os.path.join(outfolder, filename), "w", encoding="utf-8") as f:
		f.write(minidom.parseString(x).toprettyxml())  # XMLを整形して書き出す。						
g_exportedScripts = macro, #マクロセレクターに限定表示させる関数をタプルで指定。
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
	