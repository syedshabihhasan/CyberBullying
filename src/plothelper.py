from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import helper as hlp
from math import ceil
from basicInfo import plottingdetails as plt_details


class plots:
    def superimposebullyingdata(self, to_superimpose, axis, data):
        for category in to_superimpose.keys():
            if [] is not to_superimpose[category]:
                week_list = to_superimpose[category]
                i = True
                for weekno in week_list:
                    axis.axvline(x=weekno, ymin=plt_details.vline_ymin[category], ymax=plt_details.vline_ymax[category],
                                 linewidth=4, color=plt_details.bullying_category_markers[category],
                                 label=category if i else '')
                    i = False
        return axis

    def plotweeklyprogression(self, weekly_dict, location_to_store, title,
                              x_label, y_label, overlay_data=None, sentiment_legend=None):
        print 'Plotting weekly progression...'
        c_scheme = ['go-', 'ro-', 'ko-']
        for pid in weekly_dict.keys():
            p_dict = weekly_dict[pid]
            to_superimpose = {}
            if overlay_data is not None:
                if pid in overlay_data.keys():
                    to_superimpose = overlay_data[pid]
            week_list = p_dict.keys()
            week_list.sort()
            p_data_in = [] if sentiment_legend is None else [[], [], []]
            p_data_out = [] if sentiment_legend is None else [[], [], []]
            for week_no in week_list:
                if sentiment_legend == None:
                    p_data_in.append(p_dict[week_no][0])
                    p_data_out.append(p_dict[week_no][1])
                else:
                    for idx in range(3):
                        p_data_in[idx].append(p_dict[week_no][0][idx])
                        p_data_out[idx].append(p_dict[week_no][1][idx])
            fig, axes = plt.subplots(2, 1, sharex=True, sharey=True)
            if sentiment_legend is not None:
                for idx in range(3):
                    axes[0].plot(range(1, len(week_list) + 1), p_data_in[idx],
                                 c_scheme[idx], linewidth=2, alpha=0.5, label=sentiment_legend[idx])
                    axes[0].set_title('Incoming')
                    axes[1].plot(range(1, len(week_list) + 1), p_data_out[idx],
                                 c_scheme[idx], linewidth=2, alpha=0.5, label=sentiment_legend[idx])
                    axes[1].set_title('Outgoing')
                # axes[0].plot(range(1, len(week_list) + 1), p_data_in,
                #              'o-', linewidth=2, alpha=0.5)
                # axes[1].plot(range(1, len(week_list) + 1), p_data_out,
                #              'o-', linewidth=2, alpha=0.5)
            else:
                axes[0].plot(range(1, len(p_data_in) + 1), p_data_in,
                             'ko-', linewidth=2, label='In', alpha=0.5)
                axes[1].plot(range(1, len(p_data_out) + 1), p_data_out,
                             'bo-', linewidth=2, label='Out', alpha=0.5)
            if to_superimpose:
                axes[0] = self.superimposebullyingdata(to_superimpose, axes[0], p_data_in)
                axes[1] = self.superimposebullyingdata(to_superimpose, axes[1], p_data_out)
            plt.suptitle(title + '(' + pid + ')')
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            art = []
            for ax in axes:
                ax.set_xlabel(x_label)
                ax.set_ylabel(y_label)
                ax.set_xticks(np.arange(0, max(week_list) + 1, 2))
                lgd = ax.legend(loc=2, bbox_to_anchor=(1.05, 1))
                art.append(lgd)
                ax.grid(True)
            plt.savefig(location_to_store + pid + '.pdf', additional_artists=art, bbox_inches='tight')
            plt.close(fig)

    def generatetablehist(self, input_dictionary, file_path, generate_totals=False, bin_dist=-1):
        max_value = float('-inf')
        bin_dist = 5 if -1 == bin_dist else bin_dist
        for key in input_dictionary.keys():
            max_value = max(input_dictionary[key]) if max(input_dictionary[key]) > max_value else max_value
        max_value = int(ceil(max_value / bin_dist) * bin_dist)
        bins = range(0, max_value + 1, bin_dist)
        print 'bins: ', bins, 'max:', max_value
        first_line = ['category']
        for idx in range(1, len(bins)):
            first_line.append(str(bins[idx - 1]) + ' to ' + str(bins[idx]))
        if generate_totals:
            first_line.append('no. of people')
        final_to_write = [first_line]
        for key in input_dictionary.keys():
            h, be = np.histogram(input_dictionary[key], bins, range=(0, max_value))
            h = h / sum(h)
            if generate_totals:
                final_to_write.append([key] + h.tolist() + [len(input_dictionary[key])])
            else:
                final_to_write.append([key] + h.tolist())
        hlp.writecsv(final_to_write, file_path)

    def generatecdf(self, input_dictionary, x_label, y_label, title, to_store_at):
        nbins = 20
        fig = plt.figure()
        n = len(input_dictionary.keys())
        idx = 1
        ax = fig.add_subplot(111)
        for key in input_dictionary.keys():
            ax.hist(input_dictionary[key], nbins, normed=True,
                    histtype='step', cumulative=True, label=key, linewidth=2)

        plt.ylabel(y_label)
        plt.grid(True)
        plt.ylim(0, 1.05)
        plt.yticks(np.arange(0, 1.1, 0.1))
        plt.suptitle(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.legend(loc=4)
        plt.savefig(to_store_at)

    def __init__(self):
        pass
