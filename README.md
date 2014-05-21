AffyPipe: _an open-source pipeline for Affymetrix Axiom genotyping workflow on livestock species_
=========
*ref: E.L. Nicolazzi (Fondazione Parco Tecnologico Padano) - Via Einstein, Loc. Cascina Codazza (26900) Lodi (Italy). Email: ezequiel [dot] nicolazzi [at] tecnoparco [dot] org*


The goal of this pipeline is to authomatize Affymetrix's genotyping workflow for Linux and Mac users: from Power tools (APTools) to SNPolisher R package.
This is a one-step tool that combines all Affymetrix software and produces edited and user-friendly format output files. In fact, AffyPipe allows you to edit SNP probe classes directly while exporting genotypes in PLINK format (Purcel et al, 2007).
It was originally built for the **International Buffalo Genome Consortium** (Iamartino, 2013), but can be easily modified to handle other species (e.g. cow, chichen, fisheries).
Users are strongly adviced to read carefully Affymetrix's "Axiom genotyping solution data analysis guide" and "Best practice supplement to Axiom genotyping solution data analysis user guide" before using this tool. 

### **1) Getting the pipeline, and requirements**
The fastest and more clever way of getting this pipeline and all accessory files is installing git and cloning this repository.
Further information on how to install git on Linux and Mac can be found at: http://git-scm.com/book/en/Getting-Started-Installing-Git . An example of cloning command using command line is: 

% git clone --recursive https://github.com/nicolazzie/AffyPipe.git

The AffyPipe pipeline is for users running **Linux/Unix** and **Mac** operative systems, and only runs over 64bit processors. **Windows users should use Gentoyping Console (TM) Software, which already cover all of these functionalities!!!** 
You should have Python (2.x) and R (any version?) already installed on your computer (Mac users have python already installed by default). The whole pipeline was thoroughly tested under Python 2.7.6 and R 3.0.

### **2) Folders and files required**
The Affymetrix genotyping workflow requires several Affymetrix files to run. To help you through, all files were organized into two main folders.
Below, default folder names are provided as example (note these names and values are also default in AffyPipe). 
However, you can use your own folder names (see "Options" paragraph in Section 3).

All Affymetrix files are downloadable at their website (http://www.affymetrix.com).
Please remember that you need to register to be able to download all the files below!
**NOTE: If you cloned or downloaded all the folders in this repository, you'll see example names of the files you need. All files are empty: i)to avoid copyright issues with Affymetrix and; ii) to force you downloading the latest version of all the files and softwares.**

 - **2.a)** _AFFYTOOLS_ folder: Nearly all data downloaded from Affymetrix website is placed here. Essentially 3 different files are needed (2.a.1, 2.a.2.1 and 2.a.2.2). 
  - **2.a.1)** Go to: Products > Microarray Solutions > DNA Analysis Solutions > Agrigenomics Solutions > Arrays > Species > Buffalo/[other species], and download the file under *Library Files* section.  For the buffalo it is **Axiom® Buffalo Analysis Files.r[X].zip**, for cow **Axiom_GW_bos_snp_1_r[X].zip**, where [X] stands for the version of the Analysis Files. Please uncompress this file and you'll get a lot of "Axiom_[species].[X].[blablabla] files.
  - **2.a.2)** Go to: Partners & Programs > Developers' Network > DevNet Tools. Inside there you'll find:
      - **2.a.2.1)** Affymetrix PowerTools (APTools): Here you should download the right file for your operative system (something like **APT[X] Linux 64 bit x86 binaries** or **APT [X] Mac OS-Lion 64-bit Intel Binaries**). Note: This pipeline was tested on both OSs. If you're using Mavericks OS, no worries, it will run ok. Please uncompress this folder (inside AFFYTOOLS, if you like).
      - **2.a.2.2)** **SNPolisher**: An R package for post-processing array's results. Please uncompress this folder (inside AFFYTOOLS, if you like).
    
 - **2.b)** _AxiomReference_ folder: You will receive an annotation file from Affymetrix along with your genotypes. However, since data is updated constantly, the download of the latest annotation file is **STRONGLY** recommended. By doing this, even if you analyse samples in different times, you'll be sure of using the latest map information! You can find this in: Products > Microarray Solutions > DNA Analysis Solutions > Agrigenomics Solutions > Arrays > Species > Buffalo[/Bovine or other species]. There, under *Current NetAffx Annotation Files* section, download the file **Axiom_Buffalo Annotations, CSV format** (for buffalo) or **Axiom_GW_Bos_SNP_1.na[X].annot, CSV format** (for cow). Please remember to uncompress the file!
 
 - **2.c)** *a CEL list file*: All Affymetrix Power Tools programs need a file containing a list of CEL files (raw data) to be analysed. Fortunately, using AffyPipe you will have to do this just once! It is highly recommended that you provide also the full path to the .CEL files. Just remember that *CEL list files* need a compulsary header row: "cel_files". If such header is missing, AffyPipe will stop, since APTools programs cannot run without that header!. 
