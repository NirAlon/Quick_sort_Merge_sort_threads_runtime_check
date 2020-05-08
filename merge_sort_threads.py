import threading
from queue import Queue
import random
import time
from threading import Thread, Event, Lock

kill_thread = False
final_results = []
lock = Lock()
left = []


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


# The Producer thread is responsible for putting items into the queue if it is not full
def producer(out_q, array, num_of_threads, lock):

    # array of events?
    p_evt = []

    # divide the array into chunks of size step.
    step = int(len(array) / num_of_threads)
    index_wait = 0
    for n in range(num_of_threads):
        if n < num_of_threads - 1:
            chunk = array[n * step:(n + 1) * step]
        else:
            # Get the remaining elements in the list
            chunk = array[n * step:]
        p_evt.append(Event())
        out_q.put(chunk, p_evt[index_wait])
        index_wait += 1

    print("producer start waiting")
    for i in range(index_wait):
        p_evt[i].wait()
    print("producer Stop waiting")

    p_evt.clear()

    print("Left side after sort"+final_results.__str__())

    print("producer start waiting")
    p_evt[0].wait()
    print("producer Stop waiting")
    print("Pivot after sort" + final_results.__str__())

    for t in range(len(thread_list)):
        if thread_list[t].isAlive():
            print(thread_list[t].getName())
            kill_thread = True
            time.sleep(0.5)
        else:
            thread_list[t].join()
    return


# the Consumer thread consumes items if there are any.
def consumer(in_q, lock):
    while True:

        if kill_thread:
            break
        while q.empty():
            time.sleep(0.01)
        # Get some data
        data, p_evt = in_q.get()
        time.sleep(1)
        if len(data) == 0:
            p_evt.set()
            #return

        # Process the data
        print("consumer {0} got list: {1}".format(threading.get_ident().__str__(), data))
        lock.acquire()
        final_results.extend(quicksort(data))
        lock.release()
        p_evt.set()

        #if(q.empty()):
            #print("consumer {0} BREAKING".format(threading.get_ident().__str__()))
            #return


# result (queue) = results until now from the process pool.
# array = chunk of size step from main array.
# every time doing merge to a single chunk
def merge_sort_multiple(results, array):
    results.append(merge_sort(array))


# merge all chunks from result queue
# starting with the first two
# after, the result with the third
# and so on until reaching one large sorted array.
def merge_multiple(results, array_part_left, array_part_right):
    results.append(merge(array_part_left, array_part_right))


# split the list into half (mid index) until getting to size one.
# finally, calling the merge algo recursively.
def merge_sort(array):
    array_length = len(array)

    if array_length <= 1:
        return array

    middle_index = int(array_length / 2)
    left = array[0:middle_index]
    right = array[middle_index:]
    left = merge_sort(left)
    right = merge_sort(right)
    return merge(left, right)


# merge sort algorithm
def merge(left, right):
    sorted_list = []
    # We create shallow copies so that we do not mutate
    # the original objects.
    left = left[:]
    right = right[:]
    # We do not have to actually inspect the length,
    # as empty lists truth value evaluates to False.
    # This is for algorithm demonstration purposes.
    while len(left) > 0 or len(right) > 0:
        if len(left) > 0 and len(right) > 0:
            if left[0] <= right[0]:
                sorted_list.append(left.pop(0))
            else:
                sorted_list.append(right.pop(0))
        elif len(left) > 0:
            sorted_list.append(left.pop(0))
        elif len(right) > 0:
            sorted_list.append(right.pop(0))
    return sorted_list


if __name__ == '__main__':

    array = []

    array = random.sample(range(100), 100)
    q = Queue()
    thread_list = []

    for t in range(4):
        thread = Thread(target=consumer, args=(q, lock))
        thread_list.append(thread)
        thread.start()

    producer(q, array, len(thread_list), lock)

    print(final_results.__str__())
    kill_thread = True
    for t in range(len(thread_list)):
        thread_list[t].join()
