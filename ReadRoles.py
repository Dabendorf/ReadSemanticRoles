from typing import List

file = open('/home/lukas/Downloads/ReadSemanticRoles/en_fake_train.txt', 'r')

frames = []
frame_dict = {}
verb_list = []
verb_dict = {}
tree_dict = {}
id_text_dict = {}
role_dict = {}

# Returns a list of ids of words which are dependent from another word
# sub_root_id: ID of word which is root of that subtree
# ignore_other_frames: Stops recursion when hiting other verb
# -> unset value of a frame is the *direct* role of something 
def dfs_tree(sub_root_id: int, verb_dict, tree_dict, ignore_other_frames = True) -> [int]:
	list_of_word_ids = []

	for sub_id in tree_dict[sub_root_id]:
		if sub_id not in verb_dict or not ignore_other_frames:
			list_of_word_ids.append(sub_id)
			if sub_id in tree_dict:
				list_of_word_ids.extend(dfs_tree(sub_root_id=sub_id, verb_dict=verb_dict, tree_dict=tree_dict, ignore_other_frames=ignore_other_frames))

	return list_of_word_ids

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

	column_frame = column_name_map_inv["frame"]
	column_id_txt = columns[column_name_map_inv["id"]]
	if column_id_txt.isnumeric():
		column_id = int(column_id_txt)
	else:
		continue
	column_tree_id = int(columns[column_name_map_inv["headid"]])
	column_text = columns[column_name_map_inv["text"]]


	# Frames finden
	if columns[column_frame] != "_":
		verb_list.append(columns[column_frame])
		verb_dict[column_id] = columns[column_frame]

	# Baut ein Dictionary aus tree-Abhängigkeiten
	if column_tree_id in tree_dict:
		tree_dict[column_tree_id].append(column_id)
	else:
		tree_dict[column_tree_id] = [column_id]

	# Baut ID-Text-dict
	id_text_dict[column_id] = column_text

	# Baut Dictionaries für Rollen (id : srl)
	role_dict[column_id] = columns[int(column_frame)+1 : ]

	# [Frame: hit.01; Roles: [('a Yellowstone wolf', 'ARG1'), ('a car', 'ARG2')], ...]

# Gehe alle vorhandenen semantischen Rollen durch
# k = ID des Worts, v = semantische Rollen Liste
for k, v in role_dict.items():
	if any(x != "_" for x in v):
		for idx, sem_rol in enumerate(v):
			if sem_rol != "_" and sem_rol != "V":
				# sem_rol = String einer vorhandenen rolle
				# idx = Index in v, oder: Index des Verbs zu welchem Rolle gehört
				# Durchläuft jede Rolle, die kein Verb oder leer ist
				#print("ID Wort: "+str(k))
				#print("Semantische Rollen: "+str(v))
				#print("Semantische Rollen: "+sem_rol)
				#print("Verb-Index: "+str(idx))

				word_id_list = []
				word_id_list.append(k)

				if k in tree_dict:
					sub_ids = tree_dict[k]
					for sub_id in sub_ids:
						if sub_id not in tree_dict:
							word_id_list.append(sub_id)
						else:
							if k in verb_dict:
								word_id_list.append(sub_id)
								word_id_list.extend(dfs_tree(sub_id, verb_dict, tree_dict, ignore_other_frames=False))
							elif sub_id not in verb_dict:
								word_id_list.append(sub_id)
								word_id_list.extend(dfs_tree(sub_id, verb_dict, tree_dict))

				word_id_list = list(set(word_id_list))
				word_id_list.sort()

				whole_string = ""
				for word_id in word_id_list:
					whole_string += (id_text_dict[word_id] + " ")
				whole_string = whole_string.rstrip()

				if verb_list[idx] in frame_dict:
					frame_dict[verb_list[idx]].append((whole_string, (sem_rol)))
				else:
					frame_dict[verb_list[idx]] = [(whole_string, sem_rol)]



"""for k, v in role_dict.items():
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

				if verb_list[idx] in frame_dict:
					frame_dict[verb_list[idx]].append((whole_string,(sem_rol)))
				else:
					frame_dict[verb_list[idx]] = [(whole_string,sem_rol)]"""
	

print("Verb-dict:\t"+str(verb_dict)+"\n")
print("tree dict:\t"+str(tree_dict)+"\n")
print("id-text dict:\t"+str(id_text_dict)+"\n")
print("id-roles dict:\t"+str(role_dict)+"\n")
print("Frames:\t"+str(frame_dict)+"\n")

# Frames finden
# Zeilen finden, die semantische Rollen haben
# Herausfinden, welche Wörter dazu gehören (dict für tree-Spalte anlegen)
# -> Tiefensuche mit Abbruchbedingung bei neuem Frame
# Reihenfolge suchen (sortieren anhand der IDs)

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