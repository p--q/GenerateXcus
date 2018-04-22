#!/opt/libreoffice5.4/program/python
# -*- coding: utf-8 -*-
import os, glob, re
from xml.etree import ElementTree
from xml.dom import minidom
def main(): 
	pwd = os.path.dirname(os.path.abspath(__file__))  # このスクリプトのあるフォルダのパスを取得。
	outfolder = os.path.join(pwd, "xml")  # 出力先フォルダのパスの取得。
	if not os.path.exists(outfolder):  # 出力先フォルダが存在しない時。
		os.makedirs(outfolder)  # 出力先フォルダを作成。	
	xcsfolder = os.path.join(pwd, "xcs")  # ソースフォルダのパスの取得。
	os.chdir(xcsfolder)  # xcsファイルのあるフォルダに移動。
	ns = {"oor": "http://openoffice.org/2001/registry", "xs": "http://www.w3.org/2001/XMLSchema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
	ElementTree.register_namespace("oor", ns["oor"])  # 名前空間の設定。出力する時に使用される。
	for i in glob.iglob("*.xcs"):
		tree = ElementTree.parse(i)	
		schema = tree.getroot()  # コンポーネントスキーマノードを取得。
		templates = schema.find("templates", ns)  # テンプレートノードを取得。
		schema.remove(templates)  # テンプレートノードを削除。
		expandTemplates(schema, templates, ns)  # テンプレートノードを展開する。
		filename = ".".join([i.rsplit(".", 1)[0], "xml"])
		writeFile(schema, outfolder, filename, reset=True)  # ファイルを書き出す。				
def expandTemplates(schema, templates, ns):  # テンプレートノードを展開する。
	shematreeBuilder(templates, ns)(schema.find("component", ns))  # コンポーネントノードのテンプレートを展開。
	schema.set("xmlns:xs", ns["xs"])
	schema.set("xmlns:xsi", ns["xsi"])	
def writeFile(schema, outfolder, filename, *, reset=None):  # xcsファイルとして書き出す。			
	x = ElementTree.tostring(schema, encoding="unicode")  # ElementTreeをXML文字列に変換。
	if reset is not None:  # reset引数がある時。
		x = re.sub(r'(?<=>)\s+?(?=<)', "", x)  # 空文字だけのtextとtailを削除してすでにあるインデントをリセットする。
	with open(os.path.join(outfolder, filename), "w", encoding="utf-8") as f:
		f.write(minidom.parseString(x).toprettyxml())  # XMLを整形して書き出す。				
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
	main()