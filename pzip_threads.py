import sys, getopt
import os, time, random
import zipfile
from multiprocessing import Array, Semaphore, Value
from threading import Thread
from ctypes import c_char_p, c_int


def decompress(nomeFich):
        z = zipfile.ZipFile(nomeFich, mode='r')
        z.extractall()
        z.close()
    
def compress(nomeFich):
        comprimido = zipfile.ZipFile(nomeFich+'.zip', mode='a')
        comprimido.write(nomeFich)
        
def main(argv):
    
    procs = 1 # number of child processes  
    comprBool = -1 # to compress set to 1. to decompress set to 0
    fullCheck = 0 # case 1 check for all files
    fichArgs = "" # files to iterate
    
    try:
        opts, args = getopt.getopt(argv,"cdp:t",["numprocs="])
    except getopt.GetoptError:
        print 'pzip -c|-d [-p n] [-t] {ficheiros}'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-c':
            comprBool = 1
        elif opt == '-d':
            comprBool = 0
        elif opt == '-t':
            fullCheck = 1
        elif opt in ("-p", "--numprocs"):
            try:
                procs = int(arg)
            except:
                print "Insert whole number"
                return

    if procs < 1:
        print "Insert Int bigger than 0"
        return
    
    if comprBool == -1:
        print "Insert -c (compress) or -d (decompress)"
        return 0
    
    fichArgs = []
    if args == []:
        print "Insert File Names: (CTRL + D to Finish)"
        #linha = sys.stdin.readline()
        #fichArgs = linha.split()
        for line in sys.stdin:
            temp = line
            temp2 = temp.rstrip('\n')
            fichArgs.append(temp2)
    else:
        fichArgs = args
    
    fichList = []
    
    if fullCheck == 1: # -t stop in last existing file
        for ficheiro in fichArgs:
            if os.path.isfile(ficheiro):
                fichList.append(ficheiro)
            else:
                print "O ficheiro '" + ficheiro + "' nao existe."
                break
            
    elif fullCheck == 0: # -t compress all files even if one does not exist
        for ficheiro in fichArgs:
            if os.path.isfile(ficheiro):
                fichList.append(ficheiro)
    
    # print "\n"
    # print "-t: " + str(fullCheck)
    # print "lista de ficheiros: " + str(fichList)
    # print "numero de processo: " + str(procs) 
    # print "\n"
    
    
    tamanhoLista = len(fichList)
    listaPartilhada = Array(c_char_p,tamanhoLista)
    
    for p in range(tamanhoLista):
        listaPartilhada[p] = fichList[p]
    
    # print "lista partilhada copiada: "  
    # for p in listaPartilhada:
    #     print p
    # print "\n"
    
    intPartilhado = Value(c_int, -1)
    
    vazio = Semaphore(1)
    
    def filho():
        while (intPartilhado.value < len(listaPartilhada)-1):
            vazio.acquire()
            intPartilhado.value += 1
            temp = listaPartilhada[intPartilhado.value]
            # print temp
            # print intPartilhado.value
            vazio.release()
            if comprBool == 0:
                # print "process number " + str(os.getpid()) + " will decompress " + temp
                time.sleep(0.1)
                decompress(temp)
            elif comprBool == 1:
                print "process number " + str(os.getpid()) + " will compress " + temp
                time.sleep(0.1)
                compress(temp)
        return 0

    
    filhos=[]
    for i in range(procs):
        newP= Thread(target=filho)
        filhos.append(newP)
        newP.start() 
    for p in filhos: 
        p.join()
                
                

    print "Numero de ficheiros processados: " + str(intPartilhado.value+1)
    


if __name__ == "__main__":
    main(sys.argv[1:])
        
