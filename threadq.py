import threading
from queue import Queue
import random, time
from threading import Thread, Event, Lock
import multiprocessing



final_results = []
lock = Lock()
# A thread that produces data

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def isSorted(lyst):
    """
    Return whether the argument lyst is in non-decreasing order.
    """
    for i in range(1, len(lyst)):
        if lyst[i] < lyst[i - 1]:
            return False
    return True

def producer(out_q, lyst, num_of_threads,lock):

    p_evt = []
    pivot = lyst.pop(random.randint(0, len(lyst) - 1))
    print("pivot: {0}".format(pivot))
    leftSide = [x for x in lyst if x < pivot]
    pack = int(len(leftSide)/num_of_threads)
    #print(leftSide.__str__())
    print("len(leftSide) = {0} pack = {1} ".format(len(leftSide),pack))

    index_wait = 0
    if pack == 0:
        pack=1;
    my_chunks = chunks(leftSide, pack)
    for i in my_chunks:
        p_evt.append(Event())
        out_q.put((i, p_evt[index_wait]))
        index_wait+=1

    #print("producer start wating")
    for i in range(index_wait):
        p_evt[i].wait()
    #print("producer Stop wating")

    p_evt.clear()

    #print("producer sending pivot")
    p_evt.append(Event())
    #print(p_evt.__str__())
    out_q.put(([pivot], p_evt[0]))

    #print("producer start wating")
    p_evt[0].wait()
    #print("producer Stop wating")

    #print("Working on right side")
    rightSide = [x for x in lyst if x > pivot]

    pack = int(len(rightSide)/num_of_threads)
    index_wait = 0
    p_evt.clear()
    my_chunks = chunks(rightSide, pack)
    for i in my_chunks:
        p_evt.append(Event())
        out_q.put((i, p_evt[index_wait]))
        index_wait += 1

    #print("producer start wating")
    for i in range(index_wait):
        p_evt[i].wait()
    #print("producer Stop wating")

    global q_run
    print("Stop all threads",q_run.get())
    for t in range(len(thread_list)):
        if (thread_list[t].isAlive()):
            print(thread_list[t].getName())
            #time.sleep(0.5)
        else:
            thread_list[t].join()
    final_results.sort()
    return


def consumer(in_q,lock):
    global q_run
    while True:
        while not q_run.empty():
            # Get some data
            if not in_q.empty():
                data, p_evt = in_q.get()
                if len(data) == 0:
                    p_evt.set()
                # Process the data
                #print("consumer {0} got list: {1}".format(threading.get_ident().__str__(),data))
                lock.acquire()
                final_results.extend(quicksort(data))
                lock.release()
                p_evt.set()

        if(q_run.empty()):
            print("consumer {0} BREAKING".format(threading.get_ident().__str__()))
            break

def quicksort(lyst):

    if len(lyst) <= 1:
        return lyst
    pivot = lyst.pop(random.randint(0, len(lyst) - 1))
    return quicksort([x for x in lyst if x < pivot]) + [pivot] + quicksort([x for x in lyst if x >= pivot])

array = []



array = random.sample(range(1000000), 1000000)
print("process num:",multiprocessing.cpu_count())
for num_of_threads in range(1,(multiprocessing.cpu_count()*2)):
    q = Queue()
    q_run = Queue()
    q_run.put(1)
    thread_list=[]

    for t in range(num_of_threads):
        thread = Thread(target=consumer, args=(q,lock))
        thread_list.append(thread)
        thread.start()

    start = time.time()#start time
    producer(q,array,len(thread_list),lock)
    elapsed = time.time() - start   #stop time
    print('num_of_threads: {0} Sequential quicksort: {1} sec'.format (num_of_threads,elapsed))

    if isSorted(final_results):
        print("Done!")
    kill_thread = True
    for t in range(len(thread_list)):
        thread_list[t].join()

start = time.time()             #start time
lyst = quicksort(array)          #quicksort the list
elapsed = time.time() - start   #stop time
if not isSorted(lyst):
    print('quicksort did not sort the lyst. oops.')

print('Sequential quicksort: %f sec' % (elapsed))
