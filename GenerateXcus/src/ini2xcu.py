#!/opt/libreoffice5.4/program/python
# -*- coding: utf-8 -*-
import os, glob, sys, re
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from configparser import ConfigParser
from xml.dom import minidom
def main():
	pwd = os.path.dirname(os.path.abspath(__file__))  # このスクリプトのあるフォルダのパスを取得。
	outfolder = os.path.join(pwd, "xcu")  # 出力先フォルダのパスの取得。
	if not os.path.exists(outfolder):  # 出力先フォルダが存在しない時。
		os.makedirs(outfolder)  # 出力先フォルダを作成。	
	inifolder = os.path.join(pwd, "ini")  # ソースフォルダのパスの取得。
	os.chdir(inifolder)  # iniファイルのあるフォルダに移動。
	inidic = {i.rsplit(".", 1)[0]: ConfigParser().read(i) for i in glob.iglob("*.ini")}
	ns = {"oor": "http://openoffice.org/2001/registry", "xs": "http://www.w3.org/2001/XMLSchema", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
	ElementTree.register_namespace("oor", ns["oor"])  # 名前空間の設定。出力する時に使用される。
	getAttr, delAttr = attrfuncCreator(ns)
	for name, config in inidic.items():
		schemafile = os.path.join(pwd, "xml", "{}.xml".format(name))
		if os.path.exists(schemafile):
			tree = ElementTree.parse(schemafile)	
		else:
			print("There is no xml file expanding the templates node of the component-schema node.", file=sys.stderr)
			sys.exit()
		schema = tree.getroot()
		component = schema.find("component", ns)
		data = createElem("{{{}}}component-data".format(ns["oor"]))
		data.extend([i for i in component])
		parentmap = {c:p for p in data.iter() for c in p}  # キー: ノード, 値: 親ノード、の辞書。
		for n in data.iter():
			tag = n.add
			name = getAttr(n, "name")
			if tag=="set":
				delAttr(n, "node-type") 
				sectionbase = "{} set".format(" ".join(getSetNames(parentmap, n)))
				c = 1
				section = "{}{}".format(sectionbase, c)
				while section in config:
					section = "{}{}".format(sectionbase, c)
		
		
		
					c += 1
				n.tag = "node"

				
	
			
		
		
		[data.set(k, v) for k, v in schema.items() if not "lang" in k]
		data.set("xmlns:xs", ns["xs"])
		data.set("xmlns:xsi", ns["xsi"])		
		filename = ".".join([name, "xcu"])		
		writeFile(data, outfolder, filename, reset=True)  # ファイルを書き出す。	
def getSetNames(parentmap, n):  # ルートからノードnまでのセットノードのname属性のリストを取得する。
	names = []  # ルートまでのセットノードのname属性を入れるリスト。
	c = n
	while c in parentmap:  # 親ノードがある間。
		if c.tag=="set":  # セットノードの時。
			names.append(c.get("name"))
		c = parentmap[c]  # 親ノードについて調べる。	
	return names[::-1]  # ルートノードからの順にして返す。
def attrfuncCreator(ns): 	
	def _nsattr(name):
		return "".join("{", ns["oor"], "}", name)
	def getAttr(n, name):
		return n.get(_nsattr(name))
	def delAttr(n, name):
		return n.attrib.pop(_nsattr(name), None)  # 第2引数を渡すとキーがなくてもエラーが出ない。
	return getAttr, delAttr			
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
def writeFile(schema, outfolder, filename, *, reset=None):  # xcsファイルとして書き出す。			
	x = ElementTree.tostring(schema, encoding="unicode")  # ElementTreeをXML文字列に変換。
	if reset is not None:  # reset引数がある時。
		x = re.sub(r'(?<=>)\s+?(?=<)', "", x)  # 空文字だけのtextとtailを削除してすでにあるインデントをリセットする。
	with open(os.path.join(outfolder, filename), "w", encoding="utf-8") as f:
		f.write(minidom.parseString(x).toprettyxml())  # XMLを整形して書き出す。			


		
		
# 		with open(i, encoding="utf-8") as f:
# 			s = f.read()  # ファイルの文字列を取得する。
# 		s = s.replace("oor:", "").replace("xs:", "").replace("xsi:", "").replace("xml:", "")  # 名前空間の接頭辞をすべて削除する。
# 		schema = ElementTree.XML(s)  # ルートノードを取得する。
# 		parentmap = {c:p for p in schema.iter() for c in p}  # キー: ノード, 値: 親ノード、の辞書。
# 		lines = ["# {}.xcu".format(schema.get("name"))]  # 出力する行のリスト。
# 		nodetype = None  # 前のノードのnode-type属性。
# 		namescashe = []  # ルートまでのセットノードのname属性のリスト。
# 		for n in schema.iter():  # ノードをXMLの上行から順に取得する。
# 			tag = n.tag  # タグを取得。
# 			name = n.get("name")  # name属性の値を取得。
# 			if nodetype is not None:  # 1つ前のノードにnode-type属性がある、つまりsetノードかnode-typeノードの時。
# 				if parentmap[n].tag=="set":  # 親ノードがセットノードの時。
# 					names = getSetNames(parentmap, n)  # ルートからノードnまでのセットノードのname属性のリストを取得する。
# 					r = "" if namescashe and len(names)>len(namescashe) and all(map(lambda x, y: x==y, namescashe, names)) else "\n"  # 階層を深くなった時はセクションの前は改行しない。all([])はTrueになる。
# 					namescashe = names.copy()  # 次に比較するためにnamesをキャッシュしておく。
# 					lines.append("{}{}".format(r, " ".join(["[", *names, "set1 ]"])))  # セットノードname属性はセクションとして出力する。
# 					lines.append("# nodetype={}".format(nodetype))		
# 			if tag=="group":
# 				extensible = True if n.get("extensible")=="true" else False
# 				if extensible:
# 					lines.append("# extensible props {}".format(name))
# 					lines.append("# type name1 = ")
# 				else:
# 					lines.append("{} group name = ".format(name))
# 			elif tag=="prop":
# 				proptype = n.get("type")
# 				proptype = '{}:'.format(proptype) if proptype else ""
# 				nillable = 'nonnillable' if n.get("nillable")=="false" else "" 
# 				localized = 'localizable' if n.get("localized")=="true" else "" 
# 				comment = proptype, nillable, localized
# 				if any(comment):
# 					lines.append(" ".join(["#", *comment]))
# 				txt = str(n[0].text) if len(n) else ""  # テキストノードに整数が入っていると整数型になるのでテキスト型にする。
# 				lines.append(" ".join([name, "=", txt]))
# 			elif tag=="set" and len(n)==0:  # セットノードかつ子ノードがない時。つまり再帰ノードの時。
# 				names = getSetNames(parentmap, n)  # ルートからノードnまでのセットノードのname属性のリストを取得する。
# 				lines.append(" ".join(["[", *names, "set1 ]"]))							
# 				lines.append("# {} node-type={}".format(n.get("name"), n.get("node-type")))	
# 			nodetype = n.get("node-type")  # node-type属性がないときはNoneが入る。
# 		s = "\n".join(lines)
# 		print(s)	
# 		print("\n\n")
# 		filename = ".".join([i.rsplit(".", 1)[0], "ini"])
# 		with open(os.path.join(outfolder, filename), "w", encoding="utf-8") as f:
# 			f.write(s)  	
# def getSetNames(parentmap, n):  # ルートからノードnまでのセットノードのname属性のリストを取得する。
# 	names = []  # ルートまでのセットノードのname属性を入れるリスト。
# 	c = n
# 	while c in parentmap:  # 親ノードがある間。
# 		if c.tag=="set" and c!=n:  # nのname属性以外でセットノードの時。
# 			names.append(c.get("name"))
# 		c = parentmap[c]  # 親ノードについて調べる。	
# 	return names[::-1]  # ルートノードからの順にして返す。
if __name__ == "__main__":  # オートメーションで実行するとき
	main()