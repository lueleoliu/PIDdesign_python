# -*- coding: utf-8 -*-

import os
import GW_functions as gw
from multiprocessing.dummy import Pool as ThreadPool
import shutil


def pid_cal(root_dir):
    genfile = os.path.join(root_dir, 'GenFile.exe')
    gw.single_run(genfile)

    cal_folder = os.path.join(root_dir, 'PIDCal')
    exe_path = gw.get_typefile(cal_folder, '.exe')
    former_range = []
    later_range = []

    for exe in exe_path:
        if 'Pitch1' in exe:
            former_range.append(exe)
        elif 'Torque' in exe:
            former_range.append(exe)
        else:
            later_range.append(exe)

    pool = ThreadPool()
    pool.map(gw.single_run, former_range)
    pool.close()
    pool.join()

    first_pitch = os.path.join(cal_folder, 'Pitch1')
    txt_path = gw.get_typefile(first_pitch, '.txt')
    first_result = ''
    for txt in txt_path:
        if 'Result' in os.path.basename(txt):
            first_result = txt
    with open(first_result, 'r') as first:
        info = first.read()
        first_td = gw.do_split(info, ' ', 3)

    other_station = []
    for exe in exe_path:
        if 'Pitch1' not in exe and 'Torque' not in exe:
            other_dir = os.path.dirname(exe)
            other_txt = gw.get_typefile(other_dir, '.txt')
            for txt in other_txt:
                if 'Station.txt' in txt:
                    other_station.append(txt)

    for txt in other_station:
        with open(txt, 'r') as station:
            info = station.read()
            temp = info.split(' ')
            temp[3] = first_td
            info_f = ' '.join(temp)
        with open(txt, 'w') as station:
            station.write(info_f)

    # pool = ThreadPool()
    # pool.map(gw.single_run, later_range)
    # pool.close()
    # pool.join()
    fit_exe = os.path.join(root_dir, 'comfit.exe')
    shutil.copy(fit_exe, first_pitch)
    gw.single_run(os.path.join(first_pitch,  'comfit.exe'))


if __name__ == '__main__':
    path = os.path.abspath('.')
    gw.prepare(path)
    gw.gen_standard(path)
    gw.gen_campbell(path)
    gw.gen_linear_model(path)
    gw.get_wt_basic_info(path)
    pid_cal(path)
    gw.logging(path, ' PID优化计算完成')
    gw.get_result(path)
    gw.print_pid_to_xml(path)
    gw.print_filters_to_xml(path)


