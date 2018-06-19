#!/bin/bash
#
# Program:
#   lh-um2nc.sh
#
# Author:
#   Lawson Hanson, 20141007.
#
# Purpose:
#   Modified version of Harvey Ye's "um2nc.sh" to convert output
#   from Harvey's ACCESS model runs to output in my directories.
#   ==== ========                   ==           ==
#
# Reference:
# ---------
#   Author: Harvey Ye (H.Ye@bom.gov.au)
#     Date: 24/03/2014
#
# Convert data files in a directory to NetCDF format and move to DM drive.
# 
# Usage:
#   $ lh-um2nc.sh -j jobname
#
# Updates | By | Description
# --------+----+------------
# 20141007| LH | Initial version (modified copy of H.Ye's "um2nc.sh")
#
DIR="/short/eg3/$USER"
YeDIR="/short/eg3/jxb548"
SCRIPT_DIR="/home/548/hxy548/um2netcdf"

# load necessary modules:
#
module use ~access/modules
module load pythonlib/ScientificPython/2.8
module load pythonlib/cdat-lite/6.0rc2-fixed

# defaults
force=0
jobname="uacdg"

fnUsage ( )
{
    echo
    echo "Usage: ${Prog} [-h] [-f] [-j jobname]"
    echo "Where: -h         = Display this help/usage message and exit"
    echo "       -f         = Specify to 'force' ZZZ"
    echo "       -j jobname = Specify the experiment/job name"
    echo "                    (default jobname is: '${jobname}')"
    echo
}

# Parse the command line options:
#
set -- `getopt "fhj:" "$@"`

for key in "$@"
do
    case $key in
        --)
            shift
            break
            ;;
        -f)
            force=1
            shift
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

yeDir="${YeDIR}/${jobname}"
dir="${DIR}/${jobname}"
odir="${dir}/conv"

if [ ! -d $odir ]
then
  echo "$odir does not exist. Creating"
  /bin/mkdir -p $odir
fi

finito="${odir}/finito.txt"

if [ "${force}" -gt 0 ]
then
    # Initialise a blank 'finito.txt' file:
    #
    > $finito
fi

files=`find $yeDir -maxdepth 1 -cmin +60 -type f -name "${jobname}?.pa*" | xargs ls -1tr`

for f in $files
do
    if [ -s $finito ]
    then
        finished=`grep $f $finito`
        if [ -n "$finished" ]
        then
            echo "$f finished"
            continue
        fi
    fi
    #  ${SCRIPT_DIR}/um2nc.py -i $f -o tmp.nc
    ${SCRIPT_DIR}/um2netcdf.py -i $f -o tmp.nc
    date1=`cdo -s showdate tmp.nc | sed -e 's/^[ \t]*//' \
        | tr " " "\n" | head -1 | sed 's/-//g'`
    date2=`cdo -s showdate tmp.nc | sed -e 's/^[ \t]*//' \
        | tr " " "\n" | tail -1 | sed 's/-//g'`
    type=`basename $f|cut -d. -f2|cut -c-2`
    fout="${odir}/${jobname}_${type}_${date1}-${date2}.nc"
    echo "fout=$fout"
    /bin/mv tmp.nc $fout
    echo $f >> $finito
done

exit 0

