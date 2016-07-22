AffyPipe: _an open-source pipeline for Affymetrix Axiom genotyping workflow_
=========
ref: E.L. Nicolazzi (Fondazione Parco Tecnologico Padano) - Via Einstein, Loc. Cascina Codazza (26900) Lodi (Italy).
     email: ezequielluis [dot] nicolazzi [at] gmail [dot] com



#### IMPORTANT WARNING FOR AXIOM apt2 USERS
<font color=red><b>Please note that a new series of library files are being released in many species. Most of these files carry the extention "apt2.xml". Please note AffyPipe will not run with these files. I have tried to contact Affymetrix's DevNet several times now, but their support has not been helpful. At all. I will keep on trying to understand why on earth they keep changing their software, inputs and outputs, and how to make this new software work. Please be patient, as this issue is not due to AffyPipe but for a sudden (and hardly documented) change in Affymetrix software. Please know that the windows GUI software works with these library files, so I'm going to write something I never thought I would: 'If you have a windows computer at hand, please use it. It'll take you less time and mental energy to use the Windows GUI rather than trying to understand how to make the Linux/Mac versions work'.

I am truly sorry, but my hands are tied here.

Hope to get back to you with good news, but for the moment AffyPipe is in the garage.

Ezequiel L. Nicolazzi
</b></font>


### **What is AffyPipe?**
The goal of this pipeline is to authomatize Affymetrix's standard and "best practice" genotyping workflows for Linux and Mac users: from Power tools (APTools) to SNPolisher R package.
This is a one-step tool that combines all Affymetrix software and produces edited and user-friendly format output files. In fact, AffyPipe allows you to edit SNP probe classes directly while exporting genotypes in PLINK format (Purcel et al, 2007).
It was originally built for the **International Buffalo Genome Consortium** (Iamartino, 2013), but now is able to handle all species (e.g. human, cow, chichen, fisheries).
Users are strongly adviced to read carefully Affymetrix's "Axiom genotyping solution data analysis guide" and "Best practice supplement to Axiom genotyping solution data analysis user guide" before using this tool. 

### **0) AffyPipe publication & how to cite**
The AffyPipe publication can be found in: http://www.ncbi.nlm.nih.gov/pubmed/25028724

If you used this pipeline for your analysis, please cite: **Nicolazzie EL, Iamartino D, Williams JL (2014). AffyPipe: an open-source pipeline for Affymetrix Axiom genotyping workflow. Bioinformatics, DOI: 10.1093/bioinformatics/btu486**

Thanks in advance!

### **1) Getting the pipeline, and requirements**
The fastest and more clever way of getting this pipeline and all accessory files is installing git and cloning this repository.
Further information on how to install git on Linux and Mac can be found at: http://git-scm.com/book/en/Getting-Started-Installing-Git . An example of cloning command using command line is: 

    % git clone --recursive https://github.com/nicolazzie/AffyPipe.git

The AffyPipe pipeline is for users running **Linux/Unix** and **Mac** operative systems, and only runs over 64bit processors. **Windows users should use Gentoyping Console (TM) Software, which already cover all of these functionalities!!!** 
You should have Python (2.x) and R (any version?) already installed on your computer (Mac users have python already installed by default). The whole pipeline was thoroughly tested under Python 2.7.6 and R 3.0.

**IMPORTANT**: Since Cygwin uses a twisted way of building linux-like (?) paths, AffyPipe may not work properly. We **strongly** suggest using a virtual machine (e.g. VirtualBox) with ubuntu (or similar), instead of Cygwin. A tip: if you *really* want to use Cygwin (why would you?!?!?), please know that you should use *relative* paths for all the folders and files involved. Absolute paths will not work.


### **2) Folders and files required**
The Affymetrix genotyping workflow requires several Affymetrix files to run. For simplicity, all these files are expected to be placed into one folder.
The default folder names and values specified below are provided as example. However, please note these names and values are also default in AffyPipe (see "Options" paragraph in Section 3).

