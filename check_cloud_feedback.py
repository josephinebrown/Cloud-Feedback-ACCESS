#!/bm/gshare/cdat52/bin/python

import os
import sys
import subprocess
import cdms2
import datetime
import cdtime
import cdutil
from cdms2 import MV2
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import cm
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
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
fdata1='histogram_xallf.nc'
fdata2='histogram_xalua.nc'
fobs='clisccp_198307-200806_fixed.nc'

fkernel=cdms2.open(os.path.join(data_dir,f_kernel))
LWkernel = fkernel['LWkernel']
SWkernel = np.array(fkernel['SWkernel'])
[a,b,c,d,e] = SWkernel.shape

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
e = len(lon)
print a,b,c,d,e
change = hist2-hist1

dpctau = MV2.masked_array(1e20*np.ones((12,b,c,d,e),'float64'))
for mm in xrange(12):
  mm_val = change[mm::12,:,:,:,:]
  dpctau[mm,:,:,:,:]=MV2.average(mm_val,0)
tmp = dpctau.swapaxes(1,2)
dpctau = tmp

f_albedo='albedo_clim_xallf_xalua.nc'
falb=cdms2.open(os.path.join(data_dir,f_albedo))
albedo = np.array(falb['rsuscs'])

f_dtas='dtas_clim_glob_xallf_xalua.nc'
fdtas=cdms2.open(os.path.join(data_dir,f_dtas))
dtas=fdtas['tas']

LWkernel = np.ma.masked_invalid(LWkernel)
print np.min(LWkernel)
print np.max(LWkernel)

LW_glb = np.zeros((b,c),'float64')
for i in xrange(b):
  for j in xrange(c):
    LW_glb[i,j] = np.mean(LWkernel[:,i,j,:,0])

print LW_glb[:,6]
print np.min(LW_glb)
print np.max(LW_glb)

cdict = [ (0.142,0.,0.85), (0.097,0.112,0.97), (0.16,0.342,1.), (0.24,0.531,1.), (0.34,0.692,1.), (0.46,0.829,1.), (0.6,0.92,1.), (0.74,0.978,1.), (1.,1.,1.), (1.,0.948,0.74), (1.,0.840,0.6), (1.,0.676,0.46), (1.,0.472,0.34), (1.,0.24,0.24), (0.97,0.155,0.21), (0.85,0.085,0.187), (0.65,0.,0.13) ]
my_cmap = matplotlib.colors.LinearSegmentedColormap.from_list('My_cmap',cdict)
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
plot1 = ax1.pcolormesh(LW_glb.T,cmap=my_cmap,vmin=-1.8,vmax=1.8,edgecolors='k')
plt.xticks(range(len(tau_bnds)), tau_bnds)
plt.yticks(range(len(lev_bnds)), lev_bnds)
plt.colorbar(plot1)
plot_title='LW Cloud Radiative Kernel'
fig.suptitle(plot_title,fontsize=14)
ax1.set_ylabel('CTP (hPa)',fontsize=12)
ax1.set_xlabel(r'$\tau$',fontsize=12)
#ax1.set_aspect(0.8)
out_f = 'LW_global.eps'
out_path = os.path.join(data_dir, out_f)
plt.savefig(out_path)

SWkernel_map = MV2.masked_array(1e20*np.ones((12,b,c,d,e),'float64'))
for mm in xrange(12):
  for i in xrange(d):
    this=np.squeeze(albedo[mm,i,:])
    tmp=np.squeeze(SWkernel[mm,:,:,i,:])
    for j in xrange(c):
      for k in xrange(b):
	SWkernel_map[mm,k,j,i,:]=np.interp(this,albcs,tmp[k,j,:])
    
SW_glb = np.zeros((b,c),'float64')
for i in xrange(b):
  for j in xrange(c):
    SW_glb[i,j] = np.mean(SWkernel_map[:,i,j,:,:])

#print np.min(SW_glb)
#print np.max(SW_glb)
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
plot1 = ax1.pcolormesh(SW_glb.T,cmap=my_cmap,vmin=-1.8,vmax=1.8,edgecolors='k')
plt.xticks(range(len(tau_bnds)), tau_bnds)
plt.yticks(range(len(lev_bnds)), lev_bnds)
plt.colorbar(plot1)
#ax1.set_aspect(0.8)
plot_title='SW Cloud Radiative Kernel'
fig.suptitle(plot_title,fontsize=14)
ax1.set_ylabel('CTP (hPa)',fontsize=12)
ax1.set_xlabel(r'$\tau$',fontsize=12)
out_f = 'SW_global.eps'
out_path = os.path.join(data_dir, out_f)
plt.savefig(out_path)

net_glb = LW_glb + SW_glb
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
plot1 = ax1.pcolormesh(net_glb.T,cmap=my_cmap,vmin=-1.8,vmax=1.8,edgecolors='k')
plt.xticks(range(len(tau_bnds)), tau_bnds)
plt.yticks(range(len(lev_bnds)), lev_bnds)
plt.colorbar(plot1)
#ax1.set_aspect(0.8)
plot_title='Net Cloud Radiative Kernel'
fig.suptitle(plot_title,fontsize=14)
ax1.set_ylabel('CTP (hPa)',fontsize=12)
ax1.set_xlabel(r'$\tau$',fontsize=12)
out_f = 'net_global.eps'
out_path = os.path.join(data_dir, out_f)
plt.savefig(out_path)

