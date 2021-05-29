from typing import List

file = open('/home/lukas/Downloads/Beispielgedöns/en_fake_train.txt', 'r')

frames = []
verb_list = []
verb_dict = {}
tree_dict = {}
id_text_dict = {}
role_dict = {}

lines = []

# Beispielnummer wählen (1-10)
example_num = 6
correct_example = False

if example_num <=6:
	column_name_map = {0: "id", 1: 'text', 6: "headid", 10: 'frame'}
else:
	column_name_map = {0: "id", 1: 'text', 6: "headid", 9: 'frame'}
column_name_map_inv = {v: k for k, v in column_name_map.items()}

# Zeile für Zeile iterieren
for line in file:
	if line.startswith("#"):
		if line.startswith("# Example"):
			# Prüfe Beispielnummer
			ex_num_read = int(line.split(" ")[2])
			if ex_num_read == example_num:
				print("Start new sentence")
				correct_example = True
			elif ex_num_read < example_num:
				continue
			else:
				break
		elif line.startswith("# text") and correct_example:
			print(line)
	elif line != "\n" and correct_example:
		columns = line.strip().split("\t")
		lines.append(columns)

for line in lines:
	columns = line
	# Frames finden
	if columns[column_name_map_inv["frame"]] != "_":
		verb_list.append(columns[column_name_map_inv["frame"]])
	
	# Tree dict Anlegen
	# tree-id : [Liste abhängiger Wort-IDs]
	column_id_txt = columns[column_name_map_inv["id"]]
	if column_id_txt.isnumeric():
		column_id = int(column_id_txt)
	else:
		continue
	column_tree_id = int(columns[column_name_map_inv["headid"]])
	column_text = columns[column_name_map_inv["headid"]]

	# Baut ein Dictionary aus tree-Abhängigkeiten
	if column_tree_id in tree_dict:
		tree_dict[column_tree_id].append(column_id)
	else:
		tree_dict[column_tree_id] = [column_id]

	# Baut ID-Text-dict
	id_text_dict[column_id] = column_text

	# Baut Dictionaries für Rollen (id : srl)
	role_dict[column_id] = columns[int(column_name_map_inv["frame"])+1 : ]

	# [Frame: hit.01; Roles: [('a Yellowstone wolf', 'ARG1'), ('a car', 'ARG2')], ...]

#	columns = line
for k, v in role_dict.items():
	if any(x != "_" for x in v):
		for idx, sem_rol in enumerate(v):
			if sem_rol != "_" and sem_rol != "V":
				# Wenn davon etwas abhängig ist
				if k in tree_dict:
					#word_id_list = sorted([k] + tree_dict[k])
					word_id_list = sorted([k])
				else:
					word_id_list = [k]
				whole_string = ""
				for word_id in word_id_list:
					whole_string += (id_text_dict[word_id] + " ")
				whole_string = whole_string.rstrip()

				if verb_list[idx] in verb_dict:
					verb_dict[verb_list[idx]].append((whole_string,(sem_rol)))
				else:
					verb_dict[verb_list[idx]] = [(whole_string,sem_rol)]
	

print("tree dict")
print(tree_dict)
print("id-text dict")
print(id_text_dict)
print("id-roles dict")
print(role_dict)
print("Frames")
print(verb_dict)

# Frames finden
# Zeilen finden, die semantische Rollen haben
# Herausfinden, welche Wörter dazu gehören (dict für tree-Spalte anlegen)
# Reihenfolge suchen

file.close()


print(frames)




# Klasse für Frames
class Frame():
    def __init__(self, frame: str, roles : List[str]):
        self.frame = frame
        self.roles = roles


    def __len__(self):
        return len(roles)

    def __repr__(self):
        return "Frame: "+str(self.frame)+"; Roles: "+str(self.roles)