All Affymetrix files are downloadable at their website (http://www.affymetrix.com).
Please remember that you need to register to be able to download all the files below!
**NOTE: If you cloned or downloaded all the folders in this repository, you'll see example names of the files you need for the Buffalo species. All files are empty: i)to avoid copyright issues with Affymetrix and; ii) to force you downloading the latest version of all the files and softwares.**

 - **2.a.)** _AFFYTOOLS_ folder: All data downloaded from Affymetrix website is placed here. Essentially 4 different files are needed (2.a.1, 2.a.2.1 + 2.a.2.2, and 2.a.3). 
  - **2.a.1)** Go to: Products > Microarray Solutions > DNA Analysis Solutions > Agrigenomics Solutions > Arrays > Species > Buffalo/[other species], and download the file under *Library Files* section.  For the buffalo it is **Axiom® Buffalo Analysis Files.r[X].zip**, for cow **Axiom_GW_bos_snp_1_r[X].zip**, where [X] stands for the version of the Analysis Files. Please uncompress this file and you'll get a lot of "Axiom_[species].[X].[blablabla] files.
  - **2.a.2)** Go to: Partners & Programs > Developers' Network > DevNet Tools. Inside there you'll find:
      - **2.a.2.1)** Affymetrix PowerTools (APTools): Here you should download the right file for your operative system (something like **APT[X] Linux 64 bit x86 binaries** or **APT [X] Mac OS-Lion 64-bit Intel Binaries**). Note: This pipeline was tested on both OSs. If you're using Mavericks OS, no worries, it will run ok. Please uncompress this folder (inside AFFYTOOLS, if you like).
      - **2.a.2.2)** **SNPolisher**: An R package for post-processing array's results. Please uncompress this folder (inside AFFYTOOLS, if you like). **WARNING:** (Sept. 2014) Affymetrix has updated its SNPolisher package to v1.5.0, deprecating some functions. It is compulsary you update your SNPolisher (otherwise the program will stop!). If you have older versions of SNPolisher installed, please either delete them or install the new version on your own BEFORE running Affypipe!**
  - **2.a.3)** Annotation file: You will receive an annotation file from Affymetrix along with your genotypes. However, since data is updated constantly, the download of the latest annotation file is **STRONGLY** recommended. By doing this, even if you analyse samples in different times, you'll be sure of using the latest map information! You can find this in: Products > Microarray Solutions > DNA Analysis Solutions > Agrigenomics Solutions > Arrays > Species > Buffalo[/Bovine or other species]. There, under *Current NetAffx Annotation Files* section, download the file **Axiom_Buffalo Annotations, CSV format** (for buffalo) or **Axiom_GW_Bos_SNP_1.na[X].annot, CSV format** (for cow). Please remember to uncompress the file and put it inside AFFYTOOLS folder. **IMPORTANT: Please check your annotation file contains the following variables in the header (e.g. first row after a series of lines with leading '#'): "Probe Set ID","Affy SNP ID","Chromosome","Physical Position","Allele A","Allele B". Note that if any of these is not present (or is written differently) the program will stop before running SNPolisher!!**

 
 - **2.b)** *a CEL list file*: All Affymetrix Power Tools programs need a file containing a list of CEL files (raw data) to be analysed. Fortunately, using AffyPipe you will have to do this just once! It is highly recommended that you provide also the full path to the .CEL files. Just remember that *CEL list files* need a compulsary header row: "cel_files". If such header is missing, AffyPipe will stop, since APTools programs cannot run without that header!. 
To help you here, a small bash program called "createcelfile.sh" is also provided. The program *actually creates* the CEL list files for you. You only have to place this program in the directory where the .CEL files are stored, and run it. This creates a "mycellistfile.txt" file (your CEL list file!), that you can rename and put wherever you want (e.g. in the main folder?).
To run this program:

    % chmod 755 createcelfile.sh && ./createcelfile.sh 

    A short explanation for those not used to command line: **chmod 755 createcelfile.sh** means that you are giving all access rights (read/write/execute) to your user + read/execute rights to all other users. You actually need to do this just once!; **&&** means something like "after you have succeeded doing the thing on the left, do the thing on the right"; **./createcelfile.sh** this command actually launches the program.  

 - **2.c)** *a PARAM_species.inp file*: This file is already provided, and you should NOT change the name of the file! However, you need to edit it, based on the array/species you're going to analyse. Thanks to this file, AffyPipe can be used by any species genotyped with Affymetrix Axiom technology! **Please note that testing has been carried out only on Buffalo + Human Exome 319 and EUR Axiom datasets (GEO platforms: GPL18760 and GPL52691).** In this file you need to edit 3 parameters:
    - *SPEC_prefix=* : This is the prefix of your species file. Search for the file "*apt-geno-qc.AximQC1.xml". Prefix is whatever comes before the first dot. For example: in "**Axiom_Buffalo**.r2.apt-geno-qc.AxiomQC1.xml", prefix is "Axiom_Buffalo""
    - *SPEC_version=* : This is the release of the library. Usually is specified as "r[number]". For example: in "Axiom_Buffalo.**r2**.apt-geno-qc.AxiomQC1.xml", version is "r2".
    - *SPEC_annotation=* : This is Affymetrix's annotation file for the selected species. PLEASE NOTE that this file should be placed in the AFFYTOOLS (or whatever you call it) directory!! E.g. if "MasterCsvAnnotationFile.r1.txt" is speficied for buffalo, program will search for the file: AFFYTOOLS/MasterCsvAnnotationFile.r1.txt
    
