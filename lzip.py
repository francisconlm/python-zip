import struct, getopt, sys

charsLidos=[]

# open and reads file
with open(sys.argv[1], "rb") as inFile:
    linhas = inFile.readlines() # all lines
    for i in range(len(linhas)):
        string = linhas[i]
        for i in range(len(string)):
            char = string[i]
            tuplo = struct.unpack("c",char)
            charsLidos.append(tuplo[0])
            
novaLista1 = ''.join(charsLidos)
novaLista = novaLista1.split("\n")
novaLista.pop()
volumeProc = novaLista.pop()
tempoDemo = novaLista.pop()
dataProc = novaLista.pop()
print "Inicio da execucao da compressao/descompressao: " + str(dataProc)
seconds=(int(tempoDemo)/1000)%60
minutes=(int(tempoDemo)/(1000*60))%60
hours=(int(tempoDemo)/(1000*60*60))%24
print "Duracao da execucao: " + str(hours) + ":" + str(minutes) + ":" + str(seconds) + ":" + str(tempoDemo[-3:])
tupList = []
for p in novaLista:
    (a,b,c,d) = eval(p)
    tupList.append((a,b,c,d))
sortedList = sorted(tupList, key=lambda x: x[0])
procList= []
for p in sortedList:
    procList.append(p[0])
procsRed = reduce(lambda r, x: r + [x] if x not in r else r, procList, [])
for p in procsRed:
    bytesProc = []
    listaProcFilt = filter(lambda x: x[0] == p, sortedList)
    print "Processo: " + str(p)
    for (a,b,c,d) in listaProcFilt:
        Pseconds=(int(d)/1000)%60
        Pminutes=(int(d)/(1000*60))%60
        Phours=(int(d)/(1000*60*60))%24
        print "  Ficheiro processado: " + str(b)
        print "    tempo de compressao/descompressao: " + str(Phours) + ":" + str(Pminutes) + ":" + str(Pseconds) + ":" + str(str(d)[-3:])
        print "    dimensao do ficheiro depois de comprimido/descomprimido: " + str(c)+ " bytes"
        bytesProc.append(c)
    print "  Volume total de dados escritos em ficheiros: " + str(sum(bytesProc)) + " bytes"
print "Volume total de dados escritos em todos os ficheiros: " + str(volumeProc) + " bytes"
