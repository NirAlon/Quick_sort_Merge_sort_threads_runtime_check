import threading
from queue import Queue
import random, time
from threading import Thread, Event

final_results = []

# A thread that produces data
def producer(out_q, lyst, num_of_threads):
#while True:
        p_evt = Event()
        # Produce some data
        pivot = lyst.pop(random.randint(0, len(lyst) - 1))
        pivot = 7
        print("pivot: {0}".format(pivot))
        leftSide = [x for x in lyst if x < pivot]

        rng =int(len(leftSide)/ int(num_of_threads))


        modulo2 = len(leftSide) % rng
        # nir the king
        # nir the king 2
        extra_loop = 0
        if modulo2 is not 0:
            extra_loop = 1

        modulo = len(leftSide)%num_of_threads
        print(modulo)
        for i in range(int(num_of_threads)):
            if(modulo==0):
                out_q.put((leftSide[i*rng:(i+1)*rng], p_evt))
            else:
                out_q.put((leftSide[i * modulo:(i + 1) * modulo], p_evt))

        print("producer start wating")
        p_evt.wait()
        print("producer Stop wating")

        #out_q.put((final_results,p_evt))
        #p_evt.wait()
        print("Left side after sort"+final_results.__str__())
        print("producer sending pivot")
        out_q.put(([pivot], p_evt))
        p_evt.wait()
        print("Working on right side")
        rightSide = [x for x in lyst if x > pivot]

        rng =int(len(rightSide)/ int(num_of_threads / 2)) #missing the last if it's not even

        for i in range(int(num_of_threads / 2)):
            out_q.put((rightSide[i*rng:(i+1)*rng], p_evt))

        print("producer sending right list: {0} p_event: {1}".format(rightSide,p_evt))
        out_q.put((rightSide, p_evt))
        print("producer start wating")

        p_evt.wait()
        print("producer stop wating")


        print(final_results.__str__())
            # A thread that consumes data


def consumer(in_q):
    while True:
        # Get some data
        data, p_evt = in_q.get()
        # Process the data
        print("consumer {0} got list: {1}".format(threading.get_ident().__str__(),data))
        final_results.extend(quicksort(data))
        p_evt.set()

def quicksort(lyst):

    if len(lyst) <= 1:
        return lyst
    pivot = lyst.pop(random.randint(0, len(lyst) - 1))
    return quicksort([x for x in lyst if x < pivot]) + [pivot] + quicksort([x for x in lyst if x >= pivot])

array = [3,12,2,8,9,4,5,1,6,7,10,11]
q = Queue()
thread_list=[]
for t in range(4):
    thread = Thread(target=consumer, args=(q,))
    thread_list.append(thread)
    thread.start()

producer(q,array,len(thread_list))
