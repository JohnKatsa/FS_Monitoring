from random import shuffle

# make letters list [32(SPACE),126(~)]
letters1 = []
for i in range(32,127):
    letters1.append(chr(i))

# keep initial
letters2 = letters1.copy()

# shuffle list
shuffle(letters2)

# export map to file
file = open("mapping.txt","w+")
for i in range(len(letters1)):
    file.write(letters1[i]+"\t"+letters2[i]+"\t\n")
file.close()

# export map to file
file = open("unmapping.txt","w+")
for i in range(len(letters2)):
    file.write(letters2[i]+"\t"+letters1[i]+"\t\n")
file.close()

lettersMap = {}
with open ("mapping.txt", "r") as myfile:
    for line in myfile:
        key = line.split("\t")[0]
        value = line.split("\t")[1]
        lettersMap[key] = value

for item in lettersMap:
    print(item,lettersMap[item])