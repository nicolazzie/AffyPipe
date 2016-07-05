"""
Program that automatically runs Affymetrix APT and SNPolisher programs for MAC and Linux users.
Original version: Ezequiel L. Nicolazzi (Fondazione Parco Tecnologico Padano, Italy), March 2014.
Changes:
   -May 2014 (ELN): Excluded summary info of default. Direct MAP name.
                    Included editing of SNP probe classes for PLINK format.
   -Jun 2014 (ELN): Included BestPractice capabilities (option)
                    Added checks on user input of numbers and range.
                    Added some useful options in apt scripts
                    Now reading a param file to allow multiple-species analyses.
   -Jul 2014 (ELN): Exclude collector lib.,specific to Python2.7 (doing the same, less fancier now)
   -Sep 2014 (ELN): Updated SNPolisher scripts, adapted to 1.5.0 (only!) Thankyou Hernan Morales Durand (IGEVET, Argentina)
   -Dec 2014 (ELN + Hyunmin - GitHub user @hmkim): Added the possibility to output PLINK file with ACTG alleles (new option)
   -Feb 2015 (ELN): Added a new header for MasterCsvAnnotationFile(s) + added a bomb if probes==0. Thankyou Hamdy Abdel-Shafy (Cairo UNI, Egypt)
                    Changed stop for warning when Affy files missing. Thankyou Jenny C. Armstrong!
   -Mar 2015 (ELN): Previous edit was not effective, since Affy annotation files change A LOT in the different species. This version should fix that.
                    Added a --debug option to help me during troubleshooting.
                    MAJOR BUG solved for option --plinkACGT. Allele code for AA AB and BB were switched! Thank you Ryan Hillary (Standford Uni, UK)!
   -Mar 2015 (ELN): Corrected a bug in call rate procedure (Thank you user bbib!)
                    Moved control of Annotation file to start of pgm to avoid these issues stopping the program at the end.
   -Jun 2016 (ELN): Deactivated BESTPRACTICE without accessory file provided (default behaviour created only problems to users).

For bug report/comments: ezequielluis.nicolazzi@gmail.com
"""
import sys,os,time
from optparse import OptionParser
import subprocess as sub

################################################
### Useful defs
################################################
# Prints (if required) and writes the log 
def logit(msg):
    global VER
    if VER:print(msg)
    log.write(msg+'\n')

# This stops the pipeline when something BAD happens
def bomb(msg):
    logit('\n\n[BAD NEWS]: '+msg+'\n')
    print "*"*60
    print "Program stopped because of an error. Please read .log file"
    print "*"*60
    sys.exit()

def check_range(inp,option):
    try: 
        val=float(inp)
    except ValueError:
        logit('ERROR in %s: %s is not a number and it should be!' % (option,inp))        
        sys.exit()
    if val<0 or val>1:
        logit('ERROR in %s: %s is not in the range between 0 and 1, and it should be!' % (option,inp))        
        sys.exit()

##########################################
### Main (and raw) system check
##########################################
# Open .log file to store all the info
log=open(sys.argv[0].strip().split('.')[0]+'.log','w')
VER=False

