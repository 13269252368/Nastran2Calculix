'''
Nastran2Calculix

Create by Domenico Cacozza - domenico.cacozza@gmail.com

This Python code converts some Nastran format cards to a Calculix format statement.

Convert the following cards:
from GRID     to *Node
from CTRIA3   to S3
from CQUAD4   to S4R
from CQUAD8   to S8
from CHEXA    to C3D8
from CHEXA20  to C3D20
from CPENTA   to C3D6
from CPENTA15 to  C3D15
from CTET     to  C3D4
from CTET10   to  C3D10

Instruction to run the code:
>python Nastran2Calculix.py "Nastran input file"

A file with the same name and extension .inp it will be created in the Nastran file folder.
'''


import mmap
import time
import sys
import colorama
from colorama import Fore, Back, Style
colorama.init()

def main():
    print(Back.BLACK + '')
    print(Back.GREEN + 'Read '+sys.argv[1]+' file\n')

    f = open(sys.argv[1], "r")
    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

    grid = {}
    elements  = {"CTET4": {},"CTET10": {},"CQUAD4": {},"CQUAD8": {}, "CHEXA": {},  "CHEXA20": {}, "CTRIA3": {}, "CPENTA": {}, "CPENTA15": {}}
    setnodes = {}

    ReadNastranFile(s, grid, elements, setnodes)

    s.close()

    i = 0
    cx = ''
    while(True):
	    if sys.argv[1][i] == '.' or i == len(sys.argv[1]): break
	    cx = cx + sys.argv[1][i]
	    i   = i + 1

    cx = cx + '.inp'

    f = open(cx,"w")

    WriteCalculixFile(f,grid,elements)
    
    print('Write '+cx+' file\n')

    f.close()

def ReadNastranFile(s,grid,elements, setnodes):
    
 #   ReadSet(s, setnodes)

#    s.seek(0)

    ReadGrids(s,grid)
   
    s.seek(0)

    ReadCquad4(s,elements)

    s.seek(0)

    ReadCtria3(s,elements)

    s.seek(0)
    
    ReadCquad8(s,elements)

    s.seek(0)

    ReadCtetra(s,elements)
 
    s.seek(0)

    ReadChexa(s,elements)

    s.seek(0)

    ReadCpenta(s,elements)

    s.seek(0)
   
def ReadLine(a,s):
    # Find begin of the line
    s.seek(a-1)
    while(True):
        value_byte = bytes([s.read_byte()])
        a = s.tell()
        if str(value_byte) == str(b'\n'):
            break
        else:
            a -= 2
            s.seek(a)
        
    s.seek(a)
    line = s.readline()

    return line

def FindCharacter(string, character):
  indexs = []
  for j in range(0,len(string)):
      if str(bytes([string[j]])) == character:
          indexs.append(j)

  return indexs

def ReadSet(s, setnodes):
    # Find set and put it in a dictionary
    # key is set id
    # [node1, node2, node3,...]
    start_time = time.time()
    #
    setnodestmp = {}
    #    
    while(True):
        if s.find(b'SET ') == -1:
            break
        else:
            a = s.find(b'SET ')
            line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                index = FindCharacter(line, str(b'='))
                
                if len(index) != 0:
                    setnodestmp[int(line[3:index[0]-1])] = []
                    indexs = FindCharacter(line, str(b','))
                    if len(indexs) !=0:
                        
                        setnodestmp[int(line[3:index[0]-1])].append(line[index[0]:indexs[0]])
                        for j in range(1, len(indexs)):
                            print(indexs[j-1])
                            print(indexs[j])
                            print(line)
                            print(line[indexs[j-1]:index[j]])
                            setnodestmp[int(line[3:index[0]-1])].append(line[indexs[j-1]:index[j]])
                        while(True):
                            line = s.readline()
                            if  (str(bytes([line[0]])) != str(b'$')) and (len(line)>0) and (line[0:3] != 'SET'):
                               indexs = FindCharacter(line, str(b','))
                               for j in range(1, len(indexs)):
                                    setnodestmp[int(line[3:(index[0]-1)])].append(line[indexs[j-1]:index[j]])
                            else:
                                break
    print(len(setnodestmp))
    if len(setnodestmp.keys()) > 0:
        for key in sorted(setnodestmp.keys()):
            setnodes[key] = []
            listnodes = setnodestmp[key]
            for j in range(0,len(listnodes)):
                value = listnodes[j]
                listvalue = GetValue(value)
                for jj in range(0,len(listvalue)):
                    setnodes[key].append(listnodes[jj])
    
    return setnodes

