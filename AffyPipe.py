"""
Program that automatically runs Affymetrix APT and SNPolisher programs for MAC and Linux users.
Original version: Ezequiel L. Nicolazzi (Fondazione Parco Tecnologico Padano, Italy), March 2014.
Changes:
   -May 2014 (ELN): Excluded summary info of default. Direct MAP name. Gzips most output files
                    Included editing of SNP probe classes for PLINK format.
                
For bug report/comments: ezequiel.nicolazzi@tecnoparco.org
"""
import sys,os,time
from optparse import OptionParser
import subprocess as sub


################################################
### Useful defs
################################################
# This stops the pipeline when something BAD happens
def bomb(msg):
    print('\n\n[BAD NEWS]: '+msg+'\n')
    print "*"*60
    print "Program stopped because of an error. Please read .log file"
    print "*"*60
    sys.exit()

# Prints (if required) and writes the log 
def logit(msg):
    global VER
    if VER:print(msg)
    log.write(msg+'\n')

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
    APTools='/apt-1.15.2-x86_64-apple-lion/'
    logit('Recognised a MACOSx system')
else: 
    APTools='/apt-1.15.2-x86_64-intel-linux/'
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
parser.add_option("-m","--map", dest="MAP", default=HERE+'/AxiomReference/Axiom_Buffalo_Annotation.csv',
                  help="write path to Axiom annotation (SNP map) file", metavar="<FILE>")
parser.add_option("-o","--outdir", dest="DIROUT", default=HERE+'/OUTPUT/',
                  help="write path to output directory (if not found will create one)", metavar="<PATH>")
parser.add_option("-d","--dqc", dest="DQC", default='0.82',
                  help="dish QC threshold. Ind. with DQC<threshold will be excluded", metavar="VALUE 0>=1")
parser.add_option("-c","--crate", dest="CR", default='0.97',
                  help="call rate threshold. Ind. with CR<threshold will be excluded", metavar="VALUE 0>=1")
parser.add_option("-y","--summary", action="store_true", dest="SUMM", default=False,
                  help="outputs the summaries files (large mem!) of genotyping proc")
parser.add_option("-p","--plink",action="store_true", dest="PLINK", default=False,
                  help="outputs (all) BestProbeset SNPs in PLINK format")
parser.add_option("-e","--editplink", dest='EDITPLINK',default='PMNx',
                  help="Edit options (only if -p is specified). See README file for more info", metavar="PMNOCT")
parser.add_option("-q","--quiet",action="store_false", dest="VER", default=True,
                  help="Avoid showing runtime messages to stdout")
(opt, args) = parser.parse_args()
VER=opt.VER

########################################################
# SPECIES (Buffalo for now) specific software and files
########################################################
SPEC_axfiles=['Axiom_Buffalo.r2.apt-geno-qc.AxiomQC1.xml',\
              'Axiom_Buffalo_LessThan96_Step1.r2.apt-probeset-genotype.AxiomGT1.xml','Axiom_Buffalo_96orMore_Step1.r2.apt-probeset-genotype.AxiomGT1.xml',\
              'Axiom_Buffalo_LessThan96_Step2.r2.apt-probeset-genotype.AxiomGT1.xml','Axiom_Buffalo_96orMore_Step2.r2.apt-probeset-genotype.AxiomGT1.xml']
SPEC_progs=['apt-geno-qc','apt-probeset-genotype']


#######################################################
### Print and check options before running the program
#######################################################
logit('\n'+'*'*81+'\n==> PROGRAM STARTS: '+time.strftime("%B %d, %Y - %l:%M%p %Z")+'\n'+'*'*81)

# First of all, check if CEL list file is provided and exists
if len(args)!=1: bomb("Providing a .cel list file  is compulsary! Please run: python "+sys.argv[0]+" -h, for help.")
if not os.path.exists(args[0]): bomb("CEL list file not found!!! I looked for file: "+args[0])
allfile=open(args[0],'r').readlines()
header=allfile[0].strip()
if header!='cel_files':bomb("The first row of CEL list file has to be 'cel_files', but is: "+header)

