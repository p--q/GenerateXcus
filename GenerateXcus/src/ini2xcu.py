#!/opt/libreoffice5.4/program/python
# -*- coding: utf-8 -*-
import os, glob
# from xml.etree import ElementTree
from configparser import ConfigParser
def main():
	pwd = os.path.dirname(os.path.abspath(__file__))  # このスクリプトのあるフォルダのパスを取得。
	outfolder = os.path.join(pwd, "xcu")  # 出力先フォルダのパスの取得。
	if not os.path.exists(outfolder):  # 出力先フォルダが存在しない時。
		os.makedirs(outfolder)  # 出力先フォルダを作成。	
	inifolder = os.path.join(pwd, "ini")  # ソースフォルダのパスの取得。
	os.chdir(inifolder)  # iniファイルのあるフォルダに移動。
	for i in glob.iglob("*.ini"):
		config = ConfigParser()
		config.read(i)
		
		
		
		for k, v in config.items():
			print("key: {}, val: {}".format(k, v))
		
		
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