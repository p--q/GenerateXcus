#!/opt/libreoffice5.4/program/python
# -*- coding: utf-8 -*-
import os, glob
from xml.etree import ElementTree
def main():
	pwd = os.path.dirname(os.path.abspath(__file__))  # このスクリプトのあるフォルダのパスを取得。
	outfolder = os.path.join(pwd, "ini", "template")  # 出力先フォルダのパスの取得。
	if not os.path.exists(outfolder):  # 出力先フォルダが存在しない時。
		os.makedirs(outfolder)  # 出力先フォルダを作成。	
	xcsfolder = os.path.join(pwd, "xml")  # ソースフォルダのパスの取得。
	os.chdir(xcsfolder)  # xmlファイルのあるフォルダに移動。
	ns = {"oor": "http://openoffice.org/2001/registry", "xs": "http://www.w3.org/2001/XMLSchema", "xsi": "http://www.w3.org/2001/XMLSchema-instance", "xml": "http://www.w3.org/XML/1998/namespace"}  # 出てくる名前空間すべて。このスクリプトで使うのはキーのみ。
	nskeys = {"{}:".format(i): "{}--".format(i) for i in ns.keys()}  # キー: 置換前の名前空間のキー、値: 置換後の名前空間のキー。
	for i in glob.iglob("*.xml"):
		with open(i, encoding="utf-8") as f:
			s = f.read()  # ファイルの文字列を取得する。
		for k, v in nskeys.items():  # 名前空間のキーについて。
			s = s.replace(k, v)  # 名前空間の処理は面倒なので一時的に名前空間の接頭辞を置換して、名前空間を無効にする。		
		schema = ElementTree.XML(s)  # ルートノードを取得する。
		parentmap = {c:p for p in schema.iter() for c in p}  # キー: ノード, 値: 親ノード、の辞書。
		lines = ["# {}.xcu".format(schema.get("oor--name"))]  # 出力する行のリスト。
		lines.append("# The path prefixed with '++' in section must be changed to user defined name.")
		lines.append("# The [DEFAULT](case sensitive) section has special meaning in configparser.")
		lines.append("")
		nodeToini = nodeToiniCreator(lines, parentmap)
		nodeToini(schema)
		s = "\n".join(lines)
		for k, v in nskeys.items():  # 名前空間の接頭辞を元に戻す。
			s = s.replace(v, k)			
		print(s)	
		print("\n\n")
		filename = ".".join([i.rsplit(".", 1)[0], "ini"])
		with open(os.path.join(outfolder, filename), "w", encoding="utf-8") as f:
			f.write(s)  			
def nodeToiniCreator(lines, parentmap):
	steps = []
	nodetype = ""
	locales = "en-US", "ja-JP",
	def nodeToini(node):
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
				lines.append("# node-type={}".format(subnodetype))
				lines.append("[{}]".format("/".join([*steps, "++{}".format(subnodetype)])))
				return
			else:
				nodetype = node.get("oor--node-type")
				lines.append("")
		elif tag=="group":
			if parentmap[node].tag=="set":
				steps.append("".join(["++", name]))	
				lines.append("# node-type={}".format(nodetype))
				lines.append("[{}]".format("/".join(steps)))
		elif tag=="prop":
			if not steps:  # セットノードが上にないpropノードはセクションがないので/セクションを付ける。
				steps.append("/")	
			proptype = node.get("oor--type") or ""
			nillable = 'nonnillable' if node.get("oor--nillable")=="false" else "" 
			localized = 'localizable' if node.get("oor--localized")=="true" else "" 
			comment = proptype, nillable, localized
			if any(comment):
				lines.append(" ".join(["#", *comment]))		
			txt = str(node[0].text) if len(node) else ""  # 子要素(valueノード)に整数が入っていると整数型になるのでテキスト型にする。<value/>のときはNoneを返す。	
			if localized:
				[lines.append("{} {}= {} ".format(name, locale, txt)) for locale in locales]	
			else:
				lines.append(" ".join([name, "=", txt]))	
			return	
		elif tag=="node-ref":
			subnodetype = node.get("oor--node-type")
			lines.append("# node-type={}".format(subnodetype))			
			lines.append("[{}]".format("/".join([*steps, name])))
		for child in node:
			nodeToini(child)	
		else:
			steps.clear()	
	return nodeToini
if __name__ == "__main__":  # オートメーションで実行するとき
	main()