Once you have finished, if you named folders as default , you should have:
  - A main folder (where AffyPipe.py is)
  - 1 sub-folder (AFFYTOOLS -**2.a.**)
      - A bunch of files (library) 
      - 2 folders (e.g. *SNPolisher_package* and *apt-[sometext_yourversion]*)
      - An annotation file (uncompressed)
  - A .CEL list file (somewhere... I place it usually in the main folder).
  - A PARAM_species.inp file (placed where AffyPipe.py is)

### **3) Running AffyPipe.py**

AffyPipe is very versatile, thanks to a number of options you can set up. Default behavior runs Affymetrix Standard workflow, but you can choose to perform "Best Practice" workflow (see "-b" option), that includes an extra PlateQC step (please see: "Best practice supplement to Axiom genotyping solution data analysis user guide" for further details). There are two *compulsary* information for Affypipe: 1) the name (and path) of the cel list file (e.g. the one you created with createcelfile.sh) and; 2) the parameter file (PARAM_species.inp). You can find a long explanation of AffyPipe options below in the "Option" section or a short and handy version by typing:

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

**NOTE:** The first time you run AffyPipe, please note that you have to have administrator permissions to allow AffyPipe install SNPolisher package. If you do not want an authomatic installation (or simply don't feel like giving "sudo" permissions to a script coded by someone else's), please install SNPolisher _prior_ to run AffyPipe with the following code (on your terminal, with admin permissions, write "R" and press enter, then write) :

    % install.packages('[your path to file: SNPolisher[[version]].tar.gz]',repos=NULL,type='source')

This command will install the package on your R library, so it will automatically recognize it!


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

**-o [PATH]** or **--outdir=[PATH]** [DEFAULT: ./OUTPUT]
This option can be used to choose path and name of the output folder where all output files will be written. If the folder does not exists, a new folder will be created with the given name.

**-d VALUE 0>=1** or **--dqc=VALUE 0>=1** [DEFAULT: 0.82]
This option can be used to set a user defined Dish_QC threshold. Default here is Affymetrix's best practice default. See their "Axiom genotyping solution data analysis guide" and "Best practice supplement to Axiom genotyping solution data analysis user guide" for further details.

**-c VALUE 0>=1** or **--crate=VALUE 0>=1** [DEFAULT: 0.97]
This option can be used to set a user defined call rate threshold. Default here is Affymetrix's best practice default. See their "Axiom genotyping solution data analysis guide" and "Best practice supplement to Axiom genotyping solution data analysis user guide" for further details.

**-y** or **--summary** [DEFAULT: no summaries files]
This option allows to output the summary information of the genotyping process. Please note that these files are VERY large. Since the general user does not usually uses this file, the default is not printing this out. However, there are several occasions where the analysis of this file could be useful, thus an option to output this file was included.

**-b** or **--bestpractice** [DEFAULT: STANDARD workflow]
This option enhances the Best Practice workflow, adding an extra step between the two apt-genotype steps, for plate QC. Please be sure of reading "Best practice supplement to Axiom genotyping solution data analysis user guide" before choosing this option. If this option is chosen, please note that **PLATE INFORMATION FILE IS REQUIRED**. When running the "Best Practice" workflow, AffyPipe will require a file linking samples to plates. See the required (in this case) -f or --platefile option for more information.

