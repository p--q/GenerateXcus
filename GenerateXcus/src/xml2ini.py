#!/opt/libreoffice5.4/program/python
# -*- coding: utf-8 -*-
import os, glob
from xml.etree import ElementTree
def main():
	pwd = os.path.dirname(os.path.abspath(__file__))  # このスクリプトのあるフォルダのパスを取得。
	outfolder = os.path.join(pwd, "ini")  # 出力先フォルダのパスの取得。
	if not os.path.exists(outfolder):  # 出力先フォルダが存在しない時。
		os.makedirs(outfolder)  # 出力先フォルダを作成。	
	xcsfolder = os.path.join(pwd, "xml")  # ソースフォルダのパスの取得。
	os.chdir(xcsfolder)  # xmlファイルのあるフォルダに移動。
	for i in glob.iglob("*.xml"):
		with open(i, encoding="utf-8") as f:
			s = f.read()  # ファイルの文字列を取得する。
		s = s.replace("oor:", "oor--").replace("xs:", "xs--").replace("xsi:", "xsi--").replace("xml:", "xml--")  # 名前空間の接頭辞を置換する。
		schema = ElementTree.XML(s)  # ルートノードを取得する。
		parentmap = {c:p for p in schema.iter() for c in p}  # キー: ノード, 値: 親ノード、の辞書。
		lines = ["# {}.xcu".format(schema.get("oor--name"))]  # 出力する行のリスト。
		lines.append("# The path prefixed with '+' in section must be changed to user defined name.")
		nodeToini = nodeToiniCreator(lines, parentmap)
		nodeToini(schema)
		s = "\n".join(lines)
		s = s.replace("oor--", "oor:").replace("xs--", "xs:").replace("xsi--", "xsi:").replace("xml--", "xml:")  # 名前空間の接頭辞を元に戻す。
		print(s)	
		print("\n\n")
		filename = ".".join([i.rsplit(".", 1)[0], "ini"])
		with open(os.path.join(outfolder, filename), "w", encoding="utf-8") as f:
			f.write(s)  			
def nodeToiniCreator(lines, parentmap):
	steps = []
	nodetype = ""
	locales = "ja",
	def nodeToini(node):
		nonlocal nodetype
		tag = node.tag
		name = node.get("oor--name")
		if tag=="set":
			if parentmap[node].tag=="set":
				steps.append("".join(["+", name]))	
			else:
				steps.append(name)
			if len(node)==0:
				subnodetype = node.get("oor--node-type")
				lines.append("# node-type={}".format(subnodetype))
				lines.append("[{}]".format("/".join([*steps, "+{}".format(subnodetype)])))
				return
			else:
				nodetype = node.get("oor--node-type")
				lines.append("")
		elif tag=="group":
			if parentmap[node].tag=="set":
				steps.append("".join(["+", name]))	
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
			txt = str(node[0].text) if len(node) else ""  # テキストノードに整数が入っていると整数型になるのでテキスト型にする。
			lines.append(" ".join([name, "=", txt]))	
			if localized:
				for locale in locales:
					lines.append("{} {}= {} ".format(name, locale, txt))	
			return	
		elif tag=="node-ref":
			lines.append("# {}".format(name))	
		for child in node:
			nodeToini(child)	
		else:
			steps.clear()	
	return nodeToini
if __name__ == "__main__":  # オートメーションで実行するとき
	main()