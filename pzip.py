import sys, getopt
import os
import zipfile
from multiprocessing import Process, Array, Semaphore, Value
from ctypes import c_char_p, c_int

def decompress(nomeFich):
        z = zipfile.ZipFile(nomeFich, mode='r')
        z.extractall()
        z.close()
        return
    
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
            procs = int(arg)

    
    if comprBool == -1:
        print "Insert -c (compress) or -d (decompress)"
        return 0
    
    fichArgs = args
    if args == []:
        print "Insert File Names:"
        linha = sys.stdin.readline()
        fichArgs = linha.split()
    
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
    
    vazio = Semaphore(0)
    full = Semaphore(procs)
    pid = Array(c_int,procs)
    
    pai=os.fork()
    if pai == 0:
        for i in range(procs):
            pid[i] = os.fork()
            if pid[i] == 0:
                while True:
                    full.acquire()
                    vazio.release()
                    # print full
                    # print vazio
                    if intPartilhado.value >= len(listaPartilhada)-1:
                        return 0
                    else:
                        intPartilhado.value += 1
                    temp = listaPartilhada[intPartilhado.value]
                    # print temp
                    # print intPartilhado.value
                    vazio.acquire()
                    if comprBool == 0:
                        # print "process number " + str(os.getpid()) + " will decompress " + temp
                        decompress(temp)
                    elif comprBool == 1:
                        # print "process number " + str(os.getpid()) + " will compress " + temp
                        compress(temp)
                    full.release()
                
                
                
    else:
        os.wait()
        print "Numero de ficheiros processados: " + str(intPartilhado.value+1)
    
# buy bitcoin

if __name__ == "__main__":
    main(sys.argv[1:])
        