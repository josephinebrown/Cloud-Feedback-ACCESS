#!/bm/gshare/cdat52/bin/python

import os
import subprocess
import cdms2
import datetime
import cdtime
import cdutil
from cdms2 import MV2
import numpy as np
import string
import re

# Set to write classic NetCDF files
cdms2.setNetcdfShuffleFlag(0)
cdms2.setNetcdfDeflateFlag(0)
cdms2.setNetcdfDeflateLevelFlag(0)

# Define data directory and file names
data_dir='/g/data/eg3/jxb548/cloud'
work_dir='/short/eg3/jxb548'
f_kernel='cloud_kernels2_int.nc'
fdata1='histogram_xalll.nc'
fdata2='histogram_uacdg.nc'

fkernel=cdms2.open(os.path.join(data_dir,f_kernel))
LWkernel = fkernel['LWkernel']
SWkernel = np.array(fkernel['SWkernel'])
print np.max(SWkernel)
print np.min(SWkernel)

month = fkernel['mo']
tau = fkernel['tau_midpt']
lev = fkernel['p_midpt']
lat = fkernel['lat']
tau_bnds = fkernel['tau_bnds']
lev_bnds = fkernel['p_bnds']

albcs = np.array(fkernel['albcs'])

fd1=cdms2.open(os.path.join(data_dir,fdata1))
fd2=cdms2.open(os.path.join(data_dir,fdata2))

hist1 = fd1['histogram']
hist1 = hist1[:,::-1,:,:,:]
hist2 = fd2['histogram']
hist2 = hist2[:,::-1,:,:,:]

lon = fd1['lon']

change = hist2-hist1
[a,b,c,d,e] = change.shape
dpctau = MV2.masked_array(1e20*np.ones((12,b,c,d,e),'float64'))
for mm in xrange(12):
  mm_val = change[mm::12,:,:,:,:]
  dpctau[mm,:,:,:,:]=MV2.average(mm_val,0)

tmp = dpctau.swapaxes(1,2)
dpctau = tmp

f_albedo='albedo_clim_xalll_uacdg.nc'
falb=cdms2.open(os.path.join(data_dir,f_albedo))
albedo = np.array(falb['rsuscs'])

f_dtas='dtas_clim_glob_xalll_uacdg.nc'
fdtas=cdms2.open(os.path.join(data_dir,f_dtas))
dtas=fdtas['tas']

LWkernel = np.ma.masked_invalid(LWkernel)
print np.min(LWkernel)
print np.max(LWkernel)

SWkernel_map = MV2.masked_array(1e20*np.ones((12,b,c,d,e),'float64'))
for mm in xrange(12):
  for i in xrange(d):
    this=np.squeeze(albedo[mm,i,:])
    tmp=np.squeeze(SWkernel[mm,:,:,i,:])
    for j in xrange(c):
      for k in xrange(b):
	SWkernel_map[mm,k,j,i,:]=np.interp(this,albcs,tmp[k,j,:])

print np.max(SWkernel_map)
print np.min(SWkernel_map)
SWkernel_map[SWkernel_map==np.nan]=0

SW_cld_fdbk = dpctau*SWkernel_map
LW_cld_fdbk = MV2.masked_array(np.nan*np.ones((12,b,c,d,e),'float64'))
LWkernel_map = MV2.masked_array(1e20*np.ones((12,b,c,d,e),'float64'))
for mm in xrange(12):
  for i in xrange(d):
    for j in xrange(c):
      for k in xrange(b):
        LW_cld_fdbk[mm,k,j,i,:] = dpctau[mm,k,j,i,:]*LWkernel[mm,k,j,i,0]
	LWkernel_map[mm,k,j,i,:] = LWkernel[mm,k,j,i,0]

# normalise by global T change (SST only, not CO2)
#dtas = cdutil.averager(dtas, axis='xy', weight='generate')
#dtas = np.mean(dtas) 
#SW_cld_fdbk /= dtas
#LW_cld_fdbk /= dtas

SW_cld_fdbk[SWkernel_map==0]=0

print np.min(SW_cld_fdbk)
print np.max(SW_cld_fdbk)
print np.min(LW_cld_fdbk)
print np.max(LW_cld_fdbk)
print dtas.shape

