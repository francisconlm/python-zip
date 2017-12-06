import sys, getopt, os, zipfile, time
from multiprocessing import Process, Array, Semaphore, Value
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
        return
    
    fichArgs = []
    if args == []:
        print "Insert File Names: (CTRL + D to Finish)"
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
                break
            
    elif fullCheck == 0: # -t compress all files even if one does not exist
        for ficheiro in fichArgs:
            if os.path.isfile(ficheiro):
                fichList.append(ficheiro)
    
    tamanhoLista = len(fichList)
    listaPartilhada = Array(c_char_p,tamanhoLista)
    
    for p in range(tamanhoLista):
        listaPartilhada[p] = fichList[p]

    
    intPartilhado = Value(c_int, -1)
    
    vazio = Semaphore(1)
    pid = Array(c_int,procs)
    
   
    for i in range(procs):
        pid[i] = os.fork()
        if pid[i] == 0:
            while (intPartilhado.value < len(listaPartilhada)-1):
                vazio.acquire()
                intPartilhado.value += 1
                fichTemp = listaPartilhada[intPartilhado.value]
                vazio.release()
                if comprBool == 0:
                    #print "process number " + str(os.getpid()) + " will decompress " + fichTemp
                    #time.sleep(0.1)
                    decompress(fichTemp)
                elif comprBool == 1:
                    #print "process number " + str(os.getpid()) + " will compress " + fichTemp
                    #time.sleep(0.1)
                    compress(fichTemp)
            return
            
    for i in range(procs):
        os.wait()
    print "Numero de ficheiros processados: " + str(intPartilhado.value+1)
    

if __name__ == "__main__":
    main(sys.argv[1:])
