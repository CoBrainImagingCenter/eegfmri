%!/usr/bin/octave
% test triolog and prismalog functions to read and parse physio log files
% from Siemens Trio and Prisma MR scanners
% FvW 12/2017

clear all, clc
fname0 = 'log_trio.puls';
fname1 = 'log_trio.resp';
fname2 = 'log_prisma.puls';
fname3 = 'log_prisma.resp';
fname = fname3;
%[t, x] = triolog(fname);
[t, x] = prismalog(fname);

figure('Position', [50 50 1800 300])
plot(t, x, '-k')
xlabel('time [sec]')
ylabel('voltage [uV]')
title('physio log')
pause()
