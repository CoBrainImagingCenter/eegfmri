#!/usr/bin/python
# -*- coding: utf-8 -*-
# read and parse Siemens Trio & Prisma physio log files
# Example:
# 	from triolog import triolog
#	t, data = triolog("test.resp", doplot=True)
# Trigger values:
# 5000/6000 = trigger ON/OFF.
# 5002/6002 = beginning/end of the additional header data.
# 5003/6003 = beginning/end of the footer (starting and stopping time of MDH, MPCU time).
# FvW 12/2017

import os, sys
import numpy as np
import matplotlib.pyplot as plt

def findstr(s, L):
    """Find query string s in a list of strings, return indices.

    Args:
        s: query string
        L: list of strings to search
    Returns:
        x: list of indices i, such that s is a substring of L[i]
    """
    x = [i for i, l in enumerate(L) if (l.find(s) >= 0)]
    return x

def get_string_value_pair(s, L):
    "Find query string s in string list L and corresponding int value val."
    i = findstr(s, L)
    val = None
    if i:
        i = i[0]
        val = int(L[i+1][0])
    return i, val

def triolog(filename, doplot=False):
    """Read and parse Siemens Trio physio log files.

    Args:
        filename: full path to log file
        doplot: plot log data after reading (optional)
    Returns:
        t: time axis in sec. (numpy.array)
	data: log data (numpy.array)
    """

    # --- read in all data ---
    #print("[+] File: {:s}".format(filename))
    filedata = []
    with open(filename, "rb") as f:
	for l in f: filedata.append(l.strip("\n"))

    # --- find indices of keys ---
    idx_logstart = findstr("Physiolog_START", filedata)[0]
    idx_logstop = findstr("Physiolog_STOP", filedata)[0]
    idx_samplerate = findstr("Sampling_Rate", filedata)[0]

    # --- parse sampling rate ---
    l = filedata[idx_samplerate]
    fs = float(l[l.find(":")+2:])
    print("[+] Sampling rate: {:.2f} Hz".format(fs))

    # --- parse data ---
    l = filedata[idx_samplerate+1]
    s = l.strip("\n").split(" ")
    while ("" in s): s.remove("")
    data = np.array([float(_) for _ in s])
    del s

    # --- delete scanner trigger values
    trigs = [5000, 5002, 5003, 6000, 6002, 6003]
    for trig in trigs:
	data = np.delete(data, np.where(data==trig)[0])

    # --- time axis ---
    t = np.arange(len(data))/fs

    if doplot:
	fig = plt.figure(1, figsize=(20, 4))
	fig.patch.set_facecolor("white")
	plt.plot(t, data, "-k", linewidth=1)
	plt.xlabel("time [sec]")
	plt.ylabel("voltage [$\mu$V]")
	plt.title(filename)
	plt.tight_layout()
	plt.show()

    return t, data


def parseint(q, txt):
    # search query string q in txt, parse integer after ":", trim spaces
    if (q in txt) & (":" in txt):
        t_ = txt[txt.find(":")+1:].strip()
        return int(t_)
    else:
        return None