logit('-'*91+'\n==> PARAMETERS OF THE PROGRAM \n'+'-'*81)
logit('%-30s %-s' % ('CEL list file used:',args[0]))
logit('%-30s %-d' % ('Individuals read in CEL file:',len(allfile)-1))
logit('%-30s %-s' % ('AFFYTOOLS directory:',opt.DIRXML))
logit('%-30s %-s' % ('APT programs directory:',opt.DIRAPT))
logit('%-30s %-s' % ('SNPolisher directory:',opt.DIRSNP))
logit('%-30s %-s' % ('Axiom annotation file:',opt.MAP))
logit('%-30s %-s' % ('Output directory:',opt.DIROUT))
logit('%-30s %-s' % ('Dish-QC threshold used:',opt.DQC))
logit('%-30s %-s' % ('Call rate threshold used:',opt.CR))

# Checks if summary file is required
if opt.SUMM:logit('%-30s %-s' % ('Summary genotyping files:','REQUIRED'))
else:logit('%-30s %-s' % ('Summary genotyping files:','NOT REQUIRED'))

# Checks PLINK and edit options
if opt.PLINK:
    logit('%-30s %-s' % ('Genotype file format:','PLINK'))
    if opt.EDITPLINK=='PMNx':logit('%-30s %-s' % ('Retain SNP probe class:','P + M + N'))
    else:
        oplink=[opt.EDITPLINK[x] for x in range(len(opt.EDITPLINK))]
        logit('%-30s %-s' % ('Retain SNP probe class:', ' + '.join(oplink)))
else:logit('%-30s %-s' % ('Genotype file format:','Affymetrix original format'))
if not opt.PLINK and opt.EDITPLINK!='PMNx':
    logit("\nWARNING MESSAGE: Editing options selected without requiring to write a PLINK file - DISREGARDED")
logit('-'*91+'\n')

# Checks for presence of AFFYTOOLS directory (or user defined one!)
if not os.path.isdir(opt.DIRXML):bomb("AFFYTOOLS directory not found: "+opt.DIRXML)
for infile in SPEC_axfiles:
    if not os.path.exists(opt.DIRXML+'/'+infile):bomb("File '"+infile+"' not found in: ",opt.DIRXML)

# Checks for presence of APTools directory & important programs within that folder
if os.path.isdir(opt.DIRAPT):
    for infile in SPEC_progs:
        if not os.path.exists(opt.DIRAPT+'/bin/'+infile):
            bomb("Program '"+infile+"' not found in: ",opt.DIRAPT+'/bin/')
else:bomb("APTools directory not found in: "+opt.DIRAPT)

# Checks for presence of SNPolisher R package
if not os.path.isdir(opt.DIRSNP):bomb("SNPolisher R package directory not found in: "+opt.DIRSNP)

# Checks for presence of Axiom Annotation (or SNPmap) file
if not os.path.exists(opt.MAP):bomb("Annotation (MAP) file:"+opt.MAP+" not found!")

# Checks for presence of -p if -e option is present
if opt.PLINK and opt.EDITPLINK!='PMNx':
    for i in opt.EDITPLINK:
        if i not in 'PMNOCT':bomb("Editing option not recognized: '"+i+"'. Please choose between: P M N O C T") 

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
### Launch first program (affymetrix)
################################################
logit('\n'+'*'*81+'\n==> FIRST AFFYMETRIX PROGRAM: This obtains Dish_QC values <==\n'+'*'*81)
logit("COMMAND LAUNCHED :\n"+opt.DIRAPT+'/./'+SPEC_progs[0]+'\n --analysis-files-path '+opt.DIRXML)
logit(' --xml-file '+opt.DIRXML+'/'+SPEC_axfiles[0]+'\n --cel-files '+args[0])
logit(' --out-file '+opt.DIROUT+'/qc-report.txt')

