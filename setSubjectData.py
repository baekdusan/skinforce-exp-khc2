import json

targets = [["forearm", "back of hand", "knuckle"],
           ["back of hand", "knuckle", "forearm"],
           ["knuckle", "forearm", "back of hand"]]

scales = [[12, 16, 20],
          [16, 20, 12],
          [20, 12, 16]]

haptics = [[True, False],
           [False, True]]


def openData(n):
    global data
    try:
        with open(f'data{n}.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

def saveData(data, n):
    with open(f'data{n}.json', 'w') as file:
        json.dump(data, file, indent=4)

############## Exp 1 ###############

data = {}
openData(1)
subjectNames = [str(i) for i in range(1, 19)]

idx = 0
for _ in range(2):
    for i in range(3):
        for j in range(3):
            data[subjectNames[idx]] = {
                "progress": 0,
                "haptics": [False],
                "targets": targets[i],
                "scales": scales[j]
            }
            idx += 1
saveData(data, 1)

############### Exp 2 ###############

data = {}
openData(2)

idx = 0
for j in range(3):
    for k in range(2):
        data[subjectNames[idx]] = {
            "progress": 0,
            "haptics": haptics[k],
            "targets": targets[j],
            "scales": [16, 16, 16]
        }
        idx += 1
saveData(data, 2)

####################################