To help you here, a small bash program called "createcelfile.sh" is also provided. The program *actually creates* the CEL list files for you. You only have to place this program in the directory where the .CEL files are stored, and run it. This creates a "mycellistfile.txt" file (your CEL list file!), that you can rename and put wherever you want (e.g. in the main folder?).
To run this program:

% chmod 755 createcelfile.sh && ./createcelfile.sh 

A short explanation for those not used to command line: **chmod 755 createcelfile.sh** means that you are giving all access rights (read/write/execute) to your user + read/execute rights to all other users. You actually need to do this just once!; **&&** means something like "after you have succeeded doing the thing on the left, do the thing on the right"; **./createcelfile.sh** this command actually launches the program.  

Once you have finished, if you named the folders same as I did, you should have:
  - A main folder (where AffyPipe.py is)
  - 2 sub-folders (AFFYTOOLS -**2.a.**- and AxiomReference -**2.b.**-).
      - Inside AFFYTOOLS: A bunch of files + 2 folders (e.g. *SNPolisher_package* and *apt-[sometext_yourversion]*)
      - Inside AxiomReference, just one SNP map file (uncompressed)
  - A .CEL list file (somewhere... I place it usually in the main folder).
  

### **3) Running AffyPipe.py**

The AffyPipe pipeline is very versatile, thanks to a number of options you can set up. The only parameter that is *compulsary* is the name (and path) of the cel list file (e.g. the one you created with createcelfile.sh). You can find a long explanation of AffyPipe options below in the "Option" section or a short and handy version by typing:

% python AffyPipe.py -h

or 

% python AffyPipe.py --help

The general usage for the pipeline is:
 
% python AffyPipe.py [options] [cel-list-file]

For example, if:
  - You followed the instructions above, naming folders as in this readme;
  - You want to use default values;
  - Your CEL list file is in /home/Affydata;
  - You have already run createcelfile.sh in there (without renaming the output)

You can run the pipeline like this:

% python AffyPipe.py /home/Affydata/mycellistfile.txt

#### *Options*
The AffyPipe pipeline is very flexible and user-friendly. 
You can choose your own parameters, filenames and folders with very little effort. 
A bit more detailed info on each of the options available is provided, including default values.
Please be aware that these are true *options*, thus are absolutely *optional* and you can place them in any order you like. 

**-h, --help** This displays usage and options available. 
 
**-t [PATH]** or **--tooldir=[PATH]** [DEFAULT: ./AFFYTOOLS]
This option can be used to change the path and name of the folder where *Axiom® Buffalo Analysis Files.r[X].zip* (or its relative file for the bovine species) files were uncompressed (see section 2.a for further information).
 
**-a [PATH]** or **--aptdir=[PATH]** [DEFAULT: ./AFFYTOOLS/apt-[folder_name]]
If you download the Affymetrix PowerTools (APTools) version 1.15.2 for your operative system and you uncompressed it in AFFYTOOLS directory, you can skip this option, since AffyPipe will recognize your system automatically. 
For newer versions, or if APTools folder is not in the default path, you can use this option change the path to the uncompressed APTools folder. See section 2.a.2.1 for further information.
 
**-s [PATH]** or **--SNPolisher=[PATH]** [DEFAULT: ./AFFYTOOLS/SNPolisher\_package]
This option can be used to change the path and name of the folder where *SNPolisher_package.zip* files were uncompressed (see section 2.a.2.2 for further information).

**-m [FILE]** or **--map=[FILE]** [DEFAULT: ./AxiomReference/Axiom\_Buffalo_Annotation.csv]
This option can be used to change the path and name of the Annotation file. Download the **CSV format** file and uncompress it (see section 2.b for further information).

**-o [PATH]** or **--outdir=[PATH]** [DEFAULT: ./OUTPUT]
This option can be used to choose path and name of the output folder where all output files will be written. If the folder does not exists, a new folder will be created with the given name.

**-d VALUE 0>=1** or **--dqc=VALUE 0>=1** [DEFAULT: 0.82]
This option can be used to set a user defined Dish_QC threshold. Default here is Affymetrix's best practice default. See their "Axiom genotyping solution data analysis guide" and "Best practice supplement to Axiom genotyping solution data analysis user guide" for further details.

**-c VALUE 0>=1** or **--crate=VALUE 0>=1** [DEFAULT: 0.97]
This option can be used to set a user defined call rate threshold. Default here is Affymetrix's best practice default. See their "Axiom genotyping solution data analysis guide" and "Best practice supplement to Axiom genotyping solution data analysis user guide" for further details.

**-y** or **--summary** [DEFAULT: no summaries files]
This option allows to output the summary information of the genotyping process. Please note that these files are VERY large. Since the general user does not usually uses this file, the default is not printing this out. However, there are several occasions where the analysis of this file could be useful, thus an option to output this file was included.

**-p** or **--plink** [DEFAULT: no plink output]
This option outputs (all) *BestProbeset* SNPs in PLINK format. The pipeline just goes through the Ps.performace.txt (output) file keeping genotypes of all probes classified as "1" in the "BestProbeset" field. Map file is created using SNP names (please read "Axiom genotyping solution data analysis guide" for further information).

