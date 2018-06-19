;**********************************************
; Calculate average LW and SW CF at lat lon
; from Harvey's test.nc
; Plot as Zelinka Fig 5a,b,c
;
; JRB 10.03.15
;***********************************************

load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"

 begin

 nlon = 192
 nlat = 145
 nlev = 7
 ntau = 7
 nmon = 12

 cf_lw = new((/nmon,ntau,nlev,nlat,nlon/),float) 
 cl_sw = new((/nmon,ntau,nlev,nlat,nlon/),float)

 cf_sw_ave2 = new((/nmon,nlat,nlon/),float) 
 plot_lw = new((/nlat,nlon/),float) 
 plot_sw = new((/nlat,nlon/),float) 

 low_lev = (/0, 1/)    ; 1000 to 680 
 mid_lev = (/2, 3/)    ; 680 to 440
 hig_lev = (/4, 5, 6/) ; 440 to 50
 all_lev = (/0, 1, 2, 3, 4, 5, 6/)

 thn_tau = (/0, 1, 2/); < 3.6 
 med_tau = (/3, 4/)   ; 3.6 to 23 
 thk_tau = (/5, 6/)   ; > 23
 all_tau = (/0, 1, 2, 3, 4, 5, 6/)

; Processed and regridded data:

 a1 = addfile("/g/data/eg3/jxb548/cloud/cloud_feedback_xallf_xallg.nc","r") 

 cf_lw_d = a1->LW_cld_fdbk(:,:,:,:,:)                           
 cf_lw = dble2flt(cf_lw_d)

 cf_sw_d = a1->SW_cld_fdbk(:,:,:,:,:)                           
 cf_sw = dble2flt(cf_sw_d)

 latd = a1->lat
 lat = dble2flt(latd)
 lond = a1->lon
 lon = dble2flt(lond)
 tau = a1->tau
 lev = a1->lev  
 
; sum over all tau

; cf_lw_ave1 = dim_sum_Wrap(cf_lw(time|:,lev|:,lat|:,lon|:,tau|thk_tau) )  
; cf_sw_ave1 = dim_sum_Wrap(cf_sw(time|:,lev|:,lat|:,lon|:,tau|thk_tau) ) 
 cf_lw_ave1 = dim_sum_n_Wrap(cf_lw,1)
 cf_sw_ave1 = dim_sum_n_Wrap(cf_sw,1)

; sum over all / some levs

 cf_lw_ave2 = dim_sum_Wrap( cf_lw_ave1(time|:,lat|:,lon|:,lev|low_lev) )   
 cf_sw_ave2 = dim_sum_Wrap( cf_sw_ave1(time|:,lat|:,lon|:,lev|low_lev) ) 
; cf_lw_ave2 = dim_sum_n_Wrap(cf_lw_ave1,1)
; cf_sw_ave2 = dim_sum_n_Wrap(cf_sw_ave1,1)

; average over all months
 
  cf_lw_ave3 = dim_avg_n_Wrap(cf_lw_ave2,0)

;;; if missing values in sw then set to zero

 do i = 0, nlat-1
 do j = 0, nlon-1
 do m = 0, 11
  if ( ismissing(cf_sw_ave2(m,i,j)) ) then
   cf_sw_ave2(m,i,j) = 0.0
  end if
 end do
 end do
 end do

 cf_sw_ave3 = dim_avg_n_Wrap(cf_sw_ave2,0)
  
; printVarSummary(cf_lw_ave3)
; printVarSummary(cf_sw_ave3)

 plot_lw = 100*cf_lw_ave3
 plot_sw = 100*cf_sw_ave3

 ; write out lw and sw 2d fields
  
