#!/opt/libreoffice5.4/program/python
# -*- coding: utf-8 -*-
import os, glob, sys, re
from copy import deepcopy
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
	inidic = {i.rsplit(".", 1)[0]: createConfigParser(i) for i in glob.iglob("*.ini")}
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
		parentmap = {c:p for p in data.iter() for c in p}  # コンポーネントデータノードの子親ノードの辞書。パースしなおしているので元のparentmapは使えない。
		stack = data.findall(".//node")
		while stack:  # stackを変更しながらループするのwhile文で回す。
			n = stack.pop()
			if not len(n):
				parentmap[n].remove(n)  # 子要素のない<node>要素を削除。
		x = ElementTree.tostring(data, encoding="unicode")  # コンポーネントデータノードのElementTreeをXML文字列に変換。
		filename = ".".join([name, "xcu"])
		with open(os.path.join(outfolder, filename), "w", encoding="utf-8") as f:
			f.write(minidom.parseString(x).toprettyxml())  # XMLを整形して書き出す。
		print("\nxcu files have been created in\n{}".format(outfolder))		
def createConfigParser(filepath):
	config = ConfigParser()
	config.read(filepath)
	return config	
def iniToxcuCreator(config, parentmap):
	locales = "en-US", "ja-JP",
	splitsections = [i.split("/") for i in config.sections() if "/++" not in i]  # セクションを/区切りでリストにする。ユーザー未定義の名前があるセクションは除く。
	steps = []
	xcstags = "set", "group", "node-ref"  # xcuでは存在しないタグのタプル。テンプレートして使用後は削除する。
	recursivetags = *xcstags, "prop", "oor--component-schema", "component"  # これ以外のタグは処理しない。
	removenodes = []  # 削除するノードのリスト。
	def iniToxcu(node):
		tag = node.tag
		if not tag in recursivetags:  # infoやdescタグなどrecursivetags以外のタグは無視する。
			return		
		print("\n[{}]\n<{} {}>".format("/".join(steps), node.tag, " ".join(["{}={}".format(*i) for i in node.items()]).replace("--", ":")))  # 処理したノードを出力。デバッグ用。
		parentnode = node in parentmap and parentmap[node]  # 親ノードがあればそれを取得する。
		if parentnode and parentnode.get("oor--node-type"):  # セットノードの子ノードの時。親ノードのタグはnodeに変更済なのでoor:node-typ属性の有無で判断する。
			parentnode.attrib.pop("oor--node-type", None)  # oor:node-type属性はもう使用しないので削除する。
			parentpath = "/".join(steps)  # 親ノードのパスを取得。
			for splitsection in splitsections:  # すべてのsplitsectionについて。
				if parentpath=="/".join(splitsection[:-1]):  # 親ノードのパスが一致する時。
					steps.append(splitsection[-1])  # stepsに名前を追加。
					newnode = deepcopy(node)  # 新しいノードを取得。
					newnode.tag = "node"
					newnode.set("oor--name", splitsection[-1])
					newnode.set("oor--op", "replace")
					newnode.attrib.pop("oor--node-type", None)  # セットノードとnode-refノードの時のため。	
					if node.get("oor--extensible")=="true":  # extensibleなノードではpropノードを追加する。
						extendPropNode(parentmap, steps, config, newnode, locales)
					parentnode.append(newnode)	
					parentmap.update({c:p for p in newnode.iter() for c in p})  # 新しいノードの子ノードをparentmapに追加。新しいノード自体はすでに処理済なのでキーに追加しなくてよい。	
					recursiveChild(iniToxcu, parentmap, removenodes, steps, newnode)
			else:
				for xcstag in xcstags:  # 使用済のxcsのノードを削除する。親ノードまで削除してしまうと再帰が途切れる（イテレート途中なので)。
					xcsnode = parentnode.find(xcstag)
					xcsnode and parentnode.remove(xcsnode)
			return
		else:  # セットノードの子ノードではない時。
			name = node.get("oor--name")
			if tag in xcstags:							
				steps.append(name)
				node.tag = "node"
				if tag=="node-ref":
					node.attrib.pop("oor--node-type", None)  # セットノードのoor:node-refは子要素で削除する。	
				if node.get("oor--extensible")=="true":
					extendPropNode(parentmap, steps, config, node, locales)			
			elif tag=="prop":  # propノードの時。
				section = "/".join(steps)  # 親ノードのパスを取得。これがセクション名になる。
				if not section in config:
					return
				if node.get("oor--localized")=="true":  # 地域化のとき。
					for locale in locales:  # 各地域について。
						key = " ".join([name, locale])  # 設定値のキーを取得。
						if key in config[section]:  # 設定値のキーがある時。
							value = config[section][key]  # 設定値を取得。
							if value:  # 設定値が空文字でない時。
								value = None if value=="None" else value  # 文字列NoneをNoneにする。
								valuenode = node.find("./value[@xml--lang='{}']".format(locale))  # valueノードを取得。まだ存在しなければNoneが返る。
								if valuenode:  # すでにvalueノードがあるとき。
									if node.get("oor--nillable")=="false" and valuenode.text==value:  # 空値不可でデフォルト値と一致するとき。
										node.remove(valuenode)  # valueノードを削除してデフォルト値に委ねる。
									else:  # デフォルト値がなかったり、デフォルト値を上書きするとき。
										valuenode.text = value  # テキストノードに設定値を代入。
								else:  # valueノードがない時はデフォルト値もないのでvalueノードを作成して追加する。
									newnode = createElem("value", {"xml--lang": locale}, text=value)
									node.append(newnode)  # valueノードがないときは追加。
									parentmap.update({c:p for p in newnode.iter() for c in p})  # 新しいノードの子ノードをparentmapに追加。新しいノード自体はすでに処理済なのでキーに追加しなくてよい。	
				elif name in config[section]:  # 設定値のキーがあるとき。			
					value = config[section][name]  # 設定値を取得。
					if value:  # 設定値が空文字でない時。oor:nillable=trueのときは空文字は入りえず、最低Noneという文字列が返ってくる。
						value = None if value=="None" else value  # 文字列NoneをNoneにする。
						if node.get("oor--nillable")=="false" and len(node) and node[0].text==value:  # 空値不可でデフォルト値と一致するとき。
							removenodes.append(node)  #  ノードを削除してデフォルト値に委ねる。イテレートの途中で削除するとそこでループが終わるのでループ終了後に削除する。
							print("removed")
							return
						else:  # デフォルト値がなかったり、デフォルト値を上書きするとき。
							if len(node):  # すでにvalueノードが存在するとき。
								node[0].text = value  # テキストノードに設定値を代入。
							else:
								newnode = createElem("value", text=value)
								node.append(newnode)  # valueノードがないときは追加。		
								parentmap.update({c:p for p in newnode.iter() for c in p})  # 新しいノードの子ノードをparentmapに追加。新しいノード自体はすでに処理済なのでキーに追加しなくてよい。	
				if len(node):  # valueノードをもつpropノードの時。
					[node.attrib.pop(i, None) for i in ("oor--localized", "oor--nillable")]  # oor:name以外の属性値を削除。oor:typeも不要だがわかりやすいように残しておく。
				else:  # valueノードを持たないpropノードのとき。
					removenodes.append(node)  #  ノードを削除。イテレートの途中で削除するとそこでループが終わるのでループ終了後に削除する。
					print("removed")
					if node.get("oor--nillable")=="false":
						print('The prop node oor:name={} with oor:nillable="false" is not defined.'.format(name), file=sys.stderr)
				return	
			recursiveChild(iniToxcu, parentmap, removenodes, steps, node)
	return iniToxcu