**-f** or **--platefile** [DEFAULT: NONE] 
This option is **required** if **-b** option is present. This file has to contain 2 columns, comma or tab separated (or a combination of two if you want to be extra-triky!): first field has to be the name of the sample (e.g. exaclty as it is specified in the CEL list file, with or without the path, with or without the ".CEL" specification) and the second must be the plate ID. Please note that you can simply copy the CEL list file and add a field naming plates. You can name plates any way you want, just be aware that names are case-sensitive, thus PLATE and plate are considered different plates!!
For example, the following are all acceptable specifications for "animalnumber1":
 - */home/Affydata/animalnumber1.CEL    plate1* (note there is a tab separating both fields)
 - */home/Affydata/animalnumber1.CEL,plate1*
 - */home/Affydata/animalnumber1,plate1*
 - */home/Affydata/animalnumber1    plate1* (note there is a tab separating both fields)
 - *animalnumber1.CEL,plate1*
 - *animalnumber1,plate1*

**-l** or **--plateqc** [DEFAULT: 0.95,0.99] 
This option is considered only if **-b** option is present. It allows to change Plate QC thresholds for PlatePassRate and AverageCallRate, respectively. Note that these values MUST BE comma separated, and both must be provided.

**-p** or **--plink** [DEFAULT: no plink output]
This option outputs (all) *BestProbeset* SNPs in PLINK format, coding alleles as A B. The pipeline just goes through the Ps.performace.txt (output) file keeping genotypes of all probes classified as "1" in the "BestProbeset" field. Map file is created using SNP names (please read "Axiom genotyping solution data analysis guide" for further information).

**--plinkACGT** [DEFAULT: no plink output]
This option is an alternative to -p or --plink option, with the only difference that it codes alleles in ACGT instead of AB. This option was suggested (and code provided) by GitHub user Hyunmin (@hmkim). Thank you!

**-e** or **--editplink** [DEFAULT: PMN ]
This option allows the user to edit the SNP probe classes. Affymetrix SNPolisher R package currently classifies SNP probes into 6 classes: "PolyHighResolution" (P), "MonoHighResolution" (M), "NoMinorHomozygote" (N), "OTV" (O), "CallRateBelowThreshold" (C) and, "Other" (T).
Any of the 6 SNP probe classes added after this option will be retained. If both probes of the same SNP carry the retained class(es), then only the one classified as "BestProbeset" will be retained.
The default option retains all SNP probesets that are classified as PolyHighResolution, MonoHighResolution and NoMinorHomozygote.

**--debug** [DEFAUL: OFF ]
This option prints a full report on each step of the APT process. This option is useful if the program stops or gives any error message. Please run the program with this flag before reporting anything to the author, to help him identify the problem as soon as possible!

**-q** or **--quiet** [DEFAULT: loud (it's an italian software! :) )]
This option avoids showing runtime messages to stdout.

#### *Examples*
The following are just illustrative examples of commands to run the AffyPipe for typical situations. Please note that name files and paths are arbitrary (e.g. you should provide your own names/paths)

1)Run a standard workflow, using default QC values and get genotypes on Affymetrix's standard format

    % python AffyPipe.py mycellistfile.txt

2)Run a standard workflow, use own QC values and get genotypes in PLINK format (default probe QC extraction).
  
    % python AffyPipe.py mycellistfile.txt -d 0.90 -c 0.99 -p
    
3)Run a "best practice" workflow, use own QC values (default plate setting) and get best probes for "PolyHighRes" and "MonoHighRes" classes in PLINK format, coding alleles as AB (use --plinkACGT to code alleles in ACGT format). 
    
    % python AffyPipe.py mycellistfile.txt -d 0.90 -c 0.99 -b -l 0.99,0.99 --plink -e PM