**-e** or **--editplink** [DEFAULT: PMN ]
This option allows the user to edit the SNP probe classes. Affymetrix SNPolisher R package currently classifies SNP probes into 6 classes: "PolyHighResolution" (P), "MonoHighResolution" (M), "NoMinorHomozygote" (N), "OTV" (O), "CallRateBelowThreshold" (C) and, "Other" (T).
Any of the 6 SNP probe classes added after this option will be retained. If both probes of the same SNP carry the retained class(es), then only the one classified as "BestProbeset" will be retained.
The default option retains all SNP probesets that are classified as PolyHighResolution, MonoHighResolution and NoMinorHomozygote.

**-q** or **--quiet** [DEFAULT: loud (it's an italian software! :) )]
This option avoids showing runtime messages to stdout.

#### *Output files and folders*
Unless differently specified by the user, all output files will be written in a directory named OUTPUT, placed in the same directory where AffyPipe is run.
A number of files will be present in the OUTPUT folder, and most of them will be gzipped:
 - **apt-[program].log**: These are the logs of the APTools programs. 
 - **AxiomGT1.[xxx].txt**, **cc-chp folder**, **metrics.txt**,**qc-report.txt**: These are the true outputs of the APTools suite of programs. The (raw) genotypes are in the "calls" file. For specific information on each of these files, please read Affymetrix's "Axiom genotyping solution data analysis guide" and "Best practice supplement to Axiom genotyping solution data analysis user guide". Some are gzipped to reduce memory usage in your computer.
 - **celfile_DQClean.txt** and **celfile_DQClean_CRclean.txt'**: These are runtime files created by the pipeline after the different QC steps. DQClean refers to "Dish-QC" clean celfiles, and DQClean_CRclean refers to "Dish-QC" and "Call-Rate" clean cel files.
 - **LOWQUAL_ELIMids.txt**: This file contains the (CEL) ids of the individuals excluded by the APTools in the different stages.
 - **SNPol.R** and **SNPol.Rout**: Program (and I/O output) used to run SNPolisher R package.
 - **output folder**: This folder contains the output of the SNPolisher R package. You might want to have a look at the "Ps.performance.txt" file, which contains the summary of all the QC run on probes. For specific information on each of these files, please read Affymetrix's "Axiom genotyping solution data analysis guide" and "Best practice supplement to Axiom genotyping solution data analysis user guide". 
 - **Axiom_genotypes_PLINKfmt.[ped/map] (if requested)**: These files contain all SNP genotypes (choosing best probes for each SNP from "Ps.performance.txt") in PLINK format, recoding genotypes as: 0:'B/B', 1:'A/B', 2:'A/A','-1':'0/0'.

### **4) Other species**
The AffyPipe is intended for all livestock Axiom users, and coded following a general intention of expanding it to multi-species users. However, please note that this was built originally for the specific needs of the International Buffalo Genome Consortium (Iamartino et al.,2013). No CEL files for other species were available to us. Since *"In God we trust, all others bring data" (Deming)* rule applies, a specific option to switch to other species was not *directly* included. In any case, most probably you'll only have to modify just 2 (or 1?) line(s) of code, and that's it.
So, if you're analysing a non-buffalo species, please contact the author of this pipeline at: ezequiel [dot] nicolazzi [at] tecnoparco [dot] org, and he'll be very happy to help you (and integrate the necessary changes in this tool!).
 
### **5) References**

 - Iamartino D, Williams JL, Sonstegard T, Reecy J, Van Tassell C, Nicolazzi EL, Biffani S, Biscarini F, Schroeder S, de Oliveira DAA, Coletta A, Garcia JF, Ali A, Ramunno L, Pasquariello R, Drummond MG, Bastianetto E, Fritz E, Knoltes J and the International Buffalo Consortium (2013). The buffalo genome and the application of genomics in animal management and Improvement. Buffalo Bulletin, Vol. 32, Spec. Issue 1, 2013, pp.151-158.

 - Purcell S, Neale B, Todd-Brown K, Thomas L, Ferreira MAR, Bender D, Maller J, Sklar P, de Bakker PIW, Daly MJ & Sham PC (2007) PLINK: a toolset for whole-genome association and population-based linkage analysis. American Journal of Human Genetics, 81.

### **Disclaimer**
AffyPipe is a free tool that uses proprietary software that is publicly available online: you can redistribute this pipeline and/or modify this program, but at your own risk. AffyPipe is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details: http://www.gnu.org/licenses/.
This pipeline is for research and has not a commercial intent, but it can be used freely by any organization. The only goal is to help people streamline their work. Affymetrix is not responsible of any aspect regarding this pipeline. The author of this pipeline is not responsible for ANY output, modification or result obtained from it.
For bug report, feedback and questions (PLEASE read the carefully this README file before sending your question) contact ezequiel [dot] nicolazzi [at] tecnoparco [dot] org.
