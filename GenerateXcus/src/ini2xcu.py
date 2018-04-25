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
	ns = {"oor": "http://openoffice.org/2001/registry", "xs": "http://www.w3.org/2001/XMLSchema", "xsi": "http://www.w3.org/2001/XMLSchema-instance", "xml": "http://www.w3.org/XML/1998/namespace"}  # 出てくる名前空間すべて。
	defaultns = "xml", "html", "rdf", "wsdl", "xs", "xsi", "dc"  # ElementTreeのデフォルトの名前空間。tostring()で属性として出力されない。
	nskeys = {"{}:".format(i): "{}--".format(i) for i in ns.keys()}  # キー: 置換前の名前空間のキー、値: 置換後の名前空間のキー。
	[ElementTree.register_namespace(i, ns[i]) for i in ns.keys()]  # 名前空間の設定。名前空間のあるElementTreeを文字列に出力する時にデフォルト以外の名前空間の出力に必要。本当に必要なのはデフォルトの名前空間以外のみ。
	for name, config in inidic.items():
		schemafile = os.path.join(pwd, "xml", "{}.xml".format(name))
		if os.path.exists(schemafile):
			with open(schemafile, encoding="utf-8") as f:
				s = f.read()  # ファイルの文字列を取得する。
		else:
			print("There is no xml file expanding the templates node of the component-schema node.", file=sys.stderr)
			sys.exit()
		s = re.sub(r'(?<=>)\s+?(?=<)', "", s)  # 空文字だけのtextとtailを削除してすでにあるインデントをリセットする。
		for k, v in nskeys.items():  # 名前空間のキーについて。
			s = s.replace(k, v)  # 名前空間の処理は面倒なので一時的に名前空間の接頭辞を置換して、名前空間を無効にする。
		schema = ElementTree.XML(s)  # xcsファイルをElementTreeにしてルートノードを取得する。	
		schema.attrib.pop("xml--lang", None)  # コンポーネントデータノードに渡さない属性があればここで削除しておく。	
		[schema.set("xmlns:{}".format(k), v) for k, v in ns.items()]  # 文字列にした時に名前空間は置換されていて出力されないので属性として追加しておく。本当に必要なのはデフォルトの名前空間以外のみ。
		parentmap = {c:p for p in schema.iter() for c in p}  # コンポーネントスキーマノードの子親ノードの辞書。
		iniToxcu = iniToxcuCreator(config, parentmap)
		iniToxcu(schema)				
		x = ElementTree.tostring(schema, encoding="unicode")  # 処理したコンポーネントスキーマノードのElementTreeをXML文字列に変換。名前空間は置換されているので出力されない。しかしあらかじめ属性として追加しておかないと置換を戻した後にパースできない。
		data = createElem("oor:component-data")  # コンポーネントデータノードのルートを作成。
		for k, v in nskeys.items():  # コンポーネントスキーマノードの名前空間の接頭辞を元に戻す。
			if v in x:  # 元に戻す名前空間の接頭辞がある時。
				x = x.replace(v, k)	
				n = k[:-1]  # 名前空間のキーを取得。
				if n in defaultns:  # ElementTreeのデフォルトの名前空間の時。
					data.set("xmlns:{}".format(n), ns[n])  # 使用している名前空間のみコンポーネントデータノードの属性に追加。
		schema = ElementTree.XML(x)  # 名前空間を設定したXML文字列をElementTreeにする。	
		[data.set(k, v) for k, v in schema.items()]  # コンポーネントスキーマノードのルートの属性をコンポーネントデータノードのルートにコピーする。
		data.extend(i for i in schema[0])  # コンポーネントスキーマノードの子要素(元のcomponentノード）の子要素をコンポーネントデータノードのルートの子要素に追加する。	
		x = ElementTree.tostring(data, encoding="unicode")  # コンポーネントデータノードのElementTreeをXML文字列に変換。
		filename = ".".join([name, "xcu"])
		with open(os.path.join(outfolder, filename), "w", encoding="utf-8") as f:
			f.write(minidom.parseString(x).toprettyxml())  # XMLを整形して書き出す。				
def iniToxcuCreator(config, parentmap):
	
	
	
	
	steps = []
	nodetype = ""
	locales = "en-US", "ja",
	def iniToxcu(node):
		nonlocal nodetype
		tag = node.tag
		name = node.get("oor--name")
		if tag=="set":
			if parentmap[node].tag=="set":
				steps.append("".join(["++", name]))	
			else:
				steps.append(name)
			if len(node)==0:
				subnodetype = node.get("oor--node-type")
# 				lines.append("# node-type={}".format(subnodetype))
# 				lines.append("[{}]".format("/".join([*steps, "++{}".format(subnodetype)])))
				return
			else:
				nodetype = node.get("oor--node-type")
# 				lines.append("")
		elif tag=="group":
			if parentmap[node].tag=="set":
				steps.append("".join(["++", name]))	
# 				lines.append("# node-type={}".format(nodetype))
# 				lines.append("[{}]".format("/".join(steps)))
		elif tag=="prop":
			if not steps:  # セットノードが上にないpropノードはセクションがないので/セクションを付ける。
				steps.append("/")	
			proptype = node.get("oor--type") or ""
			nillable = 'nonnillable' if node.get("oor--nillable")=="false" else "" 
			localized = 'localizable' if node.get("oor--localized")=="true" else "" 
			comment = proptype, nillable, localized
# 			if any(comment):
# 				lines.append(" ".join(["#", *comment]))		
# 			txt = str(node[0].text) if len(node) else ""  # テキストノードに整数が入っていると整数型になるのでテキスト型にする。
# 			lines.append(" ".join([name, "=", txt]))	
# 			if localized:
# 				for locale in locales:
# 					lines.append("{} {}= {} ".format(name, locale, txt))	
			return	
# 		elif tag=="node-ref":
# 			lines.append("# {}".format(name))	
		for child in node:
			iniToxcu(child)	
		else:
			steps.clear()	
	return iniToxcu			
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
if __name__ == "__main__":  # オートメーションで実行するとき
	main()