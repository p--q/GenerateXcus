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
	steps = []  # パスの要素。
	nodetype = ""
	locales = "en-US", "ja-JP",
	def nodeToini(node):
		nonlocal nodetype
		tag = node.tag  # タグ名を取得。
		name = node.get("oor--name")  # oor:nameを取得。
		if tag=="set":  # セットノードの時。
			step = "".join(["++", name]) if parentmap[node].tag=="set" else name  # セットノードの子要素のoor:nameはユーザー定義になる。
			steps.append(step)  # ノードのoor:nameをパスの要素に追加する。
			if len(node)==0:  # 子要素がないとき。つまりセットノードの再帰のとき。
				subnodetype = node.get("oor--node-type")  # 子要素になるノードタイプを取得。
				lines.append("# node-type={}".format(subnodetype))  # ノードタイプをコメントに出力。
				lines.append("[{}]".format("/".join([*steps, "++{}".format(subnodetype)])))  # sectionを出力。
				return  # 子要素はないのでここで抜ける。
			else:
				nodetype = node.get("oor--node-type")  # ノードタイプをクロージャに取得。
				lines.append("")  # 空行を挿入。
		elif tag=="group":  # グループノードの時。
			if parentmap[node].tag=="set":  # 親ノードがセットノードの時。
				steps.append("".join(["++", name]))	 # セットノードの子要素のoor:nameはユーザー定義になる。
				lines.append("# node-type={}".format(nodetype))  # ノードタイプをコメントに出力。
				lines.append("[{}]".format("/".join(steps)))  # sectionを出力。
			else:
				steps.append(name)  # ノードのoor:nameをパスの要素に追加する。
		elif tag=="prop":  # propノードの時。
			if not steps:  # セクションにするパスの要素がないとき、[/]セクションにする。
				steps.append("/")	
			proptype = node.get("oor--type") or ""  # propの型を取得。
			nillable = 'nonnillable' if node.get("oor--nillable")=="false" else ""  # oor:nillable属性を取得。
			localized = 'localizable' if node.get("oor--localized")=="true" else ""   # oor:localized属性を取得。
			comment = proptype, nillable, localized
			if any(comment):  # oor:type、oor:nillable、oor:localizedのいずれかの属性があるとき。
				lines.append(" ".join(["#", *comment]))  # コメントに出力。
			txt = str(node[0].text) if len(node) else ""  # 子要素(valueノード)に整数が入っていると整数型になるのでテキスト型にする。<value/>のときはNoneを返す。	
			if localized:  # oor:localized=="true"のとき。
				[lines.append("{} {}= {} ".format(name, locale, txt)) for locale in locales]	
			else:
				lines.append(" ".join([name, "=", txt]))	
			return	
		elif tag=="node-ref":  # node-refノードの時。
			step = "".join(["++", name]) if parentmap[node].tag=="set" else name  # セットノードの子要素のoor:nameはユーザー定義になる。
			steps.append(step)  # ノードのoor:nameをパスの要素に追加する。			
			subnodetype = node.get("oor--node-type")
			lines.append("# node-type={}".format(subnodetype))			
			lines.append("[{}]".format("/".join(steps)))
		for child in node:  # 子要素について再帰。
			nodeToini(child)	
		else:
			steps.clear()  # すべての子要素について調べたらパスの要素をクリアする。	
	return nodeToini
if __name__ == "__main__":  # オートメーションで実行するとき
	main()