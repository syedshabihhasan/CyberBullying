import argparse
import helper as hlp
import statistics
import numpy as np
import matplotlib.pyplot as plt
import os


def plotbars(indv, glob, x_tick_labels, x_label, y_label, title, legend_label, save_file):
    ngroups = 2
    fig, ax = plt.subplots()
    index = np.arange(ngroups)
    bar_width = 0.35
    opacity = 0.4
    error_config = {'ecolor': '0.3'}
    bars1 = plt.bar(index, indv[0], bar_width,
                    alpha=opacity,
                    color='b',
                    #yerr=indv[1],
                    #error_kw=error_config,
                    label=legend_label[0])

    bars2 = plt.bar(index+bar_width, glob[0], bar_width,
                    alpha=opacity,
                    color='r',
                    #yerr=glob[1],
                    #error_kw=error_config,
                    label=legend_label[1])
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.xticks(index + bar_width, x_tick_labels)
    plt.legend()
    plt.savefig(save_file, bbox_inches='tight')


def resetdatares():
    return {'inD': {'between': [], 'before': []},
            'outD': {'between': [], 'before': []},
            'inC': {'between': [], 'before': []},
            'outC': {'between': [], 'before': []}}


def evaluatecustomstat(func, ip_list):
    f_v = func(ip_list)
    std_v = 0 if 1 == len(ip_list) else statistics.stdev(ip_list)
    return f_v, std_v


def calculatestats(gathered_data, func):
    res = {}
    for key in gathered_data.keys():
        between_func_val, between_std = evaluatecustomstat(func, gathered_data[key]['between'])
        before_func_val, before_std = evaluatecustomstat(func, gathered_data[key]['before'])
        res[key] = [(between_func_val, between_std), (before_func_val, before_std)]
    return res


def filldata(fill_with, fill_into, fill_type):
    fill_into['inD'][fill_type].append(fill_with['indegree'])
    fill_into['outD'][fill_type].append(fill_with['outdegree'])
    fill_into['inC'][fill_type] += fill_with['inweights']
    fill_into['outC'][fill_type] += fill_with['outweights']
    return fill_into


def gatherdata(p_data, plot_indv_survey=False):
    to_store = {}
    data_res = resetdatares()
    filled_up = False
    for sno in p_data.keys():
        if plot_indv_survey:
            data_res = resetdatares()
        beforeD = p_data[sno]['before']
        betweenD = p_data[sno]['between']
        if [] == beforeD or [] == betweenD:
            print 'either before or between is empty, skipping'
            continue
        # between dates data
        data_res = filldata(betweenD, data_res, 'between')
        filled_up = True
        # before date, weekly data
        for datum in beforeD:
            data_res = filldata(datum[2], data_res, 'before')
        if plot_indv_survey:
            stats = calculatestats(data_res)
            to_store[sno] = stats
    if not filled_up:
        return None
    else:
        return to_store if plot_indv_survey else data_res


def plotindividual(data, function_to_use, output_directory):
    for pid in data.keys():
        print 'PID: ', pid
        p_data = data[pid]
        print 'gathering data'
        gathered_data = gatherdata(p_data)
        if None == gathered_data:
            print 'PID: ', pid,  ' has no data to process, skipping'
            continue
        print 'calculating stats'
        stats = calculatestats(gathered_data, function_to_use)
        print 'plotting...'
        # create a plot with in and out degree
        indv = [
            (stats['inD'][0][0], stats['outD'][0][0]),
            (stats['inD'][0][1], stats['outD'][0][1])
        ]
        glob = [
            (stats['inD'][1][0], stats['outD'][1][0]),
            (stats['inD'][1][1], stats['outD'][1][1])
        ]
        plotbars(indv, glob, ('incoming', 'outgoing'), 'text communications',
                 '# of degrees', 'bullied:' + pid, ('during', 'before'), output_directory + 'inD_outD_' + pid + '.pdf')
        # create a plot with incoming and outgoing communications
        indv = [
            (stats['inC'][0][0], stats['outC'][0][0]),
            (stats['inC'][0][1], stats['outC'][0][1])
        ]
        glob = [
            (stats['inC'][1][0], stats['outC'][1][0]),
            (stats['inC'][1][1], stats['outC'][1][1])
        ]
        plotbars(indv, glob, ('incoming', 'outgoing'), '# of text communications',
                 '# of texts', 'bullied:' + pid, ('during', 'before'), output_directory + 'inC_outC_' + pid + '.pdf')
        print 'done'


def main():
    parse = argparse.ArgumentParser('Script to create plots of graph statistics')
    parse.add_argument('-i', '-I', type=str, required=True,
                       help='path to graph statistics data')
    parse.add_argument('-o', '-O', type=str, required=True,
                       help='directory to store the generated graphs without leading /')
    parse.add_argument('-f', '-F', type=str, default='mean',
                       help='function to use, currently supports all present in the statistics package')
    args = parse.parse_args()
    ip_file = args.i
    op_dir = args.o
    func = eval('statistics.' + args.f)
    data = hlp.recovervariable(ip_file)
    for ans in data.keys():
        print 'DK:', ans
        dpath = op_dir + '_' + args.f + '/'
        if not os.path.exists(dpath):
            os.mkdir(dpath)
        plotindividual(data[ans], func, dpath)


if __name__ == "__main__":
    main()
