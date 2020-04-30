'''
==========================================================================
Python for Parallelism in Introductory Computer Science Education
SC '13 HPC Educators Program
Steven Bogaerts, Wittenberg University
Joshua Stough, Washington and Lee
http://www.joshuastough.com/SC13
MIT License: see README_LICENSE.txt


file: parallelQuicksort.py
author: stough
Summary: Parallel quicksort versus sequential and built-in.
Using multiprocessing Process/Pipe.

Uses Process/Pipe paradigm to communicate the solutions to
the parent processes.

This code exemplifies the Process/Pipe paradigm of
parallel design.  Quicksort says:
-Partition the list according to a random pivot.
-Quicksort the left half-list.
-Quicksort the right half-list.
So a parallel version comes from the realization that
the two sorts are independent of one another after the
partition:
-Partition the list according to a random pivot.
-Quicksort the two half-lists in parallel.

This is not typical quicksort; it is NlogN in memory
and does not sort the argument lyst as a side effect,
but rather returns a sorted version of the lyst.

Using a shared memory array results in locks.  Even
with the additional memory, there is usually a
reasonable speedup here.

See:
http://docs.python.org/library/multiprocessing.html
http://docs.python.org/py3k/library/multiprocessing.html
==========================================================================
'''
from concurrent.futures import ThreadPoolExecutor as executor
import random, time, sys, queue
from multiprocessing import Process, Pipe , cpu_count
import threading


# Dependencies defined below main()

def main():
    """
    This is the main method, where we:
    -generate a random list.
    -time a sequential quicksort on the list.
    -time a parallel quicksort on the list.
    -time Python's built-in sorted on the list.
    """
    N = 5
    if len(sys.argv) > 1:  # the user input a list size.
        N = int(sys.argv[1])

    # We want to sort the same list, so make a backup.
    lystbck = [1,4,5,7,2,3,0]

    # Sequential quicksort a copy of the list.
    lyst = list(lystbck)  # copy the list
    start = time.time()  # start time
    lyst = quicksort(lyst)  # quicksort the list
    elapsed = time.time() - start  # stop time

    if not isSorted(lyst):
        print('quicksort did not sort the lyst. oops.')

    print('Sequential quicksort: %f sec' % (elapsed))

    # So that cpu usage shows a lull.
    time.sleep(3)

    # Parallel quicksort.
    lyst = list(lystbck)

    start = time.time()
    n = 3  # 2**(n+1) - 1 processes will be instantiated.
    # I set the number of processes to be high since, with
    # a random choice of pivot, it is unlikely the work
    # will distribute evenly.

    # Instantiate a Pipe so that we can receive the
    # process's response.
    pconn, cconn = Pipe()

    # Instantiate a process that executes quicksortParallel
    # on the entire list.

    #threadslist = [x for x in range(2, cpu_count() * 2)]
    #print(threadslist)
    threadslist = [2]
    tLyst = lyst
   # print(tLyst)

    #for x in threadslist:
    #    arr1 = [lyst, x]
    #    print(lyst)
    #    [executor.submit(quicksortParallelThreads,arr1) ]

    thread = threading.Thread(target=quicksortParallelThreads, args=[tLyst,2])
    thread.start()
    thread.join()
    print(tLyst)

    p = Process(target=quicksortParallel, args=(lyst, cconn, n))
    p.start()

    lyst = pconn.recv()
    # Blocks until there is something (the sorted list)
    # to receive.

    p.join()
    elapsed = time.time() - start

    if not isSorted(lyst):
        print('quicksortParallel did not sort the lyst. oops.')

    print('Parallel quicksort: %f sec' % (elapsed))

    time.sleep(3)

    # Built-in test.
    # The underlying c code is obviously the fastest, but then
    # using a calculator is usually faster too.  That isn't the
    # point here obviously.
    lyst = list(lystbck)
    start = time.time()
    lyst = sorted(lyst)
    elapsed = time.time() - start
    print('Built-in sorted: %f sec' % (elapsed))


def quicksort(lyst):
    """
    quicksort implementation, return a new sorted version
    of the input list.
    Faster quicksort in that it relies on built-in list
    comprehensions and concatenation.
    Inspired from Vitalii Vanovschi:
    http://www.parallelpython.com/component/option,com_smf/Itemid,1/action,printpage/topic,105.0
    """
    if len(lyst) <= 1:
        return lyst
    pivot = lyst.pop(random.randint(0, len(lyst) - 1))

    return quicksort([x for x in lyst if x < pivot]) + [pivot] + quicksort([x for x in lyst if x >= pivot])


def quicksortParallelThreads(lyst, threadsNum):
    print(lyst)
    print("thread num: {0}".format(threadsNum))
    if threadsNum <= 1 or len(lyst) <= 1:
        lyst.append(quicksort(lyst))
        print("list:"+ lyst.__str__())
        return
    pivot = lyst.pop(random.randint(0, len(lyst) - 1))
    print("pivot: {0}".format(pivot))
    leftSide = [x for x in lyst if x < pivot]
    rightSide = [x for x in lyst if x >= pivot]

    #executor.submit(target=quicksortParallelThreads, args=(leftSide, threadsNum - 1))
    tLeft = threading.Thread(target=quicksortParallelThreads, args=[leftSide, threadsNum - 1])
    tLeft.start()
    tLeft.join()
    tRight = threading.Thread(target=quicksortParallelThreads, args=[rightSide, threadsNum - 1])
    tRight.start()
    tRight.join()

def quicksortParallel(lyst, conn, procNum):
    """
    Partition the list, then quicksort the left and right
    sides in parallel.
    """

    if procNum <= 0 or len(lyst) <= 1:
        # In the case of len(lyst) <= 1, quicksort will
        # immediately return anyway.
        conn.send(quicksort(lyst))
        conn.close()
        return

    # Create two independent lists (independent in that
    # elements will never need be compared between lists).
    pivot = lyst.pop(random.randint(0, len(lyst) - 1))

    leftSide = [x for x in lyst if x < pivot]
    rightSide = [x for x in lyst if x >= pivot]

    # Creat a Pipe to communicate with the left subprocess
    pconnLeft, cconnLeft = Pipe()
    # Create a leftProc that executes quicksortParallel on
    # the left half-list.
    leftProc = Process(target=quicksortParallel, args=(leftSide, cconnLeft, procNum - 1))

    # Again, for the right.
    pconnRight, cconnRight = Pipe()
    rightProc = Process(target=quicksortParallel, args=(rightSide, cconnRight, procNum - 1))

    # Start the two subprocesses.
    leftProc.start()
    rightProc.start()

    # Our answer is the concatenation of the subprocesses'
    # answers, with the pivot in between.
    conn.send(pconnLeft.recv() + [pivot] + pconnRight.recv())
    conn.close()

    # Join our subprocesses.
    leftProc.join()
    rightProc.join()


def isSorted(lyst):
    """
    Return whether the argument lyst is in non-decreasing order.
    """
    for i in range(1, len(lyst)):
        if lyst[i] < lyst[i - 1]:
            return False
    return True


# Call the main method if run from the command line.
if __name__ == '__main__':
    main()



