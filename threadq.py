from queue import Queue
import random, time
from threading import Thread, Event, Lock
import multiprocessing
from animal import Animal


final_results = []
lock = Lock()

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

def create_animal_array():
    animals = []
    length = random.randint(3 * 10 ** 4, 3 * 10 ** 5)  # Randomize the length of our list
    for _ in range(300000):
        height = random.randint(10, 4000)
        weight = random.randint(2, 600)
        age = random.randint(1, 200)
        num_of_legs = random.randint(0, 10)
        if random.randint(0, 1) is 0:
            tail = False
        else:
            tail = True
        animals.append(Animal(height, weight, age, num_of_legs, tail))
    return animals

def producer(out_q, lyst, num_of_threads,lock):

    p_evt = []

    ### Pick a rendome pivot
    ### Making a list of the smaller then pivot
    ### Dividing the list in num of threads (pack)
    ### dividing the list to chunks by pack
    ### every thread gets list(chunk) and event

    pivot = lyst.pop(random.randint(0, len(lyst) - 1))
    leftSide = [x for x in lyst if x < pivot]
    pack = int(len(leftSide)/num_of_threads)



    index_wait = 0
    if pack == 0:
        pack=1;
    my_chunks = chunks(leftSide, pack)
    for i in my_chunks:
        p_evt.append(Event())
        out_q.put((i, p_evt[index_wait]))
        index_wait+=1

    # waiting for thread to finish the job
    for i in range(index_wait):
        p_evt[i].wait()

    p_evt.clear()
    p_evt.append(Event())
    out_q.put(([pivot], p_evt[0])) #Adding the Pivot to the final result

    p_evt[0].wait()

    ### Making a list of the bigger then pivot
    ### Dividing the list in num of threads (pack)
    ### dividing the list to chunks by pack
    ### every thread gets list(chunk) and event

    rightSide = [x for x in lyst if x > pivot]
    pack = int(len(rightSide)/num_of_threads)
    index_wait = 0
    p_evt.clear()
    if pack == 0:
        pack=1;
    my_chunks = chunks(rightSide, pack)
    for i in my_chunks:
        p_evt.append(Event())
        out_q.put((i, p_evt[index_wait]))
        index_wait += 1

    # waiting for thread to finish the job
    for i in range(index_wait):
        p_evt[i].wait()

    global q_run
    print("Stop all threads",q_run.get()) # Raising flag to consumer to break the while loop
    final_results.sort() # Sort final result after all the chunks are sorted in the list
    return


def consumer(in_q,lock):
    global q_run

    while not q_run.empty(): # Thread is running until the queue is empty

        if not in_q.empty():
            data, p_evt = in_q.get()
            if data == -1: # In case the job is done but this thread is still wating for data on queue
                print("-1 Break")
                break
            if len(data) == 0: #in case that the list is empty
                p_evt.set() # Thread signaling to the producer that is done and waiting for another chunk
            # Process the data
            #print("consumer {0} got list: {1}".format(threading.get_ident().__str__(),data))
            lock.acquire() # Thread acquire to edit the list, if it's already acquired the current thread will wait.
            final_results.extend(quicksort(data)) # Adding the sort chunk to the list

            lock.release() # Thead realease the lock
            p_evt.set() # Thread signaling to the producer that is done and waiting for another chunk

        if(q_run.empty()):
            # if the flag is raised and the queue is empty the threads is break out
            break

def quicksort(lyst):

    if len(lyst) <= 1:
        return lyst
    pivot = lyst.pop(random.randint(0, len(lyst) - 1))
    return quicksort([x for x in lyst if x < pivot]) + [pivot] + quicksort([x for x in lyst if x >= pivot])



print("process num:",multiprocessing.cpu_count())

for num_of_threads in range(1,(multiprocessing.cpu_count()*2)): # Program is running between 1 to num of processors * 2
    array = create_animal_array() # random array list
    final_results=[] #final sorted list
    #array = random.sample(range(5000), 5000) # random numbers
    #print("array", array)
    q = Queue() # communicate between producer and consumer
    q_run = Queue() # Flag for the while consumer is running.
    q_run.put(1) # while this queue is not empty the consumer will still running
    thread_list=[] # list of threads.
    
    for t in range(num_of_threads): # Loop of
        thread = Thread(target=consumer, args=(q,lock)) # Every thread is running on the consumer program
        thread_list.append(thread)
        thread.start()

    start = time.time()#start time
    producer(q,array,len(thread_list),lock) # supervise the job
    elapsed = time.time() - start   #stop time
    print('num_of_threads: {0} threads quicksort: {1} sec'.format (num_of_threads,elapsed))

    if isSorted(final_results): #Cheacking that the final list sorted
        print("Done! len:{}".format(len(final_results)))
        #print(final_results)

    for t in range(len(thread_list)): #Running on the thread list and cheacking who is still alive
        while thread_list[t].isAlive(): # if the current thread is alive, probbebly it's cuz is still waiting on queue
            q.put((-1,None)) #Sending -1 to the thread queue to realeas the thread

    joined = 0
    for t in range(len(thread_list)):
        thread_list[t].join() #closing the threads
        joined+=1
    print("Num of joined",joined)#Making sure that all the active threads are joined.

start = time.time()             #start time
lyst = quicksort(array)          #quicksort the list
elapsed = time.time() - start   #stop time
if not isSorted(lyst):
    print('quicksort did not sort the lyst. oops.')



print('Sequential quicksort: %f sec' % (elapsed))

start = time.time()  # start time
array.sort()  # quicksort the list
elapsed = time.time() - start  # stop time
if not isSorted(lyst):
    print('quicksort did not sort the lyst. oops.')

print('Sequential quicksort: %f sec' % (elapsed))

