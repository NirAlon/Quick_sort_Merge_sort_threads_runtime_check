from queue import Queue
import random
import time
from threading import Thread, Event, Lock
import multiprocessing
from animal import Animal
import config

lock = Lock()
final_q = Queue()


def is_sorted(lyst):
    """
    Return whether the argument lyst is in non-decreasing order.
    """

    # d for descending  יורד
    if config.SORT_ORDER is 'd':
        for i in range(1, len(lyst)):
            if lyst[i] > lyst[i - 1]:
                return False
        return True

    # a for ascending  עולה
    if config.SORT_ORDER is 'a':
        for i in range(1, len(lyst)):
            if lyst[i] < lyst[i - 1]:
                return False
        return True


def create_animal_array():
    animals = []
    length = random.randint(3 * 10 ** 4, 3 * 10 ** 5)  # Randomize the length of our list between 3000 to 30000
    for _ in range(100000):
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

    # waiting for thread to finish the job
    for i in range(index_wait):
        p_evt[i].wait()

    global q_run
    print("Stop all threads", q_run.get())  # Raising flag to consumer to break the while loop
    return


# the Consumer thread consumes items if there are any.
def consumer(in_q):  # removed lock parameter, using lock from above
    global q_run

    while not q_run.empty():  # Thread is running until the queue is empty

        if not in_q.empty():
            data, p_evt = in_q.get()
            if data == -1:  # In case the job is done but this thread is still waiting for data on queue
                print("-1 Break")
                break
            if len(data) == 0:  # in case that the list is empty
                p_evt.set()  # Thread signaling to the producer that is done and waiting for another chunk
            # Process the data
            lock.acquire()  # Thread acquire to edit the list, if it's already acquired the current thread will wait.
            merge_sort_multiple(final_q, data)  # merge sort the data into final queue
            lock.release()  # Thread release the lock
            p_evt.set()  # Thread signaling to the producer that is done and waiting for another chunk

        if q_run.empty():
            # if the flag is raised and the queue is empty the threads is break out
            break


if __name__ == '__main__':

    all_animals = create_animal_array()
    file = open('margesort', 'w')

    # check Sequential time of sort
    print('Start sequential:')
    start_sequential = time.time()
    sequential_array = merge_sort(all_animals)
    if is_sorted(sequential_array):
        print("this is the sorted array!:")
        # print(all_animals)
    else:
        print("array not sorted :(")

    elapsed_sequential = time.time() - start_sequential
    print('sequential merge: {}'.format(elapsed_sequential))

    file.write("0 {0}\n".format(elapsed_sequential))

    print("@@@ Computer Process num: {} @@@".format(multiprocessing.cpu_count()))
    for num_of_threads in range(1, (multiprocessing.cpu_count() * 2)+1):
        print('\n$$$$$$$$$$$$$$$$$$$$ Num of threads {} $$$$$$$$$$$$$$$$$$$$'.format(num_of_threads))
        final_sorted_result = []
        main_q = Queue()  # communicate between producer and consumer
        q_run = Queue()  # Flag for the while consumer is running.
        q_run.put(1)  # while this queue is not empty the consumer will still running
        thread_list = []

        for t in range(num_of_threads):
            thread = Thread(target=consumer, args=(main_q,))  # Every thread is running on the consumer program
            thread_list.append(thread)
            thread.start()

        print('start parallel:')
        start_parallel = time.time()
        producer(main_q, all_animals, len(thread_list))  # supervise the jobs
        elapsed_parallel = time.time() - start_parallel
        print('parallel merge: {} sec'.format(elapsed_parallel))
        file.write("{0} {1} \n".format(num_of_threads,elapsed_parallel))

        if elapsed_sequential > elapsed_parallel:
            print('Parallel won!!! :)')
        else:
            print('Sequential won :(')

        # merge sub-lists
        while final_q.qsize() > 1:
            merge_multiple(final_q, final_q.get(), final_q.get())
        final_sorted_result = final_q.get()

        if is_sorted(final_sorted_result):
            time.sleep(2)
            print("this is the sorted array!:")
            # print(final_sorted_result)
        else:
            print("array not sorted :(")

        for t in range(len(thread_list)):  # Running on the thread list and checking who is still alive
            while thread_list[t].isAlive():  # if the current thread is alive, probably it's because he's still waiting on queue
                main_q.put((-1, None))  # Sending -1 to the thread queue to release the thread

        joined = 0
        for t in range(len(thread_list)):
            thread_list[t].join()  # closing the threads
            joined += 1
        print("Num of joined", joined)  # Making sure that all the active threads are joined.
    file.close()
