import sys, getopt, os, zipfile, time, signal, struct
from datetime import datetime
from multiprocessing import Process, Array, Semaphore, Value
from ctypes import c_char_p, c_int, c_float


def decompress(nomeFich):
    #time.sleep(1)
    z = zipfile.ZipFile(nomeFich, mode='r')
    z.extractall()
    z.close()
    
def compress(nomeFich):
    #time.sleep(1)
    comprimido = zipfile.ZipFile(nomeFich+'.zip', mode='a')
    comprimido.write(nomeFich)
    
def writeToFile(whatToWrite,whereToWrite):
    with open(whereToWrite,"ab") as outFile:
        for char in whatToWrite:
            outFile.write(struct.pack("c",char))


def main(argv):
    dataInicial = datetime.now().strftime("%d %B %Y, %H:%M:%S:%f") 
    procs = 1 # number of child processes  
    comprBool = -1 # to compress set to 1. to decompress set to 0
    fullCheck = 0 # case 1 check for all files
    intervalo = -1 # SIGALRM
    escreverLog = 0 # case 1 write log in file
    ficheiro = " " # file for log
    
    try:
        opts, args = getopt.getopt(argv,"cdp:ta:f:",["numprocs=","numsegs=","namefile="])
    except getopt.GetoptError:
        print "pzip -c|-d [-p n] [-t] [-a n] [-f s] {ficheiros}"
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-c':
            comprBool = 1
        elif opt == '-d':
            comprBool = 0
        elif opt == '-t':
            fullCheck = 1
        elif opt in ("-p", "--numsegs"):
            try:
                procs = int(arg) # number of processes to use
                if procs < 1:
                    print "Insert Int bigger than 0."
                    return
            except:
                print "Insert whole number."
                return
        elif opt in ("-a", "--numprocs"):
            try:
                intervalo = float(arg) # SIGALRM time
                if intervalo <= 0:
                    print "Insert float bigger than 0."
                    return
            except:
                print "Insert float number."
                return
        elif opt in ("-f", "--namefile"):
            try:
                ficheiro = str(arg) # file to write log
                escreverLog = 1
                if os.path.isfile(ficheiro):
                    print "File <" + ficheiro + "> already exists."
                    return
            except:
                print "Insert file name."
                return
    if comprBool == -1:
        print "Insert -c (compress) or -d (decompress)."
        return
    
    fichArgs = [] # list of files to process
    if args == []:
        print "Insert File Names: (CTRL + D to Finish)."
        for line in sys.stdin:
            temp = line
            temp2 = temp.rstrip('\n')
            fichArgs.append(temp2)
    else:
        fichArgs = args
    
    
    intPartilhado = Value(c_int, -1) # critical section Int
    fichProcess = Value(c_int, 0) # number of files processed
    totalFileSize = Value(c_int, 0) # total processed
    finishedList = Array(c_int,procs) # check if all processes finished
    
    for p in range(procs):    
        finishedList[p] == 0

    critSec = Semaphore(1)
    horaInicial = time.time()
    pid = [0]*procs
    for i in range(procs):
        pid[i] = os.fork()
        if pid[i] == 0:
            while (intPartilhado.value+1 < len(fichArgs)): # list of inserted files
                critSec.acquire() # Enters critial zone
                ficheiroNext = fichArgs[((intPartilhado.value)+1)]
                if not os.path.isfile(ficheiroNext): # If Proposed File Does Not Exist
                    if fullCheck == 1: # -t 1 -> stop in last existing file
                        critSec.release()
                        finishedList[i] = 1
                        return
                    elif fullCheck == 0: # -t 0 -> compress all files even if one does not exist
                        if (intPartilhado.value+2 < len(fichArgs)): #not the last one
                            for indexTemp in range(intPartilhado.value+1, len(fichArgs)): # for all the missing files on the list
                                if os.path.isfile(fichArgs[indexTemp]): # if one exists
                                    fichArgs[(intPartilhado.value+1)]
                                    intPartilhado.value = indexTemp
                                    break
                                if indexTemp == len(fichArgs)-1: # if gets to the end
                                    critSec.release()
                                    finishedList[i] = 1
                                    return
                        else: #if its the last one
                            critSec.release()
                            finishedList[i] = 1
                            return
                else: # if Proposed File exists
                    intPartilhado.value += 1
                fichTemp = fichArgs[intPartilhado.value]
                critSec.release() # exits critical zone
                if comprBool == 0:
                    tempFich = fichTemp.split('.zip')
                    if os.path.isfile(tempFich[0]):
                        pass
                    else:
                        # print "process number " + str(os.getpid()) + " will decompress " + fichTemp
                        timeBC=time.time()
                        decompress(fichTemp)
                        timeAC=time.time()
                        if os.path.isfile(tempFich[0]):
                            fichProcess.value +=1
                            file_info = os.stat(tempFich[0])
                            totalFileSize.value += file_info.st_size
                            if escreverLog == 1:
                                tempTup = str((os.getpid(),fichTemp,file_info.st_size,int((timeAC-timeBC)*1000)))+"\n"
                                writeToFile(tempTup,ficheiro)
                elif comprBool == 1:
                    if os.path.isfile(fichTemp+'.zip'):
                       pass
                    else:
                        # print "process number " + str(os.getpid()) + " will compress " + fichTemp
                        timeBC=time.time()
                        compress(fichTemp)
                        timeAC=time.time()
                        if os.path.isfile(fichTemp+'.zip'):
                            fichProcess.value +=1
                            file_info = os.stat(fichTemp+'.zip')
                            totalFileSize.value += file_info.st_size
                            if escreverLog == 1:
                                tempTup = str((os.getpid(),fichTemp+'.zip',file_info.st_size,int((timeAC-timeBC)*1000)))+"\n"
                                writeToFile(tempTup,ficheiro)
                    
            if (intPartilhado.value+1 >= len(fichArgs)):
                finishedList[i] = 1
                return
    
    def handler(sig, NULL):
        print "Number of processed files so far: " + str(fichProcess.value)
        print "Information Volume Processed so far: " + str(totalFileSize.value/1024) + " Kb"
        horaAgora = time.time()
        print "Time Since Start: " + str(int((horaAgora-horaInicial)*1000)) + " ms"
    
    def controlC(sig,NULL):
        intPartilhado.value == len(fichArgs)-1
        for i in range(procs): # wait for all procs to finish
             os.wait()
        print "Number of processed files so far: " + str(fichProcess.value)
        print "Information Volume Processed so far: " + str(totalFileSize.value/1024) + " Kb"
        horaAgora = time.time()
        print "Time Since Start: " + str(int((horaAgora-horaInicial)*1000)) + " ms"
        print str(os.getpid())
        sys.exit()
    
    while len(list(filter(lambda x: x == 1, finishedList))) != len(pid): # wait for files to be processed!
        signal.signal(signal.SIGINT, controlC)
        if intervalo != -1: # if -a 
            signal.signal(signal.SIGALRM, handler) 
            signal.setitimer(signal.ITIMER_REAL, intervalo, intervalo)
            time.sleep(intervalo)
    
    for i in range(procs): # wait for all procs to finish
        os.wait()

    if escreverLog == 1:
        tempWrite = str(dataInicial)+"\n"
        horaAgora = time.time()
        tempWrite2 = str(int((horaAgora-horaInicial)*1000))+"\n"
        tempWrite3 = str(totalFileSize.value)+"\n"
        writeToFile(tempWrite,ficheiro) # data inicial
        writeToFile(tempWrite2,ficheiro) # tempo que durou
        writeToFile(tempWrite3,ficheiro) # volume processado
    print "Number of Processed Files: " + str(fichProcess.value)
    return


if __name__ == "__main__":
    main(sys.argv[1:])
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