; do i = 0, nlat-1
;    print( sprintf("%8.4f",plot_sw(i,:)) )
; end do

 plot_net = plot_lw + plot_sw

 plot_test = plot_lw
 plot_test = mask(plot_lw,(plot_lw.lt.100),True)

 plot_lw!0 = "lat"
 plot_lw&lat = lat
 plot_lw!1 = "lon"
 plot_lw&lon = lon

 plot_sw!0 = "lat"
 plot_sw&lat = lat
 plot_sw!1 = "lon"
 plot_sw&lon = lon

 plot_net!0 = "lat"
 plot_net&lat = lat
 plot_net!1 = "lon"
 plot_net&lon = lon

 plot_test!0 = "lat"
 plot_test&lat = lat
 plot_test!1 = "lon"
 plot_test&lon = lon

;************************************************
;set up colors
;*************************************************
  wks = gsn_open_wks("oldeps","climo") 
  gsn_define_colormap(wks,"cmp_b2r")         
 ; gsn_define_colormap(wks,"BlAqGrYeOrReVi200") 
 ; gsn_define_colormap(wks,"WhiteBlueGreenYellowRed") 
 ; gsn_reverse_colormap(wks)
;************************************************
; create panel plots
;*************************************************

  nplot = 1

  plot   = new (nplot , graphic)                    ; create graphical array

  res                      = True               ; plot options desired


  res@gsnSpreadColors      = True    		; use full range of colors
  res@cnFillOn             = True               ; turn on color fill
  res@cnInfoLabelOn        = False              ; turn off contour info label
  res@cnLinesOn            = False              ; turn off contour lines
  res@cnLineLabelsOn       = False              ; turn off line labels
 
  res@cnLevelSelectionMode = "ManualLevels"    ; set explicit contour levels
  res@cnMinLevelValF  =   -10			; set the minimum contour level
  res@cnMaxLevelValF  =    10			; set the maximum contour level
  res@cnLevelSpacingF =    1			; set the interval between contours  
;  res@cnMinLevelValF  =   -2			; set the minimum contour level
;  res@cnMaxLevelValF  =    2			; set the maximum contour level
;  res@cnLevelSpacingF =    0.2			; set the interval between contours  

  res@mpFillOn             = True            
  res@mpCenterLonF         = 180   

 ;  res@mpProjection = "Robinson"             

  res@mpMinLonF            =    0.              
  res@mpMaxLonF            =  360.
  res@mpMinLatF            =  -90. 
  res@mpMaxLatF            =   90.

  res@txFontHeightF   	   = 0.024          
  res@tiMainFontHeightF    = 0.024             
  res@tiMainString = ""

  res@tmXTOn = False
  res@tmXBMajorLengthF	   = 0.014	       
  res@tmXBMinorLengthF 	   = 0.007
  res@tmYLMajorLengthF 	   = 0.014
  res@tmYLMinorLengthF 	   = 0.007

  res@tmXBLabelFontHeightF = 0.016	       
  res@tmYLLabelFontHeightF = 0.016

  res@lbLabelBarOn         = True 
 ; res@lbLabelBarOn         = False 

  res@lbOrientation        = "vertical" 
  res@lbLabelFontHeightF = 0.014
  res@lbLabelStride        = 2
 
  res@mpFillOn             = True               ; turn off gray continents
  res@gsnStringFontHeightF = 0.026
 
  res@gsnLeftStringFontHeightF = 0.018 
  res@gsnRightStringFontHeightF = 0.018

  rad  = 4.0 * atan(1.0) / 180.0
  clat   = cos(lat*rad)
  
  glob_ave =  wgt_areaave(plot_sw(:,:),clat,1.0,0) 

  res@gsnRightString = "Global mean = "+sprintf("%6.2f",glob_ave)+" W/m2/K"

  print(sprintf("%6.2f",glob_ave))

;  res@gsnRightString = " "
;  res@gsnLeftString = "(c) Net Total Cloud Feedback"
  res@gsnLeftString = "(b) SW Low Cloud"

  plot = gsn_csm_contour_map_ce(wks,plot_sw(:,:),res)

end
