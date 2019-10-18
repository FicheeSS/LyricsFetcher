from mutagen.flac import FLAC
import os
import time
import csv
import multiprocessing
import matplotlib.pyplot as plt

from main import *
max_tests = 25
tstFiles = []
for i in range(max_tests):
    tstFiles.append(FLAC(os.getcwd() + "/tstFile.flac"))
TimeResults = []
BatchNumber = []


for tst in range(max_tests):
    tst += 1
    print("Starting with bach size = " + str(tst))
    st = time.time()
    ProcessFile = tstFiles
    # Cut the ProcessFile list into list of JobLimit size
    JobsFile = []
    for i in range(int(len(ProcessFile)/tst+1)):
        JobsFile.append([])
    for i in range(int(len(ProcessFile)/tst)+1):
        if (len(ProcessFile) - tst * i) > tst:
            for y in range(tst):
                JobsFile[i].append(ProcessFile[(i+1) * y])
        else:
            for y in range(len(ProcessFile) - tst * i):
                JobsFile[i].append(ProcessFile[(i+1) * y])

    jobs = []
    for i in range(len(JobsFile)):
        for y in range(len(JobsFile[i])):
            p = multiprocessing.Process(
                target=GetLyricsFromFile, args=(JobsFile[i][y],))
            p.start()
            jobs.append(p)
        for proc in jobs:
            proc.join()
    
    et = time.time()
    BatchNumber.append(tst) 
    TimeResults.append(et-st)
    print("Time taken = " + str(et-st))

#write to csv
with open("results.csv","w") as csv_file:
     csv_writer = csv.writer(csv_file)
     csv_writer.writerow(BatchNumber)
     csv_writer.writerow(TimeResults)

plt.plot(BatchNumber,TimeResults,label="Time taken [s]")
plt.xlabel("Time taken [s]")
plt.ylabel("Number of batch")
plt.savefig("results.png")
plt.show()


print("Use this setting :" + str(TimeResults.index(min(TimeResults))+1) )
