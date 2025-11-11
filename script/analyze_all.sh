#!/bin/bash
# 不完全なので修正・追記が必要
# nohup sh $WORK/tc_analyze/script/analyze_all.sh &

# center
echo "$(date): center"
python $WORK/tc_analyze/center/ss_slp_center_calc.py
python $WORK/tc_analyze/center/ss_slp_center_plot.py $style
python $WORK/tc_analyze/center/ss_slp_center_velocity.py $style
python $WORK/tc_analyze/center/mass_all.py $style
python $WORK/tc_analyze/center/mass_under20km.py $style
python $WORK/tc_analyze/center/mass.py $style

# 3d
echo "$(date): 3d"
sh $WORK/tc_analyze/3d/whole_domain.sh
sh $WORK/tc_analyze/3d/vortex_region.sh
python $WORK/tc_analyze/3d/streamplot_whole_domain.py $style
python $WORK/tc_analyze/3d/vortex_region_wind_uv_abs_plot.py $style
python $WORK/tc_analyze/3d/whole_domain_wind_uv_abs_plot.py $style
python $WORK/tc_analyze/3d/ms_wind_radial_tangential_calc.py
python $WORK/tc_analyze/3d/ms_wind_tangential_plot.py $style
python $WORK/tc_analyze/3d/ms_wind_radial_plot.py $style
python $WORK/tc_analyze/3d/vorticity_z_calc.py
python $WORK/tc_analyze/3d/vorticity_z_vortex_region_plot.py $style
python $WORK/tc_analyze/3d/vorticity_z_absolute_whole_domain_plot.py $style
python $WORK/tc_analyze/3d/divergence_calc.py
python $WORK/tc_analyze/3d/divergence_vortex_region_plot.py $style
python $WORK/tc_analyze/3d/theta_e_calc.py
python $WORK/tc_analyze/3d/theta_e_plot_vortex_region.py $style
python $WORK/tc_analyze/3d/theta_e_plot_whole_region.py $style
python $WORK/tc_analyze/3d/psi_calc.py
python $WORK/tc_analyze/3d/psi_plot.py $style
python $WORK/tc_analyze/3d/psi_plot_vortex_region.py $style
python $WORK/tc_analyze/3d/psi_plot_r200.py $style
python $WORK/tc_analyze/3d/ms_dyn_radial_tangential_calc.py
python $WORK/tc_analyze/3d/ms_dyn_tangential_plot.py $style
python $WORK/tc_analyze/3d/ms_dyn_radial_plot.py $style
python $WORK/tc_analyze/3d/relative_u.py
python $WORK/tc_analyze/3d/relative_v.py
python $WORK/tc_analyze/3d/relative_wind_radial_tangential_calc.py
python $WORK/tc_analyze/3d/relative_wind_tangential_plot.py $style
python $WORK/tc_analyze/3d/relative_wind_radial_plot.py $style
python $WORK/tc_analyze/3d/relative_wind_uv_abs_calc.py
python $WORK/tc_analyze/3d/relative_wind_uv_abs_plot.py $style


echo "$(date): 2d/vortex_region"
sh $WORK/tc_analyze/2d/whole_domain.sh
sh $WORK/tc_analyze/2d/vortex_region.sh
python $WORK/tc_analyze/2d/ss_wind10m_abs_whole_domain.py $style
python $WORK/tc_analyze/2d/ss_wind10m_abs_vortex_region.py $style
python $WORK/tc_analyze/2d/ss_wind10m_abs_vortex_region2.py $style
python $WORK/tc_analyze/2d/ss_wind10m_max_calc.py
python $WORK/tc_analyze/2d/ss_wind10m_max_plot.py $style
python $WORK/tc_analyze/2d/ss_wind10m_radial_tangential_calc.py
python $WORK/tc_analyze/2d/ss_wind10m_tangential_plot.py $style
python $WORK/tc_analyze/2d/ss_wind10m_radial_plot.py $style
echo "$(date): azim_2d_calc"
sh $WORK/tc_analyze/azim_mean/azim_2d_calc.sh
echo "$(date): azim_2d_plot"
sh $WORK/tc_analyze/azim_mean/azim_2d_plot.sh
echo "$(date): azim_3d_calc"
sh $WORK/tc_analyze/azim_mean/azim_3d_calc.sh
echo "$(date): azim_3d_plot"
sh $WORK/tc_analyze/azim_mean/azim_3d_plot.sh
python $WORK/tc_analyze/azim_mean/azim_wind10m_calc.py
python $WORK/tc_analyze/azim_mean/azim_wind10m_tangential_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_wind10m_radial_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_wind10m_tangential_max_calc.py
python $WORK/tc_analyze/azim_mean/azim_wind10m_tangential_max_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_momentum_calc.py
python $WORK/tc_analyze/azim_mean/azim_momentum_plot.py $style
sh $WORK/tc_analyze/azim_mean/azim_pert_3d_calc.sh
sh $WORK/tc_analyze/azim_mean/azim_pert_3d_plot.sh
python $WORK/tc_analyze/azim_mean/azim_stream_calc.py
python $WORK/tc_analyze/azim_mean/azim_stream_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_stream_max_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_stream2_calc.py
python $WORK/tc_analyze/azim_mean/azim_stream2_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_theta_calc.py
python $WORK/tc_analyze/azim_mean/azim_theta_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_theta_e_calc.py
python $WORK/tc_analyze/azim_mean/azim_theta_e_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_vorticity_z_calc.py
python $WORK/tc_analyze/azim_mean/azim_vorticity_z_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_vorticity_z_absolute_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_wind_calc.py
python $WORK/tc_analyze/azim_mean/azim_wind_tangential_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_wind_radial_plot.py $style
python $WORK/tc_analyze/azim_mean/azim_wind_calc2.py
python $WORK/tc_analyze/azim_mean/azim_wind_radial_plot2.py $style
python $WORK/tc_analyze/azim_mean/azim_wind_tangential_plot2.py $style

# z_profile
sh $WORK/tc_analyze/z_profile/z_profile_calc.sh
sh $WORK/tc_analyze/z_profile/z_profile_plot.sh
sh $WORK/tc_analyze/z_profile/vortex_region_calc.sh
sh $WORK/tc_analyze/z_profile/vortex_region_plot.sh
python $WORK/tc_analyze/z_profile/zeta_calc.py
python $WORK/tc_analyze/z_profile/zeta_plot.py $style
python $WORK/tc_analyze/z_profile/zeta_absolute_plot.py $style
python $WORK/tc_analyze/z_profile/hf_calc.py
python $WORK/tc_analyze/z_profile/hf_plot.py $style