def prismalog(filename, doplot=False):
    """Read and parse Siemens Prisma physio log files.

    Args:
        filename: full path to log file
        doplot: plot log data after reading (optional)
    Returns:
        t: time axis in sec. (numpy.array)
        data: log data (numpy.array)
    """

    # time stamp query strings
    q1 = "LogStartMDHTime:"
    q2 = "LogStopMDHTime:"
    q3 = "LogStartMPCUTime:"
    q4 = "LogStopMPCUTime:"

    # --- read in all data ---
    print("[+] File: {:s}".format(filename))
    filedata = []
    with open(filename, "rb") as file_:
        for t in file_:  # text lines
            filedata.append(t.strip("\n"))
            if (q1 in t): t1 = float(t[t.find(":")+1:].replace(" ", ""))
            if (q2 in t): t2 = float(t[t.find(":")+1:].replace(" ", ""))
            if (q3 in t): t3 = float(t[t.find(":")+1:].replace(" ", ""))
            if (q4 in t): t4 = float(t[t.find(":")+1:].replace(" ", ""))
    T_mdh = t2-t1 # msec
    T_mpcu = t4-t3 # msec
    print("[+] Total log time (MDH): {:.1f} sec.".format(T_mdh/1000.))
    print("[+] Total log time (MPCU): {:.1f} sec.".format(T_mpcu/1000.))

    # --- get log type ---
    s_puls = "LOGVERSION_PULS"  # first query string
    s_resp = "LOGVERSION_RESP"  # second query string
    if s_puls in filedata[0]:
        print("[+] PULS log recognized.")
    elif(s_resp in filedata[0]):
        print("[+] RESP log recognized.")
    else:
        print("Unknown log type, exiting...")
        sys.exit(-1)

    # --- get first 5 parameters ---
    s = filedata[0].split(" ")  # main data block as string list
    p5 = [int(s_) for s_ in s[:5]]  # first five parameters
    #print("p5:" + str(p5))
    # Puls: p[2] = 40
    # Resp: p[2] = 20

    # --- get more parameters from query strings ---
    s1 = "uiHwRevisionPeru/ucHWRevLevel:"
    s2 = "uiPartNbrPeruPub:"
    s3 = "uiHwRevisionPpu/ucSWSubRevLevel:"
    s4 = "uiPartNbrPpuPub:"
    s5 = "uiSwVersionPdau/ucSWMainRevLevel:"
    i1, val1 = get_string_value_pair(s1, s)
    i2, val2 = get_string_value_pair(s2, s)
    i3, val3 = get_string_value_pair(s3, s)
    i4, val4 = get_string_value_pair(s4, s)
    i5, val5 = get_string_value_pair(s5, s)
    print("[1] {:s} {:d}".format(s1, val1))
    print("[2] {:s} {:d}".format(s2, val2))
    print("[3] {:s} {:d}".format(s3, val3))
    print("[4] {:s} {:d}".format(s4, val4))
    print("[5] {:s} {:d}".format(s5, val5))

    # --- parse data ---
    data = np.array([int(s[i]) for i in range(i5+2,len(s))])
    # delete scanner trigger values
    trigs = [5000, 5002, 5003, 6000, 6002, 6003]
    for trig in trigs:
        data = np.delete(data, np.where(data==trig)[0])

    # --- time axis ---
    n = 1.*len(data)
    dt_mdh = T_mdh/(n-1)
    dt_mpcu = T_mpcu/(n-1)
    print("[+] dt (MDH): {:.3f} msec.".format(dt_mdh))
    print("[+] dt (MPCU): {:.3f} msec.".format(dt_mpcu))
    dt = dt_mdh # ms
    fs = 1000./dt # Hz
    t = np.arange(n)/fs
    print("[+] Sampling interval: {:.3f} msec.".format(dt))
    print("[+] Sampling rate: {:.3f} Hz.".format(fs))
    #print("[+] Total length of log: {:.1f} samples, {:.2f} sec.".format(n,n/fs))

    if doplot:
        fig = plt.figure(1, figsize=(20, 4))
        fig.patch.set_facecolor("white")
        plt.plot(t, data, "-k", linewidth=1)
        plt.xlabel("time [sec]")
        plt.ylabel("voltage [$\mu$V]")
        plt.title(filename)
        plt.tight_layout()
        plt.show()

    return t, data

def main():
    fname0 = "log_trio.puls"
    fname1 = "log_trio.resp"
    fname2 = "log_prisma.puls"
    fname3 = "log_prisma.resp"
    fname = fname3
    #t, x = triolog(fname, doplot=True)
    t, x = prismalog(fname, doplot=True)
    #print t.shape, x.shape

if __name__ == "__main__":
    os.system("clear")
    main()