std = sub.Popen([str(opt.DIRAPT+'/bin/./'+SPEC_progs[0]+                \
                         ' --analysis-files-path '+opt.DIRXML+          \
                         ' --xml-file '+opt.DIRXML+'/'+SPEC_axfiles[0]+ \
                         ' --cel-files '+args[0]+                       \
                         ' --out-file '+opt.DIROUT+'/qc-report.txt')],  \
                shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readlines()

if 'Done running GenoQC' in std[-1]:
    logit("[GOOD NEWS]: Program 1 (Affymetrix APT first qc) run OK!. This "+std[-2].strip())
else:
    print "\n[BAD NEWS]: Program 1 (Affymetrix APT first qc) DID NOT run ok..."
    num = [i for i,x in enumerate(std) if x=="*\n"]
    bomb("Error message given:\n[BAD NEWS]: "+std[int(num[-1]+1)]+'[BAD NEWS]: '+std[-1])

sub.call(["gzip -c %s/apt-geno-qc.log > %s/apt-geno-qc.log.gz" % (HERE,opt.DIROUT)],shell=True)

logit("[GOOD NEWS]: apt-geno-qc.log file was compressed and sent to output folder")

##############################################################################################
### Create new input CEL list file for program 2, excluding animals with low DQC
##############################################################################################
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
logit("[GOOD NEWS]: Clean cel list file is ready for program 2!")

################################################
### Launch second program (affymetrix)
################################################
logit('\n'+'*'*81+'\n==> SECOND AFFYMETRIX PROGRAM: This obtains call rates on a subset of SNPs <==\n'+'*'*81)

## This differenciates the prior depending on the # of individuals kept
if kept <= 96:axiom_prior=SPEC_axfiles[1]
else:axiom_prior=SPEC_axfiles[2]
logit("[GOOD NEWS]: A total of %s individuals were kept, thus priors file is: %s" % (kept,axiom_prior))
logit("COMMAND LAUNCHED :\n"+opt.DIRAPT+'/bin/./'+SPEC_progs[1]+'\n --analysis-files-path '+opt.DIRXML)
logit(' --xml-file '+opt.DIRXML+'/'+axiom_prior+'\n --cel-files '+opt.DIROUT+'/celfile_DQClean.txt')
if opt.SUMM:
    logit(' --summaries\n --out-dir '+opt.DIROUT)
    summary=' --summaries '
else:
    logit(' --out-dir '+opt.DIROUT)
    summary=''

std = sub.Popen([str(opt.DIRAPT+'/bin/./'+SPEC_progs[1]+                    \
                         ' --analysis-files-path '+opt.DIRXML+              \
                         ' --xml-file '+opt.DIRXML+'/'+axiom_prior+         \
                         ' --cel-files '+opt.DIROUT+'/celfile_DQClean.txt'+ \
                         summary +                                          \
                         ' --out-dir '+opt.DIROUT)],                        \
                shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readlines()

if 'Done running ProbesetGenotypeEngine' in std[-1]:
    logit("[GOOD NEWS]: Program 2 (Affymetrix APT second qc) run OK!. This "+std[-2].strip())
else:
    print "\n[BAD NEWS]: Program 2 (Affymetrix APT second qc) DID NOT run ok..."
    num = [i for i,x in enumerate(std) if x=="*\n"]
    bomb("Error message given:\n[BAD NEWS]: "+std[int(num[-1]+1)]+'[BAD NEWS]: '+std[-1])

##############################################################################################
### Create new input CEL list file for program 3, excluding animals with low CR
##############################################################################################

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
for a in open(opt.DIROUT+'/AxiomGT1.report.txt'):
    if 'cel_files' in a:
        out2.write('cel_files\n')
        skip=False;continue
    if skip:continue
    celfilex,sex,CRATE,rest=a.strip().split('\t',3)
    if float(CRATE)<float(opt.CR):
        elim.write(a.strip().split('\t')[0]+' CALLRATE:'+str(CRATE)+'\n')
        logit("### Excluding individual: "+celfilex+" -->CALL RATE: "+CRATE)
        continue
    else:
        out2.write('%s/%s\n' % ('/'.join(dove[celfilex]),celfilex))
        kept2+=1
out2.close()
elim.close()
logit("[GOOD NEWS]: Clean cel list file is ready for program 3!")

################################################
### Launch third program (affymetrix)
################################################
logit('\n'+'*'*81+'\n==> THIRD AFFYMETRIX PROGRAM: This obtains all files for downstream analyses <==\n'+'*'*81)

## This differenciates the prior depending on the # of individuals kept
if kept2 <= 96:axiom_prior=SPEC_axfiles[3]
else:axiom_prior=SPEC_axfiles[4]
logit('[GOOD NEWS]: A total of %s individuals were kept, thus priors file is: %s' % (kept2,axiom_prior))
logit('COMMAND LAUNCHED :\n'+opt.DIRAPT+'/bin/./'+SPEC_progs[1]+'\n --analysis-files-path '+opt.DIRXML)
logit(' --xml-file '+opt.DIRXML+'/'+axiom_prior+'\n --cel-files '+opt.DIROUT+'/celfile_DQClean.txt')
logit(' --out-dir '+opt.DIROUT+'\n --cc-chp-output')
if opt.SUMM:
    logit(' --summaries\n --write-models')
    summary=' --summaries '
else:
    logit(' --write-models')
    summary=''

std = sub.Popen([str(opt.DIRAPT+'/bin/./'+SPEC_progs[1]+                              \
                         ' --analysis-files-path '+opt.DIRXML+                        \
                         ' --xml-file '+opt.DIRXML+'/'+axiom_prior+                   \
                         ' --cel-files '+opt.DIROUT+'/celfile_DQClean_CRclean.txt'+   \
                         ' --out-dir '+opt.DIROUT+' '+summary+' --cc-chp-output --write-models')],\
                shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readlines()

if 'Done running ProbesetGenotypeEngine' in std[-1]:
    logit("[GOOD NEWS]: Program 3 (Affymetrix APT third qc) run OK!. This "+std[-2].strip())
else:
    print "\n[BAD NEWS]: Program 3 (Affymetrix APT third qc) DID NOT run ok..."
    num = [i for i,x in enumerate(std) if x=="*\n"]
    bomb("Error message given:\n[BAD NEWS]: "+std[int(num[-1]+1)]+'[BAD NEWS]: '+std[-1])

################################################
### Launch fourth program (affymetrix - SNPolisher)
################################################
logit('\n'+'*'*81+'\n==> FOURTH AFFYMETRIX PROGRAM: This runs SNPolisher R package <==\n'+'*'*81)

## This builds the ps2snp.txt file needed by SNPolisher.
out3=open(HERE+'/ps2snp.txt','w')
skip=True
probeset=0
if opt.PLINK:allps={}
for line in open(opt.MAP):
    if '"Affy SNP ID' in line:
        out3.write('probeset_id snpid\n')
        skip=False;continue
    if skip:continue
    line=line.replace('"','')
    probe,snp,nn,crom,pos,rest=line.strip().split(',',5)
    if opt.PLINK:allps[probe]=(snp,crom,pos)
    out3.write('%s %s\n' % (probe,snp))
    probeset+=1
out3.close()
logit("[GOOD NEWS]: Total probe sets read: "+str(probeset))

PAC = sub.Popen(["ls "+opt.DIRSNP+"/SNPolisher*.tar.gz"], shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readline()
Rsc=open(opt.DIROUT+'/SNPol.R','w')

## Writes a specific Rscript for SNPolisher
Rsc.write("if (is.element('SNPolisher',installed.packages())){\nlibrary(SNPolisher)}else{\n")
Rsc.write("install.packages('"+PAC+"',repos=NULL,type='source');library(SNPolisher)}\n")
#Rsc.write("source('"+opt.DIRXML+"/Ps_Classification.R')\n")
Rsc.write("ps.metrics <- Ps_Metrics(posteriorFile=paste('"+opt.DIROUT+"','/AxiomGT1.snp-posteriors.txt',sep=''),")
Rsc.write("callFile=paste('"+opt.DIROUT+"','/AxiomGT1.calls.txt',sep=''),")
Rsc.write("output.metricsFile=paste('"+opt.DIROUT+"','/metrics.txt',sep=''))\n")
Rsc.write("Ps_Classification(metrics.file=paste('"+opt.DIROUT+"','/metrics.txt',sep=''),")
Rsc.write("ps2snp.file=paste('"+HERE+"','/ps2snp.txt',sep=''),output.dir=paste('"+opt.DIROUT+"','/output',sep=''),")
Rsc.write("SpeciesType='Diploid')\n")
Rsc.write("print('ENDOK')\n")
Rsc.close()

## This actually runs the R script
sub.call(["R CMD BATCH %s/SNPol.R %s/SNPol.Rout " % (opt.DIROUT,opt.DIROUT)],shell=True)

## Checks results
CHK = sub.Popen(["tail "+opt.DIROUT+"/SNPol.Rout | grep '[1]'| grep 'ENDOK'"], shell=True,stdout=sub.PIPE, stderr=sub.STDOUT).stdout.readline().strip()
if CHK=='[1] "ENDOK"':
    logit("[GOOD NEWS]: Program 4 (Affymetrix SNPolisher) seems to have run OK!")
    logit("Please check output file:"+opt.DIROUT+"/SNPol.Rout")
else:
    print "\n[BAD NEWS]: Program 4 (Affymetrix SNPolisher) DID NOT run ok..."
    bomb("Error message given:\n[BAD NEWS]: Please check: "+opt.DIROUT+"/SNPol.Rout for more information")

###############################################################
### Launch fifth part (conversion to PLINK fmt if required)
###############################################################
edits={'P':'PolyHighResolution','M':'MonoHighResolution','N':'NoMinorHom',\
       'O':'OTV','C':'CallRateBelowThreshold', 'T':'Other'} 
if opt.PLINK:
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
    geno_code = {'0':'B B', '1':'A B', '2':'A A', '-1':'0 0'}

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
        if not keeprobe.has_key(line[0]):continue
        odata=allps.get(line[0],False)
        if not odata:
            bomb('Probe set '+line[0]+' not found in Master Annotation file! Please check this!')
        file_map.write('%s %s 0 %s\n' % (odata[1],odata[0],odata[2]))
        okp+=1
        d=-1
        for x in line[1:]:
            d+=1
            G[d].append(geno_code[x])

    # Write .ped file
    for j in range(len(allids)):
        file_ped.write('FAM '+allids[j]+' 0 0 0 0 '+' '.join(G[j])+'\n')

    logit('Genotypes were recoded as follows: 0="B/B", 1="A/B" and 2="A/A" -1="0/0"')
    logit('A total of '+str(len(allids))+' samples were written to '+opt.DIROUT+'/Axiom_genotypes_PLINKfmt.ped')
    logit('A total of '+str(okp)+' SNPs were written to '+opt.DIROUT+'/Axiom_genotypes_PLINKfmt.map')
    file_ped.close()
    file_map.close()

print;print
print "NOTE: Check file %s/LOWQUAL_ELIMids.txt\n      which contains the list of individuals discarded during the process (if any)" % opt.DIROUT
print;print "BAZINGA! I'm done."
logit('*'*81+'\n==> PROGRAM ENDED SUCCESSFULLY: '+time.strftime("%B %d, %Y - %l:%M%p %Z")+' <==\n'+'*'*81)
