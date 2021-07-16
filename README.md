## <span style="color: #cc0000">Nastran2Calculix</span>

<span style="color: #0504aa">Create by</span> <span style="color: #cc0000">Domenico Cacozza</span> - domenico.cacozza@gmail.com


<span style="color: #0504aa">This Python code release converts some Nastran input  file cards into the  equivalent CalculiX input file instructions.</span>


<span style="color: #0504aa">Convert the following cards:</span>
* <span style="color: #cc0000">**GRID**</span> <span style="color: #0504aa">&rightarrow;</span> <span style="color: #cc0000">***Node**</span>
* <span style="color: #cc0000">**CTRIA3**</span> <span style="color: #0504aa">&rightarrow;</span> <span style="color: #cc0000">**S3**</span>
* <span style="color: #cc0000">**CQUAD4**</span> <span style="color: #0504aa">&rightarrow;</span> <span style="color: #cc0000">**S4R**</span>
* <span style="color: #cc0000">**CQUAD8**</span> <span style="color: #0504aa">&rightarrow;</span> <span style="color: #cc0000">**S8**</span>
* <span style="color: #cc0000">**CHEXA**</span> <span style="color: #0504aa">&rightarrow;</span> <span style="color: #cc0000">**C3D8**</span>
* <span style="color: #cc0000">**CHEXA20**</span> <span style="color: #0504aa">&rightarrow;</span> <span style="color: #cc0000">**C3D20**</span>
* <span style="color: #cc0000">**CPENTA**</span> <span style="color: #0504aa">&rightarrow;</span> <span style="color: #cc0000">**C3D6**</span>
* <span style="color: #cc0000">**CPENTA15**</span> <span style="color: #0504aa">&rightarrow;</span> <span style="color: #cc0000">**C3D15**</span>
* <span style="color: #cc0000">**CTET**</span> <span style="color: #0504aa">&rightarrow;</span> <span style="color: #cc0000">**C3D4**</span>
* <span style="color: #cc0000">**CTET10**</span> <span style="color: #0504aa">&rightarrow;</span> <span style="color: #cc0000">**C3D10**</span>

<span style="color: #0504aa">Instruction to run the code:</span>

<span style="color: #0504aa">**>python**</span> <span style="color: #cc0000">**Nastran2Calculix.py**</span> <span style="color: #0504aa">*"Nastran input file"*</span>

<span style="color: #0504aa">A file with the same name and extension <span style="color: #cc0000">**.inp**</span> it will be created in the Nastran file folder.</span>