#### *Output files and folders*
Unless differently specified by the user, all output files will be written in a directory named OUTPUT, placed in the same directory where AffyPipe is run.
A number of files will be present in the OUTPUT folder, and most of them will be gzipped:
 - **apt-[program].log**: These are the logs of the APTools programs. 
 - **AxiomGT1.[xxx].txt**, **cc-chp folder**, **metrics.txt**,**qc-report.txt**: These are the true outputs of the APTools suite of programs. The (raw) genotypes are in the "calls" file. For specific information on each of these files, please read Affymetrix's "Axiom genotyping solution data analysis guide" and "Best practice supplement to Axiom genotyping solution data analysis user guide". Some are gzipped to reduce memory usage in your computer.
 - **celfile_DQClean.txt** and **celfile_DQClean_CRclean.txt'**: These are runtime files created by the pipeline after the different QC steps. DQClean refers to "Dish-QC" clean celfiles, and DQClean_CRclean refers to "Dish-QC" and "Call-Rate" clean cel files.
 - **LOWQUAL_ELIMids.txt**: This file contains the (CEL) ids of the individuals excluded by the APTools in the different stages.
 - **SNPol.R** and **SNPol.Rout**: Program (and I/O output) used to run SNPolisher R package.
 - **output folder**: This folder contains the output of the SNPolisher R package. You might want to have a look at the "Ps.performance.txt" file, which contains the summary of all the QC run on probes. For specific information on each of these files, please read Affymetrix's "Axiom genotyping solution data analysis guide" and "Best practice supplement to Axiom genotyping solution data analysis user guide". 
 - **Axiom_genotypes_PLINKfmt.[ped/map] (if requested)**: These files contain all SNP genotypes (choosing best probes for each SNP from "Ps.performance.txt") in PLINK format, recoding genotypes as: 0:'A/A', 1:'A/B', 2:'B/B','-1':'0/0' or their respective alleles if --plinkACGT option is requested.

### **4) Different species**
The AffyPipe is intended for all species gentoyped with the Axiom technology, although it was originally built for the specific needs of the International Buffalo Genome Consortium (Iamartino et al.,2013). **Please note that testing has been carried out only on Buffalo + Human Exome 319 and EUR Axiom datasets (GEO platforms: GPL18760 and GPL52691).** Just by setting up the parameter file, you should be successful in using this tool on any other non-tested species. In case of problems, please contact the author of this pipeline at: ezequielluis [dot] nicolazzi [at] gmail [dot] com, and he'll be very happy to help you (and integrate the necessary changes in this tool!).
 
### **5) References**

  - Affymetrix, Genotyping solution analysis guide (2014). http://www.affymetrix.com/support/downloads/manuals/axiom_genotyping_solution_analysis_guide.pdf
 
  - Affymetrix, Best practice analysis guide (2014). http://www.affymetrix.com/support/downloads/manuals/axiom_best_practice_supplement_user_guide.pdf

  - Iamartino D, Williams JL, Sonstegard T, Reecy J, Van Tassell C, Nicolazzi EL, Biffani S, Biscarini F, Schroeder S, de Oliveira DAA, Coletta A, Garcia JF, Ali A, Ramunno L, Pasquariello R, Drummond MG, Bastianetto E, Fritz E, Knoltes J and the International Buffalo Consortium (2013). The buffalo genome and the application of genomics in animal management and Improvement. Buffalo Bulletin, Vol. 32, Spec. Issue 1, 2013, pp.151-158.

  - NCBI GEO, Platform GPL18760 (2014a). http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL18760

  - NCBI GEO, Platform GPL52691 (2014b). http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE52691

  - Purcell S, Neale B, Todd-Brown K, Thomas L, Ferreira MAR, Bender D, Maller J, Sklar P, de Bakker PIW, Daly MJ & Sham PC (2007) PLINK: a toolset for whole-genome association and population-based linkage analysis. American Journal of Human Genetics, 81.


### **6) Acknowledgments**
This work was supported by the Italian Ministry of Education, University and Research, project GenHome [D.M. 505/Ric]; and the European Union's Seventh Framework Programme, project Gene2Farm [G.A. 289592].
I personally thank Hernan Morales Durand (IGEVET, Argentina) and GitHub user Hyunmin (@hmkim) for suggestions (and code) provided to improve this tool.


### **Disclaimer**
AffyPipe is a free tool that uses proprietary software that is publicly available online: you can redistribute this pipeline and/or modify this program, but at your own risk. AffyPipe is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details: http://www.gnu.org/licenses/.
This pipeline is for research and has not a commercial intent, but it can be used freely by any organization. The only goal is to help people streamline their work. Affymetrix is not responsible of any aspect regarding this pipeline. The author of this pipeline is not responsible for ANY output, modification or result obtained from it.
For bug report, feedback and questions (PLEASE read the carefully this README file before sending your question) contact ezequielluis [dot] nicolazzi [at] gmail [dot] com.