hist1_glb = np.zeros((a,b,c),'float64')
hist2_glb = np.zeros((a,b,c),'float64')
change_glb = np.zeros((a,b,c),'float64')
for mm in xrange(a):
 for i in xrange(b):
  for j in xrange(c):
    data = hist1[mm,i,j,:,:]
    hist1_glb[mm,j,i] = cdutil.averager(data, axis='xy', weight='generate')
    data = hist2[mm,i,j,:,:]
    hist2_glb[mm,j,i] = cdutil.averager(data, axis='xy', weight='generate')
    data = change[mm,i,j,:,:]
    change_glb[mm,j,i] = cdutil.averager(data, axis='xy', weight='generate')

data = cdutil.averager(hist1_glb,axis='0')
hist1_glb = data
data = cdutil.averager(hist2_glb,axis='0')
hist2_glb = data
data = cdutil.averager(change_glb,axis='0')
change_glb = data
#print lat.getBounds()

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
plot1 = ax1.pcolormesh(100.0*hist1_glb.T,cmap=cm.afmhot_r,vmin=0.,vmax=5.0,edgecolors='k')
plt.xticks(range(len(tau_bnds)), tau_bnds)
#plt.xticks(range(len(tau_bnds)-1), tau_bnds[1:])
plt.yticks(range(len(lev_bnds)), lev_bnds)
plt.colorbar(plot1)
#ax1.set_aspect(0.8)
tot = 100.0 * np.sum(hist1_glb)
plot_title='(b) ACCESS Mean Cloud Fraction: '+'%0.2f' % tot + '%'
fig.suptitle(plot_title,fontsize=14)
ax1.set_ylabel('CTP (hPa)',fontsize=12)
ax1.set_xlabel(r'$\tau$',fontsize=12)

out_f = 'hist1_global.eps'
out_path = os.path.join(data_dir, out_f)
plt.savefig(out_path)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
plot1 = ax1.pcolormesh(100.0*hist2_glb.T,cmap=cm.afmhot_r,vmin=0.,vmax=5.0,edgecolors='k')
plt.xticks(range(len(tau_bnds)), tau_bnds)
plt.yticks(range(len(lev_bnds)), lev_bnds)
plt.colorbar(plot1)
#ax1.set_aspect(0.8)
tot = 100.0 * np.sum(hist2_glb)
plot_title='XALLG Mean Cloud Fraction: '+'%0.2f' % tot + '%'
fig.suptitle(plot_title,fontsize=14)
ax1.set_ylabel('CTP (hPa)',fontsize=12)
ax1.set_xlabel(r'$\tau$',fontsize=12)
out_f = 'hist2_global.eps'
out_path = os.path.join(data_dir, out_f)
plt.savefig(out_path)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
plot1 = ax1.pcolormesh(100.0*change_glb.T,cmap=my_cmap,vmin=-0.15,vmax=0.15,edgecolors='k')
#plot1 = ax1.pcolormesh(100.0*change_glb.T,cmap=my_cmap,vmin=-0.45,vmax=0.45,edgecolors='k')
plt.xticks(range(len(tau_bnds)), tau_bnds)
plt.yticks(range(len(lev_bnds)), lev_bnds)
plt.colorbar(plot1)
#ax1.set_aspect(0.8)
tot = 100.0 * np.sum(change_glb)
plot_title='(b) $\Delta$ Cloud Fraction: '+'%0.2f' % tot + '%'
fig.suptitle(plot_title,fontsize=14)
ax1.set_ylabel('CTP (hPa)',fontsize=12)
ax1.set_xlabel(r'$\tau$',fontsize=12)
out_f = 'change_global.eps'
out_path = os.path.join(data_dir, out_f)
plt.savefig(out_path)

# Calculate observed cloud fraction?

fob=cdms2.open(os.path.join(data_dir,fobs))
obs = MV2.masked_array(fob['hist'])
obs = obs[:,:,::-1,:,:]
lat = obs.getLatitude()
lon = obs.getLongitude()
#bounds = fob['tau_bnds']
[a,b,c,d,e] = obs.shape
obs_m = MV2.masked_array(1e20*np.ones((12,b,c,d,e),'float64'))
for mm in xrange(12):
  mm_val = obs[mm::12,:,:,:,:]
  obs_m[mm,:,:,:,:]=MV2.average(mm_val,0)

obs_glb = np.zeros((12,b,c),'float64')
for mm in xrange(12):
 for i in xrange(b):
  for j in xrange(c):
    data = obs_m[mm,i,j,:,:]
    
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

    data.setAxis(0,lat)
    data.setAxis(1,lon)
#    wts=cdutil.area_weights(data)
#    print np.max(wts)
#    print np.min(wts)
#    quit()
    obs_glb[mm,i,j]  = cdutil.averager(data, axis='xy', weight='generate')

data = cdutil.averager(obs_glb,axis='0')
obs_glb = data

print np.max(obs_glb)
print np.min(obs_glb)

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

plot1 = ax1.pcolormesh(obs_glb.T,cmap=cm.afmhot_r,vmin=0.,vmax=5.0,edgecolors='k')
plt.xticks(range(len(tau_bnds)-1), tau_bnds[1:])
plt.yticks(range(len(lev_bnds)), lev_bnds)
plt.colorbar(plot1)
#ax1.set_aspect(0.8)
tot = np.sum(obs_glb)
plot_title='(a) Observed Mean Cloud Fraction: '+'%0.2f' % tot + '%'
fig.suptitle(plot_title,fontsize=14)
ax1.set_ylabel('CTP (hPa)',fontsize=12)
ax1.set_xlabel(r'$\tau$',fontsize=12)

out_f = 'obs_global.eps'
out_path = os.path.join(data_dir, out_f)
plt.savefig(out_path)

quit()

