#!/bin/bash
# 中心を使わない解析
# nohup sh $WORK/tc_analyze/script/analyze2.sh &

python $WORK/tc_analyze/center/mass_all.py $style
python $WORK/tc_analyze/center/mass_under20km.py $style

# 3d
echo "$(date): 3d"
sh $WORK/tc_analyze/3d/whole_domain.sh
python $WORK/tc_analyze/3d/whole_domain_wind_uv_abs_plot.py $style
python $WORK/tc_analyze/3d/vorticity_z_calc.py
python $WORK/tc_analyze/3d/vorticity_z_absolute_whole_domain_plot.py $style
python $WORK/tc_analyze/3d/divergence_calc.py
python $WORK/tc_analyze/3d/theta_e_calc.py
python $WORK/tc_analyze/3d/theta_e_plot_whole_region.py $style
python $WORK/tc_analyze/3d/psi_calc.py
python $WORK/tc_analyze/3d/psi_plot.py $style

echo "$(date): 2d/vortex_region"
sh $WORK/tc_analyze/2d/whole_domain.sh
python $WORK/tc_analyze/2d/ss_wind10m_abs_whole_domain.py $style
python $WORK/tc_analyze/2d/ss_wind10m_max_calc.py
python $WORK/tc_analyze/2d/ss_wind10m_max_plot.py $style