def GetValue(value):
    listvalue = []
    index = FindCharacter(value,'T')
    if len(index) > 0:
        pos1 = index[0]
        index = FindCharacter(value,'U')
        pos2 = index[0]
        firstvalue  = int(value[0:pos1])
        secondvalue = int(value[pos2:(len(value) - 1)])
        for j in range(0,(secondvalue - firstvalue)):
            listvalue.append(firstvalue + j)
    return listvalue

def ReadGrids(s,grid):
    # Find grid points and put it in a dictionary
    # key is grid id
    # [coord id, x, y, z]
    start_time = time.time()
    # Find small filds       
    while(True):
        if s.find(b'GRID    ') == -1:
            break
        else:
            a = s.find(b'GRID    ')
            line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                x = line[24:32].decode()
                y = line[32:40].decode()
                z = line[40:48].decode()
                grid[int(line[8:16])] = [int((line[16:24] and line[16:24].strip()) or '0'),\
                    float(AdjNasNum(x)),float(AdjNasNum(y)),float(AdjNasNum(z))]
                
    # Find large filds
    s.seek(0)
    while(True):
        if s.find(b'GRID*   ') == -1:
            break
        else:
            a = s.find(b'GRID*   ')
            line = line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                x = line[40:56].decode()
                y = line[56:72].decode()
                grid[int(line[8:24])] = [int((line[24:40] and line[24:40].strip()) or '0'),\
                    float(AdjNasNum(x)),float(AdjNasNum(y))]
                id = int(line[8:24])
                line = s.readline()
                z = line[8:24].decode()
                grid[id].append(float(AdjNasNum(z)))
    end_time = time.time()
    e = int(end_time - start_time)

    if len(grid.keys()) > 0:
        print('Read' +' '+ str(len(grid.keys())) +' '+ 'Nodes in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms'.format(e \
            // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))
        print('')
    else:
        print(Back.RED + 'No Nodes in file\n')

def ReadCquad4(s,elements):
    # Find cquad4 and put it in the dictionary of dictionary elements
    # key is cquad4 id
    # [PSHELL id, GRID1, GRID2, GRID3, GRID4]
    start_time = time.time()
    # Find small filds
    while(True):
        if s.find(b'CQUAD4  ') == -1:
            break
        else:
            a = s.find(b'CQUAD4  ')
            line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                elements["CQUAD4"][int(line[8:16])] = [int(line[16:24]),int(line[24:32]),\
                    int(line[32:40]),int(line[40:48]),int(line[48:56])]
    
    # Find large filds
    s.seek(0)
    while(True):
        if s.find(b'CQUAD4* ') == -1:
            break
        else:
            a = s.find(b'CQUAD4* ')
            line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                elements["CQUAD4"][int(line[8:24])] = [int(line[24:40]),int(line[40:56]),\
                    int(line[56:72])]
                id = int(line[8:24])
                line = s.readline()
                elements["CQUAD4"][id].append(int(line[8:24]))
                elements["CQUAD4"][id].append(int(line[24:40]))

    end_time = time.time()
    e = int(end_time - start_time)

    if len(elements['CQUAD4'].keys()) > 0:
        print(Back.GREEN + 'Read' +' '+ str(len(elements['CQUAD4'].keys())) +' '+ 'cquad4 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))
        print('')
    else:
        print(Back.YELLOW + 'No cquad4 elements in file\n')

def ReadCtria3(s,elements):
    # Find ctria3 and put it in the dictionary of dictionary elements
    # key is ctria3 id
    # [PSHELL id, GRID1, GRID2, GRID3]
    start_time = time.time()
    # Find small filds
    while(True):
        if s.find(b'CTRIA3  ') == -1:
            break
        else:
            a = s.find(b'CTRIA3  ')
            line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                elements["CTRIA3"][int(line[8:16])] = [int(line[16:24]),int(line[24:32]),\
                    int(line[32:40]),int(line[40:48])]
    
    # Find large filds
    s.seek(0)
    while(True):
        if s.find(b'CTRIA3* ') == -1:
            break
        else:
            a = s.find(b'CTRIA3* ')
            line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                elements["CTRIA3"][int(line[8:24])] = [int(line[24:40]),int(line[40:56]),\
                    int(line[56:72])]
                id = int(line[8:24])
                line = s.readline()
                elements["CTRIA3"][id].append(int(line[8:24]))
    
    end_time = time.time()
    e = int(end_time - start_time)

    if len(elements['CTRIA3'].keys()) > 0:
        print(Back.GREEN + 'Read' +' '+ str(len(elements['CTRIA3'].keys())) +' '+ 'ctria3 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))
        print('')
    else:
        print(Back.YELLOW + 'No ctria3 elements in file\n')

def ReadCquad8(s,elements):
    # Find chexa and put it in the dictionary of dictionary elements
    # key is chexa id
    # [PSOLID id, GRID1, GRID2, GRID3, GRID4, GRID5, GRID6, GRID7, GRID8]
    start_time = time.time()
    # Find small filds
    while(True):
        if s.find(b'CQUAD8  ') == -1:
            break
        else:
            a = s.find(b'CQUAD8  ')
            line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                elements["CQUAD8"][int(line[8:16])] = [int(line[16:24]),int(line[24:32]),int(line[32:40]),int(line[40:48]),int(line[48:56]),\
		        int(line[56:64]),int(line[64:72])]
                id = int(line[8:16])
                line = s.readline()
                elements["CQUAD8"][id].append(int(line[8:16]))
                elements["CQUAD8"][id].append(int(line[16:24]))

    # Find large filds
    while(True):
        if s.find(b'CQUAD8* ') == -1:
            break
        else:
            a = s.find(b'CQUAD8* ')
            line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                elements["CQUAD8"][int(line[8:24])] = [int(line[24:40]),int(line[40:56]),int(line[56:72])]
                id = int(line[8:24])
                line = s.readline()
                elements["CQUAD8"][id].append(int(line[8:24]))
                elements["CQUAD8"][id].append(int(line[24:40]))
                elements["CQUAD8"][id].append(int(line[40:56]))
                elements["CQUAD8"][id].append(int(line[56:72]))
                line = s.readline()
                elements["CQUAD8"][id].append(int(line[8:24]))
                elements["CQUAD8"][id].append(int(line[24:40]))

    end_time = time.time()
    e = int(end_time - start_time)

    if len(elements['CQUAD8'].keys()) - 1 > 0:
        print(Back.GREEN + 'Read' +' '+ str(len(elements['CQUAD8'].keys()) - 1) +' '+ 'cquad8 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))
        print('')
    else:
        print(Back.YELLOW + 'No cquad8 elements in file')
        print('')

def ReadCtetra(s,elements):
    # Find ctetra10 and put it in the dictionary of dictionary elements
    # key is ctetra id
    # tretra4 [PSOLID id, GRID1, GRID2, GRID3, GRID4]
    # tretra10 [PSOLID id, GRID1, GRID2, GRID3, GRID4, GRID5, GRID6, GRID7, GRID8, GRID9, GRID10]
    start_time = time.time()
    # Find small filds
    while(True):
        if s.find(b'CTETRA  ') == -1:
            break
        else:
            a = s.find(b'CTETRA  ')
            line = ReadLine(a,s)
            line = line[0:80] # Considering only the first 80 columns
            line = line.rstrip() # Remove blank on the right
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                if len(line) > 56: # If it is true, it means CTETRA 10
                    elements["CTET10"][int(line[8:16])] = [int(line[16:24]),int(line[24:32]),int(line[32:40]),\
                        int(line[40:48]),int(line[48:56]),int(line[56:64]),int(line[64:72])]
                    id = int(line[8:16])
                    line = s.readline()
                    elements["CTET10"][id].append(int(line[8:16]))
                    elements["CTET10"][id].append(int(line[16:24]))
                    elements["CTET10"][id].append(int(line[24:32]))
                    elements["CTET10"][id].append(int(line[32:40]))
                else:
                    elements["CTET4"][int(line[8:16])] = [int(line[16:24]),int(line[24:32]),int(line[32:40]),\
                        int(line[40:48]),int(line[48:56])]


    # Find large filds
    s.seek(0)
    while(True):
        if s.find(b'CTETRA* ') == -1:
            break
        else:
            a = s.find(b'CTETRA* ')
            line_1 = ReadLine(a,s)
            line_2 = s.readline()
            line_2 = line_2[0:80] # Considering only the first 80 columns
            line_2 = line_2.rstrip() # Remove blank on the right
            if str(bytes([line_1[0]])) != str(b'$'): # line not commented
                if len(line_2) > 40: # If it is true, it means CTETRA 10
                    elements["CTET10"][int(line_1[8:24])] = [int(line_1[24:40]),int(line_1[40:56]),int(line_1[56:72]),\
                        int(line_2[8:24]),int(line_2[24:40]),int(line_2[40:56]),int(line_2[56:72])]
                    id = int(line_1[8:24])
                    line = s.readline()
                    elements["CTET10"][id].append(int(line[8:24]))
                    elements["CTET10"][id].append(int(line[24:40]))
                    elements["CTET10"][id].append(int(line[40:56]))
                    elements["CTET10"][id].append(int(line[56:72]))
                else:
                    elements["CTET4"][int(line_1[8:24])] = [int(line_1[24:40]),int(line_1[40:56]),int(line_1[56:72]),\
                        int(line_2[8:24]),int(line_2[24:40])]

    end_time = time.time()
    e = int(end_time - start_time)

    if len(elements['CTET4'].keys()) > 0:
        print(Back.GREEN + 'Read' +' '+ str(len(elements['CTET4'].keys())) +' '+ 'ctetra4 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))
        print('')
    else:
        print(Back.YELLOW + 'No ctetra4 elements in file\n')

    if len(elements['CTET10'].keys()) > 0:
        print(Back.GREEN + 'Read' +' '+ str(len(elements['CTET10'].keys())) +' '+ 'ctetra10 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))
        print('')
    else:
        print(Back.YELLOW + 'No ctetra10 elements in file\n')

def ReadChexa(s,elements):
    # Find chexa and put it in the dictionary of dictionary elements
    # key is chexa id
    # [PSOLID id, GRID1, GRID2, GRID3, GRID4, GRID5, GRID6, GRID7, GRID8]
    start_time = time.time()
    # Find small filds
    while(True):
        if s.find(b'CHEXA   ') == -1:
            break
        else:
            a = s.find(b'CHEXA   ')
            line_1 = ReadLine(a,s)
            line_2 = s.readline()
            line_2 = line_2[0:80] # Considering only the first 80 columns
            line_2 = line_2.rstrip() # Remove blank on the right
            if str(bytes([line_1[0]])) != str(b'$'): # line not commented
                if len(line_2) > 25: # If it is true, it means CHEXA 20
                    elements["CHEXA20"][int(line_1[8:16])] = [int(line_1[16:24]),int(line_1[24:32]),int(line_1[32:40]),int(line_1[40:48]),int(line_1[48:56]),\
                        int(line_1[56:64]),int(line_1[64:72]),int(line_2[8:16]),int(line_2[16:24]),int(line_2[24:32]),int(line_2[32:40]),int(line_2[40:48]),int(line_2[48:56]),\
                        int(line_2[56:64]),int(line_2[64:72])]
                    id = int(line_1[8:16])
                    line = s.readline()
                    elements["CHEXA20"][id].append(int(line[8:16]))
                    elements["CHEXA20"][id].append(int(line[16:24]))
                    elements["CHEXA20"][id].append(int(line[24:32]))
                    elements["CHEXA20"][id].append(int(line[32:40]))
                    elements["CHEXA20"][id].append(int(line[40:48]))
                    elements["CHEXA20"][id].append(int(line[48:56]))
                else:
                    elements["CHEXA"][int(line_1[8:16])] = [int(line_1[16:24]),int(line_1[24:32]),int(line_1[32:40]),int(line_1[40:48]),int(line_1[48:56]),\
                        int(line_1[56:64]),int(line_1[64:72]),int(line_2[8:16]),int(line_2[16:24])]

    # Find large filds
    while(True):
        if s.find(b'CHEXA*  ') == -1:
            break
        else:
            a = s.find(b'CHEXA*  ')
            line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                elements["CHEXA"][int(line[8:24])] = [int(line[24:40]),int(line[40:56]),int(line[56:72])]
                id = int(line[8:24])
                line = s.readline()
                elements["CHEXA"][id].append(int(line[8:24]))
                elements["CHEXA"][id].append(int(line[24:40]))
                elements["CHEXA"][id].append(int(line[40:56]))
                elements["CHEXA"][id].append(int(line[56:72]))
                line = s.readline()
                elements["CHEXA"][id].append(int(line[8:24]))
                elements["CHEXA"][id].append(int(line[24:40]))

    end_time = time.time()
    e = int(end_time - start_time)

    if len(elements['CHEXA'].keys()) - 1 > 0:
        print(Back.GREEN + 'Read' +' '+ str(len(elements['CHEXA'].keys()) - 1) +' '+ 'chexa 8 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))
        print('')
    else:
        print(Back.YELLOW + 'No chexa 8 elements in file')
        print('')

    if len(elements['CHEXA20'].keys()) - 1 > 0:
        print(Back.GREEN + 'Read' +' '+ str(len(elements['CHEXA20'].keys()) - 1) +' '+ 'chexa 20 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))
        print('')
    else:
        print(Back.YELLOW + 'No chexa 20 elements in file')
        print('')

def ReadCpenta(s,elements):
    # Find chexa and put it in the dictionary of dictionary elements
    # key is cpenta id
    # [PSOLID id, GRID1, GRID2, GRID3, GRID4, GRID5, GRID6]
    start_time = time.time()
    # Find small filds
    while(True):
        if s.find(b'CPENTA  ') == -1:
            break
        else:
            a = s.find(b'CPENTA  ')
            line_1 = ReadLine(a,s)
            line_2 = s.readline()
            line_2 = line_2[0:80] # Considering only the first 80 columns
            line_2 = line_2.rstrip() # Remove blank on the right
            if str(bytes([line_1[0]])) != str(b'$'): # line not commented
                if line_2[0:8] == b'        ': # If it is true, it means CPENTA 15
                    elements["CPENTA15"][int(line_1[8:16])] = [int(line_1[16:24]),int(line_1[24:32]),int(line_1[32:40]),int(line_1[40:48]),int(line_1[48:56]),\
                        int(line_1[56:64]),int(line_1[64:72]),int(line_2[8:16]),int(line_2[16:24]),int(line_2[24:32]),int(line_2[32:40]),int(line_2[40:48]),int(line_2[48:56]),\
                        int(line_2[56:64]),int(line_2[64:72])]
                    id = int(line_1[8:16])
                    line = s.readline()
                    elements["CPENTA15"][id].append(int(line[8:16]))
                else:
                    elements["CPENTA"][int(line_1[8:16])] = [int(line_1[16:24]),int(line_1[24:32]),int(line_1[32:40]),int(line_1[40:48]),int(line_1[48:56]), \
                        int(line_1[56:64]),int(line_1[64:72])]
                    s.seek(a+1) # Because if no it continues after line_2 

    # Find large filds
    while(True):
        if s.find(b'CPENTA* ') == -1:
            break
        else:
            a = s.find(b'CPENTA* ')
            line = ReadLine(a,s)
            if str(bytes([line[0]])) != str(b'$'): # line not commented
                elements["CPENTA"][int(line[8:24])] = [int(line[24:40]),int(line[40:56]),int(line[56:72])]
                id = int(line[8:24])
                line = s.readline()
                elements["CPENTA"][id].append(int(line[8:24]))
                elements["CPENTA"][id].append(int(line[24:40]))
                elements["CPENTA"][id].append(int(line[40:56]))
                elements["CPENTA"][id].append(int(line[56:72]))

    end_time = time.time()
    e = int(end_time - start_time)

    if len(elements['CPENTA'].keys()) - 1 > 0:
        print(Back.GREEN + 'Read' +' '+ str(len(elements['CPENTA'].keys()) - 1) +' '+ 'cpenta 6 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))
        print('')
    else:
        print(Back.YELLOW + 'No cpenta 6 elements in file')
        print('')

    if len(elements['CPENTA15'].keys()) - 1 > 0:
        print(Back.GREEN + 'Read' +' '+ str(len(elements['CPENTA15'].keys()) - 1) +' '+ 'cpenta 15 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))
        print('')
    else:
        print(Back.YELLOW + 'No cpenta 15 elements in file')
        print('')

def WriteCalculixFile(f,grid,elements):

    WriteNodes(f,grid)    

    WriteD3D10(f,elements)
 
    WriteD3D4(f,elements)

    WriteS4R(f,elements)
    
    WriteS8(f,elements)

    WriteS3(f,elements)
    
    WriteC3D8(f,elements)

    WriteC3D6(f,elements)

    WriteC3D20(f,elements)

    WriteC3D15(f,elements)

def WriteNodes(f,grid):

    stringa = []
    if len(grid.keys()) != 0:
        start_time = time.time()
        f.write('*node, nset=Nall\n')
        for key in sorted(grid.keys()):
            stringa.append('%d, %1.6e, %1.6e, %1.6e\n' % (key, grid[key][1], grid[key][2], grid[key][3]))


        f.writelines(stringa)
        end_time = time.time()
        e = int(end_time - start_time)
        print(Back.GREEN + 'Write Nodes in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms\n'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))

def WriteD3D10(f,elements):
    #Write C3D10 elements
    stringa = []
    if len(elements['CTET10'].keys())!= 0:
        start_time = time.time()
        f.write('*element, elset=CTET10,type=C3D10\n')
        for key in sorted(elements['CTET10'].keys()):
            stringa.append('%d, %d, %d, %d, %d, %d, %d, %d, %d,%d, %d,\n' % (key,\
																  elements['CTET10'][key][1],elements['CTET10'][key][2],elements['CTET10'][key][3],\
																  elements['CTET10'][key][4],elements['CTET10'][key][5],elements['CTET10'][key][6],\
																  elements['CTET10'][key][7],elements['CTET10'][key][8],elements['CTET10'][key][9],\
																  elements['CTET10'][key][10]))
        f.writelines(stringa)   
        end_time = time.time()
        e = int(end_time - start_time)
        print('Write C3D10 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms\n'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))

def WriteD3D4(f,elements):
    #Write C3D4 elements
    stringa = []
    if len(elements['CTET4'].keys())!= 0:
        start_time = time.time()
        f.write('*element, elset=CTET10,type=C3D10\n')
        for key in sorted(elements['CTET4'].keys()):
            stringa.append('%d, %d, %d, %d, %d,\n' % (key,\
																  elements['CTET4'][key][1],elements['CTET4'][key][2],elements['CTET4'][key][3],\
																  elements['CTET4'][key][4]))
        f.writelines(stringa)   
        end_time = time.time()
        e = int(end_time - start_time)
        print('Write C3D4 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms\n'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))

def WriteS4R(f,elements):
    #Write S4R elements
    stringa = []
    if len(elements['CQUAD4'].keys())!= 0:
        start_time = time.time()
        f.write('*element, elset=S4R,type=S4R\n')
        for key in sorted(elements['CQUAD4'].keys()):
            stringa.append('%d, %d, %d, %d, %d,\n' % (key,\
												elements['CQUAD4'][key][1],elements['CQUAD4'][key][2],elements['CQUAD4'][key][3],\
												elements['CQUAD4'][key][4]))
        f.writelines(stringa)
    
        end_time = time.time()
        e = int(end_time - start_time)
        print('Write S4R elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms\n'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))

def WriteS8(f,elements):
    #Write S8 elements
    stringa = []
    if len(elements['CQUAD8'].keys())!= 0:
        f.write('*element, elset=S8,type=S8\n')
        start_time = time.time()
        for key in sorted(elements['CQUAD8'].keys()):
            stringa.append('%d, %d, %d, %d, %d, %d, %d, %d, %d,\n' % (key,\
                elements['CQUAD8'][key][1],elements['CQUAD8'][key][2],elements['CQUAD8'][key][3],\
                elements['CQUAD8'][key][4],elements['CQUAD8'][key][5],elements['CQUAD8'][key][6],\
                elements['CQUAD8'][key][7],elements['CQUAD8'][key][8]))
        f.writelines(stringa)

        end_time = time.time()
        e = int(end_time - start_time)
        print('Write S8 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms\n'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))

def WriteS3(f,elements):
    #Write S3 elements
    stringa = []
    if len(elements['CTRIA3'].keys())!= 0:
        start_time = time.time()
        f.write('*element, elset=S3,type=S3\n')
        for key in sorted(elements['CTRIA3'].keys()):
            stringa.append('%d, %d, %d, %d,\n' % (key,\
												elements['CTRIA3'][key][1],elements['CTRIA3'][key][2],elements['CTRIA3'][key][3]))
        f.writelines(stringa)

        end_time = time.time()
        e = int(end_time - start_time)
        print('Write S3 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms\n'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))

def WriteC3D8(f,elements):
    #Write C3D8 elements
    stringa = []
    if len(elements['CHEXA'].keys())!= 0:
        f.write('*element, elset=C3D8,type=C3D8\n')
        start_time = time.time()
        for key in sorted(elements['CHEXA'].keys()):
            stringa.append('%d, %d, %d, %d, %d, %d, %d, %d, %d,\n' % (key,\
                elements['CHEXA'][key][1],elements['CHEXA'][key][2],elements['CHEXA'][key][3],\
                elements['CHEXA'][key][4],elements['CHEXA'][key][5],elements['CHEXA'][key][6],\
                elements['CHEXA'][key][7],elements['CHEXA'][key][8]))
        f.writelines(stringa)

        end_time = time.time()
        e = int(end_time - start_time)
        print('Write C3D8 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms\n'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))

def WriteC3D20(f,elements):
    #Write C3D20 elements
    stringa = []
    if len(elements['CHEXA20'].keys())!= 0:
        f.write('*element, elset=C3D20,type=C3D20\n')
        start_time = time.time()
        for key in sorted(elements['CHEXA20'].keys()):
            stringa.append('%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, \n' % (key,\
                elements['CHEXA20'][key][1],elements['CHEXA20'][key][2],elements['CHEXA20'][key][3],\
                elements['CHEXA20'][key][4],elements['CHEXA20'][key][5],elements['CHEXA20'][key][6],\
                elements['CHEXA20'][key][7],elements['CHEXA20'][key][8], elements['CHEXA20'][key][9],\
                elements['CHEXA20'][key][10]))
            stringa.append('%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, \n' % (elements['CHEXA20'][key][11], elements['CHEXA20'][key][12],\
                elements['CHEXA20'][key][17], elements['CHEXA20'][key][18], elements['CHEXA20'][key][19],\
                elements['CHEXA20'][key][20], elements['CHEXA20'][key][13], elements['CHEXA20'][key][14],\
                elements['CHEXA20'][key][15], elements['CHEXA20'][key][16]))
        f.writelines(stringa)

        end_time = time.time()
        e = int(end_time - start_time)
        print('Write C3D20 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms\n'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))

def WriteC3D6(f,elements):
    #Write C3D6 elements
    stringa = []
    if len(elements['CPENTA'].keys())!= 0:
        f.write('*element, elset=C3D6,type=C3D6\n')
        start_time = time.time()
        for key in sorted(elements['CPENTA'].keys()):
            stringa.append('%d, %d, %d, %d, %d, %d, %d,\n' % (key,\
                elements['CPENTA'][key][1],elements['CPENTA'][key][2],elements['CPENTA'][key][3],\
                elements['CPENTA'][key][4],elements['CPENTA'][key][5],elements['CPENTA'][key][6],))
        f.writelines(stringa)

        end_time = time.time()
        e = int(end_time - start_time)
        print('Write C3D6 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms\n'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))

def WriteC3D15(f,elements):
    #Write C3D15 elements
    stringa = []
    if len(elements['CPENTA15'].keys())!= 0:
        f.write('*element, elset=C3D15,type=C3D15\n')
        start_time = time.time()
        for key in sorted(elements['CPENTA15'].keys()):
            stringa.append('%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, \n' % (key,\
                elements['CPENTA15'][key][1],elements['CPENTA15'][key][2],elements['CPENTA15'][key][3],\
                elements['CPENTA15'][key][4],elements['CPENTA15'][key][5],elements['CPENTA15'][key][6],\
                elements['CPENTA15'][key][7],elements['CPENTA15'][key][8],elements['CPENTA15'][key][9],\
                elements['CPENTA15'][key][13],elements['CPENTA15'][key][14],elements['CPENTA15'][key][15],\
                elements['CPENTA15'][key][10],elements['CPENTA15'][key][11],elements['CPENTA15'][key][12]))
        f.writelines(stringa)

        end_time = time.time()
        e = int(end_time - start_time)
        print('Write C3D15 elements in:')
        print('{:02d} h : {:02d} m : {:02d} s : {:2.8f} ms\n'.format(e // 3600, (e % 3600 // 60), e % 60, (end_time - start_time) * 1000))

def SearchInList(list, value):

    # Find a value in a list

    for i in range(len(list)):
        if list[i] == value:
            return True
    return False

def AdjNasNum(list):
    
    # Replaces numbers from format (es) 12 + 4 to the format 12e + 12
    
    if SearchInList(list[1:], '-') or SearchInList(list[1:], '+'):
        if SearchInList(list[1:], '-'): 
            index = list[1:].index('-')
        else:
            index = list[1:].index('+')
        if(list[index] != 'e') and (list[index] != 'E'):
            list = list[:index + 1] + 'e' + list[index + 1:]
    
    return list

if __name__ == '__main__':
    main()
