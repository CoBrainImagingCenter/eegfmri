%!/usr/bin/octave
% read and parse Siemens Prisma physio log files
% FvW 05/2018

function [t, data] = prismalog(fname)

% --- time stamp query strings ---
q1 = "LogStartMDHTime:";
q2 = "LogStopMDHTime:";
q3 = "LogStartMPCUTime:";
q4 = "LogStopMPCUTime:";

% --- read in all data ---
disp(['[+] File: ' fname])
i = 1;
fid = fopen(fname);
tline = fgetl(fid);
filedata{i} = tline;
while ischar(tline)
    tline = fgetl(fid);
    i = i+1;
    filedata{i} = tline;
    b1 = findstr(tline, q1);
    if b1
        j = findstr(':', tline);
        t = tline(j+1:end);
        t1 = str2num(t(~isspace(t)));
    end
    b2 = findstr(tline, q2);
    if b2
        j = findstr(':', tline);
        t = tline(j+1:end);
        t2 = str2num(t(~isspace(t)));
    end
    b3 = findstr(tline, q3);
    if b3
        j = findstr(':', tline);
        t = tline(j+1:end);
        t3 = str2num(t(~isspace(t)));
    end
    b4 = findstr(tline, q4);
    if b4
        j = findstr(':', tline);
        t = tline(j+1:end);
        t4 = str2num(t(~isspace(t)));
    end
end
fclose(fid);
T_mdh = t2-t1; # msec
T_mpcu = t4-t3; # msec
disp(['[+] Total log time (MDH): ', num2str(T_mdh/1000.), ' sec.'])
disp(['[+] Total log time (MPCU): ', num2str(T_mpcu/1000.), ' sec.'])

% --- get log type ---
s_puls = 'LOGVERSION_PULS';  % first query string
s_resp = 'LOGVERSION_RESP';  % second query string
for i=1:length(filedata)
    b1 = findstr(filedata{i}, s_puls); % Boolean: pulse
    b2 = findstr(filedata{i}, s_resp);
    b3 = (b1==[]) && (b2==[]);
    if b1
    	disp('[+] PULS log recognized.')
    elseif b2
    	disp('[+] RESP log recognized.')
    elseif b3
        disp('Unknown log type, exiting...')
        quit()
    end
end

% --- split data into strings ---
l = filedata{1};
sp = isspace(l);
if any(sp)
    delta = diff(sp);
    starts = [1, find(delta == -1) + 1];
    stops = [find(delta == 1), length(l)];
    n_values = numel(starts);
    s = cell(1, n_values);
    for i=1:n_values
    	s{i} = l(starts(i):stops(i));
    end
else
    s = {l};
end
% if you have at least Matlab2013b, you can substitute the
% last block of code, starting with 'sp = ', by:
% s = strsplit(l, ' ');

% --- get sampling interval ---
%p5 = zeros(1,5);
%for i=(1:5)
%    p5(i) = str2num(s{i});  % first five parameters
%end

% --- get more parameters from query strings ---
s1 = 'uiHwRevisionPeru/ucHWRevLevel:'; i1 = 0; val1 = -1;
s2 = 'uiPartNbrPeruPub:'; i2 = 0; val2 = -1;
s3 = 'uiHwRevisionPpu/ucSWSubRevLevel:'; i3 = 0; val3 = -1;
s4 = 'uiPartNbrPpuPub:'; i4 = 0; val4 = -1;
s5 = 'uiSwVersionPdau/ucSWMainRevLevel:'; i5 = 0; val5 = -1;
found = [false, false, false, false, false];
for i=1:length(s)
    if findstr(s{i}, s1)
        i1 = i;
        val1 = str2num(s{i+1}(1));
        found(1) = true;
    end
    if findstr(s{i}, s2)
        i2 = i;
        val2 = str2num(s{i+1}(1));
        found(2) = true;
    end
    if findstr(s{i}, s3)
        i3 = i;
        val3 = str2num(s{i+1}(1));
        found(3) = true;
    end
    if findstr(s{i}, s4)
        i4 = i;
        val4 = str2num(s{i+1}(1));
        found(4) = true;
    end
    if findstr(s{i}, s5)
        i5 = i;
        val5 = str2num(s{i+1}(1));
        found(5) = true;
    end
    if all(found) % stop searching ...
        break;
    end
end
disp(['[1] ' s1 ' ' num2str(val1)])
disp(['[2] ' s2 ' ' num2str(val2)])
disp(['[3] ' s3 ' ' num2str(val3)])
disp(['[4] ' s4 ' ' num2str(val4)])
disp(['[5] ' s5 ' ' num2str(val5)])

% --- parse data ---
data = [];
for i = i5+2:length(s) % data block starts after 5th parameter
    x = str2num(s{i});
    if x
    	data = [data x];
    end
end

% --- delete scanner trigger values ---
trigs = [5000, 5002, 5003, 6000, 6002, 6003];
for trig=trigs
    data(data==trig) = [];
end

% --- time axis ---
n = length(data);
dt_mdh = T_mdh/n;
dt_mpcu = T_mpcu/n;
disp(["[+] dt (MDH): ", num2str(dt_mdh), ' msec.'])
disp(["[+] dt (MPCU): ", num2str(dt_mpcu), ' msec.'])
dt = dt_mdh; # ms
fs = 1000./dt; # Hzdisp(['[+] Sampling interval: ' num2str(dt) ' msec.'])
t = (0:n-1)/fs;
disp(['[+] Sampling interval: ' num2str(dt) ' msec.'])
disp(['[+] Sampling rate: ' num2str(fs) ' Hz.'])
disp(['[+] Total length of log: ', num2str(n) ' samples, ' num2str(n/fs) ' sec.'])

end