# Decorate the time axis
time=cdms2.createAxis(month)
time.designateTime()
time.id='time'
time.units='months since January'
time.axis='T'

# Decorate the tau axis
tau=cdms2.createAxis(tau)
tau.id='tau'
tau.long_name='Optical Depth Bin Midpoint'
tau.units='unitless'

# Decorate the tau_bnds axis
tau_bnds=cdms2.createAxis(tau_bnds)
tau_bnds.id='tau_bnds'
tau_bnds.long_name='Optical Depth Bin Edge'
tau_bnds.units='unitless'
#cdms2.createVariable(tau_bnds,type(tau_bnds),tau_bnds)

# Decorate the lev axis
lev=cdms2.createAxis(lev)
lev.id='lev'
lev.long_name='Cloud Top Pressure Bin Midpoint'
lev.units='hPa'

# Decorate the lev_bnds axis
lev_bnds=cdms2.createAxis(lev_bnds)
lev_bnds.id='lev_bnds'
lev_bnds.long_name='Cloud Top Pressure Bin Edge'
lev_bnds.units='hPa'
#cdms2.createVariable(lev_bnds,type(lev_bnds),lev_bnds)

# Decorate the latitude axis
lat=cdms2.createAxis(lat)
lat.designateLatitude()
lat.id='lat'
lat.units='degrees_north'
lat.standard_name = 'latitude'
lat.long_name = 'latitude'
lat.axis = 'Y'

# Decorate the longitude axis
lon=cdms2.createAxis(lon)
lon.designateLongitude()
lon.id='lon'
lon.units='degrees_east'
lon.standard_name = 'longitude'
lon.long_name = 'longitude'
lon.axis = 'X'

# Decorate the mapped kernels
SWkernel_map.id='SWkernel_map'
SWkernel_map.standard_name='SW Kernel mapped to all longitudes'
SWkernel_map.long_name='SW Kernel mapped to all longitudes'
SWkernel_map.setAxis(0,time)
SWkernel_map.setAxis(1,tau)
SWkernel_map.setAxis(2,lev)
SWkernel_map.setAxis(3,lat)
SWkernel_map.setAxis(4,lon)

LWkernel_map.id='LWkernel_map'
LWkernel_map.standard_name='LW Kernel mapped to all longitudes'
LWkernel_map.long_name='LW Kernel mapped to all longitudes'
LWkernel_map.setAxis(0,time)
LWkernel_map.setAxis(1,tau)
LWkernel_map.setAxis(2,lev)
LWkernel_map.setAxis(3,lat)
LWkernel_map.setAxis(4,lon)

# Decorate the variables
SW_cld_fdbk.id='SW_cld_fdbk'
SW_cld_fdbk.units='W/m2'
SW_cld_fdbk.standard_name='SW Cloud Feedback'
SW_cld_fdbk.long_name='SW Cloud Feedback'
SW_cld_fdbk.setAxis(0,time)
SW_cld_fdbk.setAxis(1,tau)
SW_cld_fdbk.setAxis(2,lev)
SW_cld_fdbk.setAxis(3,lat)
SW_cld_fdbk.setAxis(4,lon)

LW_cld_fdbk.id='LW_cld_fdbk'
LW_cld_fdbk.units='W/m2'
LW_cld_fdbk.standard_name='LW Cloud Feedback'
LW_cld_fdbk.long_name='LW Cloud Feedback'
LW_cld_fdbk.setAxis(0,time)
LW_cld_fdbk.setAxis(1,tau)
LW_cld_fdbk.setAxis(2,lev)
LW_cld_fdbk.setAxis(3,lat)
LW_cld_fdbk.setAxis(4,lon)

# Write the data
oFname=os.path.join(data_dir,'kernel_map.nc')
out=cdms2.open(oFname,'w')
out.copyAxis(tau_bnds)
out.copyAxis(lev_bnds)
out.write(LWkernel_map)
out.write(SWkernel_map)
out.close()

oFname=os.path.join(data_dir,'cloud_feedback_xalll_uacdg.nc')
print oFname
out=cdms2.open(oFname,'w')
out.copyAxis(tau_bnds)
out.copyAxis(lev_bnds)
out.write(LW_cld_fdbk)
out.write(SW_cld_fdbk)
out.close()
quit()

