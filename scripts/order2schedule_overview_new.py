#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Matt Post, June 2014

"""
Generates the daily overviews for the main conference schedule. Amalgamates multiple order
iles containing difference pieces of the schedule and outputs a schedule for each day,
rooted in an optionally-supplied directory.

Usage:

 cat data/{papers,shortpapers,demos,srw}/order | order2schedule_overview.py

"""

import re, os
import sys, csv
import argparse
from handbook import *
from collections import defaultdict

PARSER = argparse.ArgumentParser(description="Generate overview schedules for *ACL handbooks")
PARSER.add_argument("-output_dir", dest="output_dir", default="auto/papers")
args = PARSER.parse_args()

if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

def time_min(a, b):
    ahour, amin = a.split(':')
    bhour, bmin = b.split(':')
    if ahour == bhour:
        if amin < bmin:
            return a
        elif amin > bmin:
            return b
        else:
            return a
    elif ahour < bhour:
        return a
    else:
        return b

def time_max(a, b):
    if time_min(a, b) == a:
        return b
    return a

# List of dates
dates = []
schedule = defaultdict(defaultdict)
sessions = defaultdict()
session_times = defaultdict()

for line in sys.stdin:
    line = line.rstrip()

    # print "LINE", line

    if line.startswith('*'):
        day, date, year = line[2:].split(', ')
        if not (day, date, year) in dates:
            dates.append((day, date, year))

    elif line.startswith('='):
        str = line[2:]
        time_range, session_name = str.split(' ', 1)
        sessions[session_name] = Session(line, (day, date, year))

    elif line.startswith('+') or line.startswith('!'):
        timerange, title = line[2:].split(' ', 1)
        title, keys = extract_keywords(title)
        if keys.has_key('by'):
            title = "%s (%s)" % (title.strip(), keys['by'])
        session_name = None

        if not schedule[(day, date, year)].has_key(timerange):
            schedule[(day, date, year)][timerange] = []
        schedule[(day, date, year)][timerange].append(title)

# Take all the sessions and place them at their time
for session in sorted(sessions.keys()):
    day, date, year = sessions[session].date
    timerange = sessions[session].time
#    print >> sys.stderr, "SESSION", session, day, date, year, timerange
    if not schedule[(day, date, year)].has_key(timerange):
        schedule[(day, date, year)][timerange] = []
    schedule[(day, date, year)][timerange].append(sessions[session])

def sort_times(a, b):
    print a
    print b
    print a[0].split('--')
    print a[0].split('--')[0].split(':')
    ahour, amin = a[0].split('--')[0].split(':')
    bhour, bmin = b[0].split('--')[0].split(':')
    if ahour == bhour:
        return cmp(int(amin), int(bmin))
    return cmp(int(ahour), int(bhour))

def minus12(time):
    hours, minutes = time.split(':')
    #if hours.startswith('0'):
    #    hours = hours[1:]
    #if int(hours) >= 13:
    #    hours = `int(hours) - 12`

    return '%s:%s' % (hours, minutes)

print(dates)
for date in dates:
    day, num, year = date
    path = os.path.join(args.output_dir, '%s-overview.tex' % (day))
    out = open(path, 'w')
    print >> sys.stderr, "Writing file", path
    print >>out, '\\section*{Overview}'
    print >>out, '\\renewcommand{\\arraystretch}{1.2}'
    print >>out, '\\begin{SingleTrackSchedule}'
    for timerange, events in sorted(schedule[date].iteritems(), cmp=sort_times):
        print timerange, events
        start, stop = timerange.split('--')

        if len(events) >= 3:
            # Parallel sessions (assume there are at least 4)
            sessions = [x for x in events]

            # turn "Session 9A" to "Session 9"
            title = 'Session %s' % (sessions[0].num)
            num_parallel_sessions = len(sessions)
            if num_parallel_sessions <= 6:
                rooms = ['\emph{\Track%cLoc}' % (chr(65+x)) for x in range(num_parallel_sessions)]
                # column width in inches
                width = 3.7 / num_parallel_sessions
                print >>out, '  %s & -- & %s &' % (minus12(start), minus12(stop))
                print >>out, '  \\begin{tabular}{|%s|}' % ('|'.join(['p{%.1fin}' % width for x in range(num_parallel_sessions)]))
                print >>out, '    \\multicolumn{%d}{l}{{\\bfseries %s}}\\\\\\hline' % (num_parallel_sessions,title)
                print >>out, ' & '.join([session.desc.replace('#','') for session in sessions]), '\\\\'
                print >>out, ' & '.join(rooms), '\\\\'
                print >>out, '  \\hline\\end{tabular} \\\\'
            else:
                max_cols = 6
                rooms = ['\emph{\Track%cLoc}' % (chr(65+x)) for x in range(num_parallel_sessions)]
                # column width in inches
                width = 3.7 / max_cols
                print >>out, '  %s & -- & %s &' % (minus12(start), minus12(stop))
                print >>out, '  \\begin{tabular}{|%s|}' % ('|'.join(['p{%.1fin}' % width for x in range(max_cols)]))
                print >>out, '    \\multicolumn{%d}{l}{{\\bfseries %s}}\\\\\\hline' % (max_cols,title)
                for i in range(num_parallel_sessions / max_cols):
                    if i > 0:
                        print >>out, '\\hline'
                    print >>out, ' & '.join([session.desc.replace('#','') for session in sessions[i*max_cols:(i+1)*max_cols]]), '\\\\'
                    print >>out, ' & '.join(rooms[i*max_cols:(i+1)*max_cols]), '\\\\\\hline'
                loc = rooms[-1]
                event = sessions[-1].desc.replace('#','')
                print >> out, '\multicolumn{6}{|p{3.7in}|}{{\\bfseries [Posters\\&Demos]:} %s \\hfill %s} \\\\'%(event, loc)
                #print >> out, '\multicolumn{4}{|l|}{%s} \\\\' % (loc.replace('Mini-break','Coffee'))
                print >>out, '  \\hline\\end{tabular} \\\\'
        else:

            for event in events:
                # A regular event
                print "event:", event, " ", type(event)
                print >>out, '  %s & -- & %s &' % (minus12(start), minus12(stop))
                try:
                    loc = event.split(' ')[0].capitalize()
                except AttributeError:
                    loc = "TODO Location"
                print >>out, '  {\\bfseries %s} \\hfill \emph{\\%sLoc}' % (event, loc.replace('Mini-break','Coffee'))
                print >>out, '  \\\\'

    print >>out, '\\end{SingleTrackSchedule}'
    print >>out, '\\clearpage'
    out.close()

