#!/bin/sh
#PBS -N tc_ACCESS1-3 
#PBS -S /bin/sh
#PBS -q normal
#PBS -l walltime=3:00:00
#PBS -l mem=15GB
#PBS -l jobfs=10GB
#
# Program:
#   lh-cal_cloud_var.sh
#
# Reference:
#   #------------------------------------------------------------------------
#   # Written By: Harvey Ye
#   # Purpose: Calculate cloud variables from converted UM output data. 
#   # July 9, 2014
#   #------------------------------------------------------------------------
#
# set -x
### . ~/.bashrc
### module remove cdo
### module load cdo

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

# define paths and job names
#
out_dir="/g/data/eg3/${USER}/cloud"
in_dir="/short/eg3/$USER"
job="uacdg"

fnUsage ( )
{
    echo
    echo "Usage: ${Prog} [-h] [-j jobname]"
    echo "Where: -h         = Display this help/usage message and exit"
    echo "       -j jobname = Specify the experiment/job name"
    echo "                    (default jobname is: '${job}')"
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
            job=$2
            shift 2
            ;;
    esac
done

# Ensure the output directory exists:
#
if [ ! -d "${out_dir}" ]
then
    /bin/mkdir -p $out_dir
fi

data_dir="${in_dir}/${job}/conv"
fname="${job}.nc"

# Combine all data files into one:
#
if [ ! -f "${data_dir}/${fname}" ]
then
    cdo cat \
        ${data_dir}/${job}_pa_*.nc \
        ${data_dir}/$fname
fi

# Calculate albedo
#
vList="rsuscs rsdscs tas"

for var in $vList
do
    cdo -s selvar,$var \
        ${data_dir}/$fname \
        ${out_dir}/${var}_${job}.nc
    cdo -s ymonmean \
        ${out_dir}/${var}_${job}.nc \
        ${out_dir}/${var}_clim_${job}.nc
done

cdo -s div \
    ${out_dir}/rsuscs_clim_${job}.nc \
    ${out_dir}/rsdscs_clim_${job}.nc \
    ${out_dir}/albedo_clim_${job}.nc

exit 0

