import threading
from queue import Queue
import random
import time
from threading import Thread, Event, Lock

kill_thread = False
lock = Lock()
final_q = Queue()


def is_sorted(lyst):
    """
    Return whether the argument lyst is in non-decreasing order.
    """
    for i in range(1, len(lyst)):
        if lyst[i] < lyst[i - 1]:
            return False
    return True


# result (queue) = results until now from the process pool.
# array = chunk of size step from main array.
# every time doing merge to a single chunk
def merge_sort_multiple(results, array):
    results.put(merge_sort(array))


# merge all chunks from result queue
# starting with the first two
# after, the result with the third
# and so on until reaching one large sorted array.
def merge_multiple(results, array_part_left, array_part_right):
    results.put(merge(array_part_left, array_part_right))


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


# The Producer thread is responsible for putting items into the queue if it is not full
def producer(out_q, array, num_of_threads):

    # array of events
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
        out_q.put((chunk, p_evt[index_wait]))  # tuple of data and event
        index_wait += 1

    print("producer start waiting")
    for i in range(index_wait):
        # blocks until the flag is true
        p_evt[i].wait()
    print("producer Stop waiting")

    # clear event list
    p_evt.clear()

    global q_run
    print("Stop all threads", q_run.get())
    for t in thread_list:
        if t.isAlive():
            print(t.getName())
            # time.sleep(0.5)
        else:
            t.join()


# the Consumer thread consumes items if there are any.
def consumer(in_q, lock):
    global q_run
    while True:
        while not q_run.empty():
            # Get some data
            if not in_q.empty():
                data, p_evt = in_q.get()  # tuple of data and event
                if len(data) == 0:
                    p_evt.set()
                # Process the data
                lock.acquire()
                merge_sort_multiple(final_q, data)  # merge sort the data
                lock.release()
                p_evt.set()

        if q_run.empty():
            print("consumer {0} BREAKING ".format(threading.get_ident().__str__()))
            break


if __name__ == '__main__':

    length = random.randint(3 * 10 ** 4, 3 * 10 ** 5)  # Randomize the length of our list
    # unsorted_array = []
    final_result = []
    num_of_threads = 4
    unsorted_array = [random.randint(0, n * 100) for n in range(length)]  # Create an unsorted list with random numbers
    main_q = Queue()
    q_run = Queue()
    q_run.put(1)
    thread_list = []

    for t in range(num_of_threads):
        thread = Thread(target=consumer, args=(main_q, lock))
        thread_list.append(thread)
        thread.start()

    print('start Sequential:')
    start_sequential = time.time()
    merge_sort(unsorted_array)
    elapsed_sequential = time.time() - start_sequential
    print('sequential merge: {}'.format(elapsed_sequential))

    print('start parallel:')
    start_parallel = time.time()
    producer(main_q, unsorted_array, len(thread_list))
    elapsed_parallel = time.time() - start_parallel  # stop time
    print('num_of_threads: {0} parallel merge: {1} sec'.format(num_of_threads, elapsed_parallel))

    while final_q.qsize() > 1:
        merge_multiple(final_q, final_q.get(), final_q.get())
    final_result = final_q.get()

    if is_sorted(final_result):
        print("this is the sorted array!:")
        print((final_result.__str__()))
    else:
        print("array not sorted :(")

    for t in range(len(thread_list)):
        thread_list[t].join()
