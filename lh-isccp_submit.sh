#!/bin/sh
#PBS -P eg3
#PBS -N isccp_process 
#PBS -S /bin/sh
#PBS -q normal
#PBS -l walltime=8:00:00
#PBS -l mem=15GB
#PBS -l jobfs=15GB
#

#
# Program:
#   lh-isccp_submit.sh
#
# Purpose:
#   Use "qd8x15.sh" to submit this as a batch job
#   to run Python script "isccp.py" with required
#   resources of 15 GB memory and 8 hours walltime.
#
# Output:
#   "/short/eg3/${USER}/${jobname}/histogram_{jobname}.nc"
#   gets moved to the: /g/data/eg3/${USER}/cloud" directory.
#
# Usage:
#   $ qs8x15.sh -- ${HOME}/bin/lh-isccp_submit.sh [-j jobname]
#
Prog=`basename $0 .sh`

# The 'NC_MISSING_VALUE' environment variable is used by
# the 'cdi' library that is used by 'cdo', and causes the
# "missing_value" data attribute to be set in addition to
# the newer "_FillValue" attribute ... some old software
# still needs the (now deprecated) "missing_value" item:
#
NC_MISSING_VALUE=1
export NC_MISSING_VALUE

# Load the local module configuration file:
#
# Note:
#   Different computer systems keep local modules in
#   different locations, and perhaps have different
#   versions of the environment "module" system.
#   The configuration file needs to be kept up-to-date
#   on each system, but that should be easier than
#   trying to update lots of scripts that need this.
#
cfgFile="${HOME}/lib/local-module-info.cfg"

if [ ! -f "${cfgFile}" ]
then
    echo
    echo "${Prog}: Error: Configuration file not found:"
    echo "    ${cfgFile}"
    echo
    exit 1
else
    # Source the local module configuration file:
    #
    . $cfgFile
fi

# Load the required modules:
#
module use /g/data/r87/public/modulefiles
module remove python
module load python/2.7.5
# module load cct
# module load pipeline
module load python-cdat-lite
# module load python-setuptools
module load netcdf
# module load cdo
# module load ncl
# module load nco
# module load java

# load necessary modules:
#
module use ~access/modules
# module load pythonlib/ScientificPython/2.8
# module load pythonlib/cdat-lite/6.0rc2-fixed

### source $HOME/.bashrc

jobname="uacdg"

fnUsage ( )
{
    echo
    echo "Usage: ${Prog} [-h] [-j jobname]"
    echo "Where: -h         = Display this help/usage message and exit"
    echo "       -j jobname = Specify the experiment/job name"
    echo "                    (default jobname is: '${jobname}')"
    echo
}

# Parse the command line options:
#
set -- `getopt "hj:" "$@"`

for key in "$@"
do
    case $key in
        --)
            shift
            break
            ;;
        -h)
            fnUsage
            exit 0
            ;;
        -j)
            jobname=$2
            shift 2
            ;;
    esac
done

# Copy 'hxy' ACCESS output data files to 'user' area:
#
hxyDir=/short/eg3/jxb548/$jobname
usrDir=/short/eg3/${USER}/$jobname

if [ ! -d "${hxyDir}" ]
then
    echo "lh-isccp_submit.sh: Error: Input directory not found:"
    echo "    ${hxyDir}"
    exit 1
fi

if [ ! -d "${usrDir}" ]
then
    /bin/mkdir -p $usrDir
fi

/usr/bin/rsync -ptg ${hxyDir}/${jobname}a.pd[ij][0-9]??? $usrDir

python $HOME/bin/feedback/isccp.py -j $jobname

clouDir="/g/data/eg3/${USER}/cloud"

if [ ! -d "${clouDir}" ]
then
    /bin/mkdir -p $clouDir
fi

oFile="${usrDir}/histogram_${jobname}.nc"

if [ ! -f "${oFile}" ]
then
    echo
    echo "${Prog}: Error: Output file NOT found:"
    echo "    ${oFile}"
    echo
    exit 1
else
    # The "mv" option '-n' ---> 'noclobber':
    #
    /bin/mv -n $oFile $clouDir
fi

exit 0

