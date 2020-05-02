import threading
from queue import Queue
import random, time
from threading import Thread, Event, Lock

final_results = []
lock = Lock()
# A thread that produces data
def producer(out_q, lyst, num_of_threads):

    p_evt = Event()
    pivot = lyst.pop(random.randint(0, len(lyst) - 1))
    pivot = 1
    print("pivot: {0}".format(pivot))
    leftSide = [x for x in lyst if x < pivot]

    out_q.put((leftSide, p_evt))

    print("producer start wating")
    p_evt.wait()
    print("producer Stop wating")

    print("Left side after sort"+final_results.__str__())
    print("producer sending pivot")
    out_q.put(([pivot], p_evt))

    print("producer start wating")
    p_evt.wait()
    print("producer Stop wating")
    print("Pivot after sort" + final_results.__str__())

    print("Working on right side")
    rightSide = [x for x in lyst if x > pivot]

    out_q.put((rightSide, p_evt))

    print("producer start wating")
    p_evt.wait()
    print("producer stop wating")

    print("right side after sort" + final_results.__str__())

    #for _ in range(num_of_threads):
    out_q.task_done()


def consumer(in_q):
    while True:
        # Get some data
        data, p_evt = in_q.get()
        if len(data) == 0 :
            p_evt.set()
            break
        # Process the data
        print("consumer {0} got list: {1}".format(threading.get_ident().__str__(),data))
        lock.acquire()
        final_results.extend(quicksort(data))
        lock.release()
        p_evt.set()

        if(q.empty()):
            print("consumer {0} BREAKING".format(threading.get_ident().__str__()))
            break

def quicksort(lyst):

    if len(lyst) <= 1:
        return lyst
    pivot = lyst.pop(random.randint(0, len(lyst) - 1))
    return quicksort([x for x in lyst if x < pivot]) + [pivot] + quicksort([x for x in lyst if x >= pivot])


array = [3,12,2,8,9,4,5,1,6,7,10,11]
q = Queue()
thread_list=[]
for t in range(2):
    thread = Thread(target=consumer, args=(q,))
    thread_list.append(thread)
    thread.start()

producer(q,array,len(thread_list))
for t in range(len(thread_list)):
    thread_list[t].join()
print(final_results.__str__())