# Extract environment info (system and memory) to try avoiding some sys-dpd errors. ############
SYS = sub.Popen(["uname -s"], shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readline().strip()
ARC = sub.Popen(["uname -m"], shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readline().strip()

if SYS=='Darwin':
    APTools='/apt-1.18.0-x86_64-apple-lion/'
    logit('Recognised a MACOSx system')
else: 
    APTools='/apt-1.18.0-x86_64-intel-linux/'
    logit('Recognised a Linux system')

if '64' in ARC:
    logit('Recognised a 64 bit architecture')
else:
    bomb("Architecture should be 64bit. Please check your computer is 64bit.")

################################################
### Options parser
################################################
HERE = sub.Popen(["pwd"], shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readline().strip()
usage = "usage: %prog [options] cel_list_file"
parser = OptionParser(usage=usage)

parser.add_option("-t","--tooldir", dest="DIRXML", default=HERE+'/AFFYTOOLS/',
                  help="write path to AFFYTOOLS directory", metavar="<PATH>")
parser.add_option("-a","--aptdir", dest="DIRAPT", default=HERE+'/AFFYTOOLS/'+APTools,
                  help="write path to APT programs directory", metavar="<PATH>")
parser.add_option("-s","--SNPolisher", dest="DIRSNP", default=HERE+'/AFFYTOOLS/SNPolisher_package',
                  help="write path to SNPolisher directory", metavar="<PATH>")
parser.add_option("-o","--outdir", dest="DIROUT", default=HERE+'/OUTPUT/',
                  help="write path to output directory (if not found will create one)", metavar="<PATH>")
parser.add_option("-d","--dqc", dest="DQC", default='0.82',
                  help="dish QC threshold. Ind. with DQC<threshold will be excluded", metavar="VALUE 0>=1")
parser.add_option("-c","--crate", dest="CR", default='0.97',
                  help="call rate threshold. Ind. with CR<threshold will be excluded", metavar="VALUE 0>=1")
parser.add_option("-y","--summary", action="store_true", dest="SUMM", default=False,
                  help="outputs the summaries files (large mem!) of genotyping proc")
parser.add_option("-b","--bestpractice",action="store_true",dest="BEST", default=False,
                  help="Uses BEST PRACTICE workflow protocol (performs PlateQC)")
parser.add_option("-f","--platefile", dest='Pfile',default=0,
                  help="Plate IDs accessory file (BESTPRACTICE only)",metavar="<FILE>")
parser.add_option("-l","--plateqc", dest='PQC',default='0.95,0.99',
                  help="Plate QC for PlatePassRate and AvgCallRate (BESTPRACTICE only).",metavar="VALUE 0>=1,VALUE 0>=1")
parser.add_option("-p","--plink",action="store_true", dest="PLINK", default=False,
                  help="outputs (all) BestProbeset SNPs in PLINK format - A B alleles")
parser.add_option("--plinkACGT",action="store_true", dest="PLINKacgt", default=False,
                  help="outputs (all) BestProbeset SNPs in PLINK format - A C G T alleles")
parser.add_option("-e","--editplink", dest='EDITPLINK',default='PMNx',
                  help="Edit options (only if -p is specified). See README file for more info", metavar="PMNOCT")
parser.add_option("--debug", action="store_true",dest='DEBUG',default=False,
                  help="Use this option to create a more informative .log if something does not work")
parser.add_option("-q","--quiet",action="store_false", dest="VER", default=True,
                  help="Avoid showing runtime messages to stdout")
(opt, args) = parser.parse_args()

## Some useful (unchainged parameters)
VER=opt.VER
APT_progs=('apt-geno-qc','apt-probeset-genotype')
PARAM_FILE='./PARAM_species.inp'

########################################################
# IMPORT SPECIES PARAM file (selects library files)
########################################################
# Reads parameters in PARAM_species.inp file and runs a simple check for a required file.
# Second, check if param file is there. We will check contents after.
if not os.path.exists(PARAM_FILE):
    bomb("Param file not found on this directory. Looking for ./PARAM_species.inp failed !!")
else:
    Spfix=0;Sver=0;Smap=0
    for line in open(PARAM_FILE):
        if '#' in line:continue
        if not 'SPEC_' in line:continue
        if 'SPEC_prefix' in line:
            Spfix=line.split('=')[1].strip().split()[0].strip()
        if 'SPEC_version' in line:
            Sver=line.split('=')[1].strip().split()[0].strip()
        if 'SPEC_annotation' in line:
            Smap=opt.DIRXML+'/'+line.split('=')[1].strip().split()[0].strip()
            for line in open(Smap):
                if '#' in line[0] or len(line)<50:continue  #Avoids issues caused by Affy's different headings and formats
                line=line.replace('"','').replace("'","")
                if len(line.strip().split('\t')) > 5: he=line.strip().split('\t')
                elif len(line.strip().split(',')) > 5:he=line.strip().split(',')
                elif len(line.strip().split(';')) > 5:he=line.strip().split(',')
                else: he=line.strip().split()
                okhead=('Probe Set ID','Affy SNP ID','Chromosome','Physical Position','Allele A','Allele B')
                for oktxt in okhead:
                    if not oktxt in he: bomb("Header in annotation file: "+Smap+" does not contain required variable '"+oktxt+"' - Please change manually!")
                break
    if not Spfix or not Sver or not Smap:
        bomb("Ooopsss, something went wrong with the reading of param file. Please check the file are retry!")
    if not os.path.exists(opt.DIRXML+'/'+Spfix+'.'+Sver+'.apt-geno-qc.AxiomQC1.xml'):
        bomb('Looking for '+Spfix+'.'+Sver+'.apt-geno-qc.AxiomQC1.xml in '+opt.DIRXML+' FAILED! Please check PARAM file!')
    if not os.path.exists(Smap):
        bomb('Looking for '+Smap+' FAILED! Please check PARAM file!')

SPEC_axfiles=[Spfix+'.'+Sver+'.apt-geno-qc.AxiomQC1.xml',\
              Spfix+'_LessThan96_Step1.'+Sver+'.apt-probeset-genotype.AxiomGT1.xml',\
              Spfix+'_96orMore_Step1.'+Sver+'.apt-probeset-genotype.AxiomGT1.xml',\
              Spfix+'_LessThan96_Step2.'+Sver+'.apt-probeset-genotype.AxiomGT1.xml',\
              Spfix+'_96orMore_Step2.'+Sver+'.apt-probeset-genotype.AxiomGT1.xml']

#######################################################
### Print and check options before running the program
#######################################################
logit('\n'+'*'*81+'\n==> PROGRAM STARTS: '+time.strftime("%B %d, %Y - %l:%M%p %Z")+'\n'+'*'*81)

# First of all, check if CEL list file is provided and exists. Check for header, and keep a list of all individuals 
if len(args)!=1: bomb("Providing a .cel list file  is compulsary! Please run: python "+sys.argv[0]+" -h, for help.")
if not os.path.exists(args[0]): bomb("CEL list file not found!!! I looked for file: "+args[0])
allfile=open(args[0],'r').readlines()
header=allfile[0].strip()
if header!='cel_files':bomb("The first row of CEL list file has to be 'cel_files', but is: "+header)
tut =[allfile[i].split('/')[-1].split('.')[0] for i in range(1,len(allfile),1)]  

# IF BESTPRACTICE, check for presence of Plate# or accessory file (if specified). In addition checks consistency of file
if opt.BEST:
    if len(opt.PQC.strip().split(','))!=2:bomb('Option -l needs 2 comma separated fields! E.g. 0.95,0.99 -> You provided: '+opt.PQC)
    if opt.Pfile and not os.path.exists(opt.Pfile):bomb('Plate ID accessory file specified: '+opt.Pfile+' not found!')
    animplate={}
    for i in tut:animplate[i]=0
    if not opt.Pfile: bomb('Plate ID accessory file is required when performing BESTPRACTICE')
    ## IF Plate file is provided, get and retain individuals ID and plate links
    plates={}
    temp=[]
    for line in open(opt.Pfile):
        if 'cel_files' in line:continue
        data=line.replace('\t',',')
        data=data.strip().split(',')
        if '.CEL' in data[0]:anim=data[0].split('/')[-1].split('.')[0].strip()
        else:anim=data[0].split('/')[-1].strip()
        if not animplate.has_key(anim):
            bomb('Individual: '+anim+' present in PLATE ID accessory file, but not in CEL list file!')
        pla=data[1].strip()
        animplate[anim]=pla
        temp.append(pla)
    plates=[(i,temp.count(i)) for i in set(temp)]
#    else:             ## IF default behavior, get and retain individuals ID an plate links (DEACTIVATED)
#        temp=[tut[i][:-4] for i in range(len(tut))]
#        for en,i in enumerate(tut):animplate[i]=temp[en]
#        plates=[(i,temp.count(i)) for i in set(temp)]

# Print options and params
logit('-'*81+'\n==> CEL FILE INFORMATION READ \n'+'-'*81)
if opt.BEST:
    if opt.Pfile:logit('%-30s %-s' % ('Plate specification file:',opt.Pfile))
    else:logit('%-30s %-s' % ('Plate specification file:',"not provided (using default behavior)"))
    logit('%-30s %-s' % ('Total # of individuals read:',len(tut)))
    logit('%-30s %-s' % ('Total # of plates identified:',len(plates)))
    logit('%-40s' % ('Specifically: (Plate#. PlateID: #individuals)'))
    for en,it in enumerate(plates):logit('               Plate%s. %-s: %s' % (str(en+1),it[0],it[1]))
else:
    logit('%-30s %-s' % ('Total # of individuals read:',len(tut)))
logit('')
logit('-'*81+'\n==> PARAMETERS OF THE PROGRAM \n'+'-'*81)
logit('%-30s %-s' % ('CEL list file used:',args[0]))
logit('%-30s %-s' % ('AFFYTOOLS directory:',opt.DIRXML))
logit('%-30s %-s' % ('APT programs directory:',opt.DIRAPT))
logit('%-30s %-s' % ('SNPolisher directory:',opt.DIRSNP))
logit('%-30s %-s' % ('Axiom annotation file:',Smap))
logit('%-30s %-s' % ('Output directory:',opt.DIROUT))
logit('%-30s %-s' % ('Dish-QC threshold used:',opt.DQC))
logit('%-30s %-s' % ('Call rate threshold used:',opt.CR))

# Checks if summary file is required
if opt.SUMM:logit('%-30s %-s' % ('Summary genotyping files:','REQUIRED'))
else:logit('%-30s %-s' % ('Summary genotyping files:','NOT REQUIRED'))

# Checks if BEST PRACTICE workflow is required. Checks also presence of options
if opt.BEST:
    logit('%-30s %-s' % ('Type of workflow required:','BEST PRACTICE'))
    logit('%-30s %-s' % ('  - PlatePassRate threshold:',opt.PQC.strip().split(',')[0]))
    logit('%-30s %-s' % ('  - AvgCallRate   threshold:',opt.PQC.strip().split(',')[1]))
else:logit('%-30s %-s' % ('Type of workflow required:','STANDARD'))

# Checks PLINK and edit options
if opt.PLINK or opt.PLINKacgt:
    if opt.PLINK:
        logit('%-30s %-s' % ('Genotype file format:','PLINK - AB alleles'))
    else:
        logit('%-30s %-s' % ('Genotype file format:','PLINK - ACGT alleles'))
    if opt.EDITPLINK=='PMNx':
        oplink=['P','M','N']
        logit('%-30s %-s' % ('Retain SNP probe class:','P + M + N'))
    else:
        oplink=[opt.EDITPLINK[x] for x in range(len(opt.EDITPLINK))]
        logit('%-30s %-s' % ('Retain SNP probe class:', ' + '.join(oplink)))
else:logit('%-30s %-s' % ('Genotype file format:','Affymetrix original format'))

# Checks and prints if DEBUG option is on
if opt.DEBUG:logit('%-30s %-s' % ('DEBUG mode:','ON'))


# Checks presence of one of the two plink options
if opt.PLINK and opt.PLINKacgt:
    bomb('Please choose just ONE of the two plink options (--plink or --plinkACGT). Both options cannot be chosen!')

# Prints warning messages
if not opt.BEST and opt.PQC!='0.95,0.99':
    logit("\nWARNING MESSAGE: PlateQC options selected without requiring BestPractice workflow - DISREGARDED\n")
if not opt.BEST and opt.Pfile:
    logit("\nWARNING MESSAGE: Plate file specified without requiring BestPractice workflow - DISREGARDED\n")
if not opt.PLINK and opt.EDITPLINK!='PMNx':
    if not opt.PLINKacgt:
        logit("\nWARNING MESSAGE: Editing options selected without requiring to write a PLINK file - DISREGARDED\n")
logit('-'*81+'\n')

# Checks for presence of AFFYTOOLS directory (or user defined one!)
if not os.path.isdir(opt.DIRXML):bomb("AFFYTOOLS directory not found: "+opt.DIRXML)
for infile in SPEC_axfiles:
    if not os.path.exists(opt.DIRXML+'/'+infile):
        logit("WARNING MESSAGE: File '"+infile+"' not found in: "+opt.DIRXML+"\n             ==> Program might behave unexpectedly!! <==\n")

# Checks for presence of APTools directory & important programs within that folder
if os.path.isdir(opt.DIRAPT):
    for infile in APT_progs:
        if not os.path.exists(opt.DIRAPT+'/bin/'+infile):
            bomb("Program '"+infile+"' not found in: "+opt.DIRAPT+'/bin/')
else:bomb("APTools directory not found in: "+opt.DIRAPT)

# Checks for presence of SNPolisher R package
if not os.path.isdir(opt.DIRSNP):bomb("Expected SNPolisher R package directory (SNPolisher_package) not found in: "+opt.DIRSNP+"\n            This may also due to Affymetrix changing this folder name.\n            In that case, please rename the folder as SNPolisher_package (and update the package BEFORE running this pgm!)")

# Checks for presence of SNPolisher R package
if not os.path.isdir(opt.DIRSNP):bomb("SNPolisher R package directory not found in: "+opt.DIRSNP)

# Checks for presence of -p if -e option is present
if opt.PLINK or opt.PLINKacgt:
    if opt.EDITPLINK!='PMNx':
        for i in opt.EDITPLINK:
            if i not in 'PMNOCT':bomb("Editing option not recognized: '"+i+"'. Please choose between: P M N O C T") 

# Check that numbers are numbers and are within range
check_range(opt.DQC,'Dish-QC')
check_range(opt.CR,'Call rate')
if opt.BEST:check_range(opt.PQC.strip().split(',')[0],'PlatePassRate')
if opt.BEST:check_range(opt.PQC.strip().split(',')[1],'AvgCallRate')

################################################
### Create output folder if not present
################################################
sub.call(["mkdir -p %s" % opt.DIROUT],shell=True)
sub.call(["mkdir -p %s/output" % opt.DIROUT],shell=True)
logit("[GOOD NEWS]: Internal checks OK! Now real stuff begins..")

############################################################################################################
###
###   REAL PIPELINE BEGINS HERE!
###
############################################################################################################
################################################
### Launch first program (affymetrix APT_GENO-QC)
################################################
logit('\n'+'*'*81+'\n==> FIRST AFFYMETRIX PROGRAM: This obtains Dish_QC values <==\n'+'*'*81)
logit("COMMAND LAUNCHED :\n %s/./%s\n --analysis-files-path %s" % (opt.DIRAPT,APT_progs[0],opt.DIRXML))
logit(' --xml-file %s/%s\n --cel-files %s' %(opt.DIRXML,SPEC_axfiles[0],args[0]))
logit(' --out-dir %s\n --log-file apt-geno-qc.log\n --out-file %s/qc-report.txt' % (opt.DIROUT,opt.DIROUT))

std = sub.Popen([str(opt.DIRAPT+'/bin/./'+APT_progs[0]+                \
                         ' --analysis-files-path '+opt.DIRXML+          \
                         ' --xml-file '+opt.DIRXML+'/'+SPEC_axfiles[0]+ \
                         ' --cel-files '+args[0]+                       \
                         ' --out-dir '+opt.DIROUT+                      \
                         ' --log-file apt-geno-qc.log '+                \
                         ' --out-file '+opt.DIROUT+'/qc-report.txt')],  \
                shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readlines()

if 'Done running GenoQC' in std[-1]:
    logit("[GOOD NEWS]: Affymetrix APT first qc run OK!. This "+std[-2].strip())
    if opt.DEBUG:logit('AffyAPT - 1 - OK:\n'+''.join(std))
else:
    print "\n[BAD NEWS]: Affymetrix APT first qc DID NOT run ok..."
    num = [i for i,x in enumerate(std) if x=="*\n"]
    if opt.DEBUG:logit('AffyAPT - 1 - ERROR:\n'+''.join(std))
    bomb("Error message given:\n[BAD NEWS]: "+std[int(num[-1]+1)]+'[BAD NEWS]: '+std[-1])

##############################################################################################
### Create new input CEL list file for program 2, excluding animals with low DQC
##############################################################################################
logit('\n'+'*'*81+'\n==> CREATING NEW .CEL LIST FILE excluding low DQC individuals <==\n'+'*'*81)
out =open(opt.DIROUT+'/celfile_DQClean.txt','w')
elim=open(opt.DIROUT+'/LOWQUAL_ELIMids.txt','w')
skip=True
dove={}

# This stores original .CEL file info.
for x in open(args[0]):
    if skip:
        skip=False;continue
    data=x.strip().split('/')
    idx=data[-1]
    path=data[:-1]
    dove[idx]=path

# This cleans celfile, creating the new input for Affy prog. N.2
skip=True
kept=0
for a in open(opt.DIROUT+'/qc-report.txt'):
    if 'cel_files' in a:
        out.write('cel_files\n')
        skip=False;continue
    if skip:continue
    data=a.strip().split('\t')
    celfilex=data[0]
    qq=data[17]                    ### DISH QC VALUE
    if float(qq) < float(opt.DQC):
        elim.write(a.strip().split('\t')[0]+' DISHQC:'+str(qq)+'\n')
        logit("### Excluding individual: "+celfilex+" -->Dish_QC: "+qq)
        continue
    else:
        out.write('%s/%s\n' % ('/'.join(dove[celfilex]),celfilex))
        kept+=1
out.close()
if kept==0:bomb('No individuals left for analysis. You may want to review thresholds used?')
logit("[GOOD NEWS]: Clean cel list file is ready for program 2!")

################################################
### Launch second program (affymetrix)
################################################
logit('\n'+'*'*81+'\n==> SECOND AFFYMETRIX PROGRAM: This obtains call rates on a subset of SNPs <==\n'+'*'*81)

## This differenciates the prior depending on the # of individuals kept
if kept <= 96:
    axiom_prior=SPEC_axfiles[1]
else:
    axiom_prior=SPEC_axfiles[2]

logit("[GOOD NEWS]: A total of %s individuals were kept, thus priors file is: %s\n" % (kept,axiom_prior))

summary=' --out-dir %s' % opt.DIROUT
if opt.SUMM:summary='--summaries --out-dir %s' % opt.DIROUT

logit("COMMAND LAUNCHED :\n %s/bin/./%s\n --analysis-files-path %s" % (opt.DIRAPT,APT_progs[1],opt.DIRXML))
logit(' --xml-file %s/%s\n --cel-files %s/celfile_DQClean.txt' % (opt.DIRXML,axiom_prior,opt.DIROUT))
logit(' --log-file apt-probeset-genotype1.log %s' % summary.replace(' ','\n ',1))

std = sub.Popen([str(opt.DIRAPT+'/bin/./'+APT_progs[1]+                    \
                         ' --analysis-files-path '+opt.DIRXML+              \
                         ' --xml-file '+opt.DIRXML+'/'+axiom_prior+         \
                         ' --cel-files '+opt.DIROUT+'/celfile_DQClean.txt'+ \
                         ' --log-file apt-probeset-genotype1.log '+         \
                         summary)],                                         \
                shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readlines()

if 'Done running ProbesetGenotypeEngine' in std[-1]:
    logit("[GOOD NEWS]: Affymetrix APT second qc run OK!. This "+std[-2].strip())
    if opt.DEBUG:logit('AffyAPT - 2 - OK:\n'+''.join(std))

else:
    print "\n[BAD NEWS]: Affymetrix APT second qc DID NOT run ok..."
    num = [i for i,x in enumerate(std) if x=="*\n"]
    if opt.DEBUG:logit('AffyAPT - 2 - ERROR:\n'+''.join(std))
    bomb("Error message given:\n[BAD NEWS]: "+std[int(num[-1]+1)]+'[BAD NEWS]: '+std[-1])

##############################################################################################
### Create new input CEL list file for program 3, excluding animals with low CR
##############################################################################################
logit('\n'+'*'*81+'\n==> CREATING NEW .CEL LIST FILE excluding low CR individuals <==\n'+'*'*81)
out2 =open(opt.DIROUT+'/celfile_DQClean_CRclean.txt','w')
skip=True

dove={}
for x in open(opt.DIROUT+'/celfile_DQClean.txt'):
    if skip:
        skip=False;continue
    data=x.strip().split('/')
    idx=data[-1]
    path=data[:-1]
    dove[idx]=path

skip=True
kept2=0
if opt.BEST:
    c_plates={}
    sumCR={}
for a in open(opt.DIROUT+'/AxiomGT1.report.txt'):
    if 'cel_files' in a:
        out2.write('cel_files\n')
        skip=False;continue
    if skip:continue
    celfilex,sex,CRATE,rest=a.strip().split('\t',3)
    if float(CRATE)/100.<float(opt.CR):
        elim.write(a.strip().split('\t')[0]+' CALLRATE:'+str(CRATE)+'\n')
        logit("### Excluding individual: "+celfilex+" -->CALL RATE: "+CRATE)
        continue
    else:
        if opt.BEST:
            plate=animplate[celfilex.split('/')[-1].split('.')[0]]
            if not c_plates.has_key(plate):
                c_plates[plate]=1
                sumCR[plate]=float(CRATE)
            else:
                c_plates[plate]+=1
                sumCR[plate]+=float(CRATE)
        out2.write('%s/%s\n' % ('/'.join(dove[celfilex]),celfilex))
        kept2+=1

out2.close()
elim.close()
if kept2==0:bomb('No individuals left for analysis. You may want to review thresholds used?')
logit("[GOOD NEWS]: Clean cel list file is ready for program 3 (or PlateQC if BestPractice required)!")

#######################################################
### Launch QC on Plates (if bestpractice is required)
#######################################################
if opt.BEST:
    kept2=0
    goodP={}
    out3=open(opt.DIROUT+'/celfile_DQClean_CRclean_PQClean.txt','w')
    out3.write('cel_files\n')

    logit('\n'+'*'*81+'\n==> PLATE QC CONTROL: Obtaining PlateQC values <==\n'+'*'*81)
    ppr=float(opt.PQC.strip().split(',')[0])*100
    acr=float(opt.PQC.strip().split(',')[1])*100
    ## Total #individuals by plate are stored in             : plates
    ## Total #individuals passing QCs by plate are stored in : c_plates (clean_plates)
    for en,plate in enumerate(plates):
        PlatePR=round(100.*float(c_plates[plate[0]])/float(plate[1]),2)
        AvgCR=round(sumCR[plate[0]]/c_plates[plate[0]],2)
        if PlatePR>=ppr and AvgCR>=acr:
            if not goodP.has_key(plate[0]):goodP[plate[0]]=0
        else:
            logit("[BAD NEWS]: Plate: %s DID NOT pass PlateQC (PlatePR: %s and AvgCR: %s) - Eliminating %s individuals" % \
                  (plate[0],PlatePR,AvgCR,c_plates[plate[0]]))
    skip=True
    for a in open(opt.DIROUT+'/celfile_DQClean_CRclean.txt'):
        if skip:
            skip=False;continue
        data=a.strip().split('/')
        idx=data[-1]
        path=data[:-1]
        dove[idx]=path        
        plate=animplate[idx.split('/')[-1].split('.')[0]]
        if goodP.has_key(plate):
            out3.write('%s/%s\n' % ('/'.join(dove[idx]),idx))
            kept2+=1

    out3.close()
    if kept2==0:bomb('No individuals left for analysis. You may want to review thresholds used?')
    logit("[GOOD NEWS]: Clean Plate cel list file is ready for program 3")

################################################
### Launch third program (affymetrix)
################################################
logit('\n'+'*'*81+'\n==> THIRD AFFYMETRIX PROGRAM: This obtains all files for downstream analyses <==\n'+'*'*81)

## This uses the right cel list file in case (or not) BestPractice is chosen.
infile3=opt.DIROUT+'/celfile_DQClean_CRclean.txt'
if opt.BEST:infile3=opt.DIROUT+'/celfile_DQClean_CRclean_PQClean.txt'

## This differenciates the prior depending on the # of individuals kept
if kept2 <= 96:
    axiom_prior=SPEC_axfiles[3]
else:
    axiom_prior=SPEC_axfiles[4]
logit('[GOOD NEWS]: A total of %s individuals were kept, thus priors file is: %s\n' % (kept2,axiom_prior))

summary='--cc-chp-output --write-models'
if opt.SUMM:summary='--summaries --cc-chp-output --write-models'

logit('COMMAND LAUNCHED :\n %s/bin/./%s\n --analysis-files-path %s' % (opt.DIRAPT,APT_progs[1],opt.DIRXML))
logit(' --xml-file %s/%s\n --cel-files %s' % (opt.DIRXML,axiom_prior,infile3))
logit(' --log-file apt-probeset-genotype2.log\n --out-dir %s\n %s' % (opt.DIROUT,summary.replace(' ','\n ')))

std = sub.Popen([str(opt.DIRAPT+'/bin/./'+APT_progs[1]+                              \
                         ' --analysis-files-path '+opt.DIRXML+                        \
                         ' --xml-file '+opt.DIRXML+'/'+axiom_prior+                   \
                         ' --cel-files '+infile3 +                                    \
                         ' --log-file apt-probeset-genotype2.log'+                    \
                         ' --out-dir '+opt.DIROUT+' '+                                \
                         summary)],                                                   \
                shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readlines()

if 'Done running ProbesetGenotypeEngine' in std[-1]:
    logit("[GOOD NEWS]: Affymetrix APT third qc run OK!. This "+std[-2].strip())
    if opt.DEBUG:logit('AffyAPT - 3 - OK:\n'+''.join(std))
else:
    print "\n[BAD NEWS]: Affymetrix APT third qc DID NOT run ok..."
    num = [i for i,x in enumerate(std) if x=="*\n"]
    if opt.DEBUG:logit('AffyAPT - 3 - ERROR:\n'+''.join(std))
    bomb("Error message given:\n[BAD NEWS]: "+std[int(num[-1]+1)]+'[BAD NEWS]: '+std[-1])

################################################
### Launch SNPolisher
################################################
logit('\n'+'*'*81+'\n==> FOURTH AFFYMETRIX PROGRAM: This runs SNPolisher R package <==\n'+'*'*81)

## This builds the ps2snp.txt file needed by SNPolisher.
out3=open(HERE+'/ps2snp.txt','w')
skip=True
probeset=0
if opt.PLINK or opt.PLINKacgt: allps={}
if opt.PLINKacgt:AlleleACGT={}
for line in open(Smap):
    if '#' in line[0] or len(line)<50:continue  #Avoids issues caused by Affy's different headings and formats 
    if skip:
        if line.count('"')>10:
            line=line.replace('"','')
            if len(line.strip().split('\t')) > 5:
                sep='\t'
                header=line.strip().split('\t')
            elif len(line.strip().split(',')) > 5:
                sep=','
                header=line.strip().split(',')
            elif len(line.strip().split(';')) > 5:
                sep=';'
                header=line.strip().split(',')
            else:
                sep='SPA'
                header=line.strip().split()
        try:probe=header.index('Probe Set ID')
        except ValueError:bomb("Variable 'Probe Set ID' not found in header. Header variables found:"+str(header))
        try:snp=header.index('Affy SNP ID')
        except ValueError:bomb("Variable 'Affy SNP ID' not found in header read. Header variables found:"+str(header))
        try:crom=header.index('Chromosome')
        except ValueError:bomb("Variable 'Chromosome' not found in header read. Header variables found:"+str(header))
        try:pos=header.index('Physical Position')
        except ValueError:bomb("Variable 'Physical Position' not found in header. Header variables found:"+str(header))
        try:pos_allA=header.index('Allele A')
        except ValueError:bomb("Variable 'Allele A' not found in header. Header variables found:"+str(header))
        try:pos_allB=header.index('Allele B')
        except ValueError:bomb("Variable 'Allele B' not found in header. Header variables found:"+str(header))
        out3.write('probeset_id snpid\n')
        skip=False
        continue
    line=line.replace('"','')
    ## Detecting separator
    if sep!='SPA':allfields=line.strip().split(sep)
    else: allfields=line.strip().split()
    ## 
    if opt.PLINKacgt:
        allps[allfields[probe]]=(allfields[snp],allfields[crom],allfields[pos])
        if not AlleleACGT.has_key(allfields[probe]):
            AlleleACGT[allfields[probe]] = [allfields[pos_allA],allfields[pos_allB]]
    if opt.PLINK: allps[allfields[probe]]=(allfields[snp],allfields[crom],allfields[pos])
    out3.write('%s %s\n' % (allfields[probe],allfields[snp]))
    probeset+=1
out3.close()

if probeset==0:bomb('ANNOTATION file ('+Smap+') seems to be empty!. Please check the file.\n'+\
                     '            If the file is not empty, please write to ezequielluis.nicolazzi@gmail.com')
logit("[GOOD NEWS]: Total probe sets read in "+Smap+"\n              (separator found:'"+sep+"' & alleles in position: "+\
                    str(pos_allA+1)+"-"+str(pos_allB+1)+"): "+str(probeset))

PAC = sub.Popen(["ls "+opt.DIRSNP+"/SNPolisher*.tar.gz"], shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readline()
Rsc=open(opt.DIROUT+'/SNPol.R','w')

## Writes a specific Rscript for SNPolisher
Rsc.write("if (is.element('SNPolisher',installed.packages())){\nlibrary(SNPolisher)}else{\n")
Rsc.write("install.packages('"+PAC+"',repos=NULL,type='source');library(SNPolisher)}\n")
Rsc.write("ps.metrics <- Ps_Metrics(posteriorFile=paste('"+opt.DIROUT+"','/AxiomGT1.snp-posteriors.txt',sep=''),")
Rsc.write("callFile=paste('"+opt.DIROUT+"','/AxiomGT1.calls.txt',sep=''),")
Rsc.write("output.metricsFile=paste('"+opt.DIROUT+"','/metrics.txt',sep=''))\n")
Rsc.write("Ps_Classification(metricsFile=paste('"+opt.DIROUT+"','/metrics.txt',sep=''),")
Rsc.write("ps2snpFile=paste('"+HERE+"','/ps2snp.txt',sep=''),output.dir=paste('"+opt.DIROUT+"','/output',sep=''),")
Rsc.write("SpeciesType='Diploid')\n")
Rsc.write("print('ENDOK')\n")
Rsc.close()

## This actually runs the R script
sub.call(["R CMD BATCH %s/SNPol.R %s/SNPol.Rout " % (opt.DIROUT,opt.DIROUT)],shell=True)

## Checks results
CHK = sub.Popen(["tail "+opt.DIROUT+"/SNPol.Rout | grep '[1]'| grep 'ENDOK'"], shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readline().strip()
if CHK=='[1] "ENDOK"':
    logit("[GOOD NEWS]: Program 4 (Affymetrix SNPolisher) seems to have run OK!")
    if opt.DEBUG:logit('SNPolisher - OK:\n'+''.join(CHK))
else:
    print "\n[BAD NEWS]: Program 4 (Affymetrix SNPolisher) DID NOT run ok..."
    if opt.DEBUG:logit('SNPolisher - ERROR:\n'+''.join(CHK))
    bomb("Error message given:\n[BAD NEWS]: Please check: "+opt.DIROUT+"/SNPol.Rout for more information")

###############################################################
### Launch fifth part (conversion to PLINK fmt if required)
###############################################################
edits={'P':'PolyHighResolution','M':'MonoHighResolution','N':'NoMinorHom','O':'OTV','C':'CallRateBelowThreshold', 'T':'Other'} 
if opt.PLINK or opt.PLINKacgt:
    logit('\n'+'*'*81+'\n==> Reading SNPolisher output to keep best probes <==\n'+'*'*81)
    skip=True
    n=0;ke=0
    keeprobe={};keeptype={}
    for x in oplink:keeptype[edits[x]]=0

    for line in open(opt.DIROUT+'/output/Ps.performance.txt'):
        if skip:
            skip=False;continue
        inline=line.strip().split('\t')
        probe=inline[0]
        bestprobe=inline[-1]
        probetype=inline[-2]
        n+=1
        if bestprobe=='1' and keeptype.has_key(probetype):
            keeprobe[probe]=0
            ke+=1
    logit("A total of %s probes were read from %s/output/Ps.performance.txt" % (n,opt.DIROUT))
    logit("A total of %s SNPs were kept (e.g. bestprobes and edited by type of probe)" % ke)
    logit('\n'+'*'*81+'\n==> Converting gentoypes into PLINK FORMAT <==\n'+'*'*81)
    file_ped=open(opt.DIROUT+'/Axiom_genotypes_PLINKfmt.ped','w')
    file_map=open(opt.DIROUT+'/Axiom_genotypes_PLINKfmt.map','w')
    geno_code = {'0':'A A', '1':'A B', '2':'B B', '-1':'0 0'}

    try:
        callfile=open(opt.DIROUT+'/AxiomGT1.calls.txt','r')
    except:
        bomb('AxiomGT1.calls.txt file not found in: '+opt.DIROUT+' An Affy pgm probably did not work as expected!!')

    anims=False
    okp=0;allids=[]
    # Read Axiom call file, and write map file.
    for line in open(opt.DIROUT+'/AxiomGT1.calls.txt'):
        if 'probeset_id' in line:
            allids=[x[:-4] for x in line.strip().split('\t')[1:]]
            G=[[] for x in range(len(allids))]
            anims=True;continue
        if not anims:continue
        line = line.strip().split('\t')
        if opt.PLINKacgt:
            probe_id = line[0]
            if not AlleleACGT.has_key(probe_id):
                bomb("Annotation file does not contain probe: "+probe_id+" information. Check you're using the right file!")
            probe_a,probe_b = AlleleACGT[probe_id]
            geno_code = {'2':probe_b+' '+probe_b, '1':probe_a+' '+probe_b, '0':probe_a+' '+probe_a, '-1':'0 0'}
        if not keeprobe.has_key(line[0]):continue
        odata=allps.get(line[0],False)
        if not odata:
            bomb('Probe set '+line[0]+' not found in Master Annotation file! Please check this!')
        file_map.write('%s %s 0 %s\n' % (odata[1],odata[0],odata[2]))
        okp+=1
        d=-1
        for x in line[1:]:
            d+=1
            try:
                G[d].append(geno_code[x])
            except:
                bomb('ERROR while reading probe '+probe_id+' in '+opt.DIROUT+'/AxiomGT1.calls.txt -> ALLELES '+x+' NOT RECOGNIZED!')

    # Write .ped file
    for j in range(len(allids)):
        file_ped.write('FAM '+allids[j]+' 0 0 0 0 '+' '.join(G[j])+'\n')

    logit('Genotypes were recoded as follows: 0="B/B", 1="A/B" and 2="A/A" -1="0/0"')
    logit('A total of '+str(len(allids))+' samples were written to '+opt.DIROUT+'/Axiom_genotypes_PLINKfmt.ped')
    logit('A total of '+str(okp)+' SNPs were written to '+opt.DIROUT+'/Axiom_genotypes_PLINKfmt.map')
    file_ped.close()
    file_map.close()

sub.call(["mv -f %s/apt-geno-qc.log %s/apt-probeset-genotype1.log %s/apt-probeset-genotype2.log %s" % (HERE,HERE,HERE,opt.DIROUT)],shell=True)
logit("[GOOD NEWS]: .log files were moved to output folder %s" % opt.DIROUT)
logit("\n --> Please check output file:"+opt.DIROUT+"/SNPol.Rout <--")

print;print
print "NOTE: Check file %s/LOWQUAL_ELIMids.txt\n      which contains the list of individuals discarded during the process (if any)" % opt.DIROUT
print;print "BAZINGA! I've done my work."
logit('*'*81+'\n==> PROGRAM ENDED SUCCESSFULLY: '+time.strftime("%B %d, %Y - %l:%M%p %Z")+' <==\n'+'*'*81)