def recursiveChild(iniToxcu, parentmap, removenodes, steps, node):  # 再帰と葉まで来た時の処理。
	for child in node:
		iniToxcu(child)	
	[parentmap[i].remove(i) for i in removenodes]
	removenodes.clear()
	if steps:
		steps.pop()	
def extendPropNode(parentmap, steps, config, node, locales):  # extensibleなノードの時。動作未検証。
	section = "/".join(steps)
	if section in config:
		propnames = config[section].keys()
		for propname in propnames:
			if propname.startswith("xs--"):  # xs:で始まるprop名が追加されたprop。
				keytype, key = propname.split(" ", 1)  # oor:type、設定値のキーを取得。
				newname, *keylocale = key.rsplit(" ", 1)
				if keylocale and keylocale[0] in locales:  # 設定値のキーにlocaleがある時。
					if not node.find('./prop[@oor-name="{}"'.format(newname)):  # すでに同じoor:nameのpropが存在するときはpropnodeを追加しない。
						newnode = createElem("prop", {"oor--name": newname, "oor--type": keytype, "oor--localized": "true"})
						node.append(newnode)
						parentmap.update({c:p for p in newnode.iter() for c in p})  # 新しいノードをparentmapに追加。	
				else:
					newnode = createElem("prop", {"oor--name": newname, "oor--type": keytype})
					node.append(newnode)
					parentmap.update({c:p for p in newnode.iter() for c in p})  # 新しいノードをparentmapに追加。	
				config[section][newname] = config[section][propname]  # configのキーにnewnameを追加してその値をpropnameのものにする。
				config[section].pop(propname, None)  # configのキーからpropnameを消去。
	node.attrib.pop("oor--extensible", None)  	
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