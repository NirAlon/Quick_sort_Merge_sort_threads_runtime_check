from queue import Queue
import random
import time
from threading import Thread, Event, Lock
import multiprocessing
from animal import Animal
import config


class MergeSortThreads:
    lock = Lock()
    final_q = Queue()
    final_sorted_result = []
    main_q = Queue()  # communicate between producer and consumer
    q_run = Queue()  # Flag for the while consumer is running.
    # q_run.put(1)  # while this queue is not empty the consumer will still running
    thread_list = []

    def is_sorted(self, lyst):
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

    def create_animal_array(self):
        animals = []
        # length = random.randint(3 * 10 ** 4, 3 * 10 ** 5)  # Randomize the length of our list between 3000 to 30000
        for _ in range(config.ARRAY_LENGTH):
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
    def merge_sort_multiple(self, results, array):
        results.put(self.merge_sort(array))

    # merge all chunks from result queue
    # starting with the first two
    # after, the result with the third
    # and so on until reaching one large sorted array.
    def merge_multiple(self, results, array_part_left, array_part_right):
        results.put(self.merge(array_part_left, array_part_right))

    # split the list into half (mid index) until getting to size one.
    # finally, calling the merge algo recursively.
    def merge_sort(self, array):
        array_length = len(array)

        if array_length <= 1:
            return array

        middle_index = int(array_length / 2)
        left = array[0:middle_index]
        right = array[middle_index:]
        left = self.merge_sort(left)
        right = self.merge_sort(right)
        return self.merge(left, right)

    # merge sort algorithm
    def merge(self, left, right):
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
                if config.SORT_ORDER is 'a':
                    if left[0] <= right[0]:
                        sorted_list.append(left.pop(0))
                    else:
                        sorted_list.append(right.pop(0))
                elif config.SORT_ORDER is 'd':
                    if left[0] >= right[0]:
                        sorted_list.append(left.pop(0))
                    else:
                        sorted_list.append(right.pop(0))
                else:
                    raise Exception("You must enter 'a' for ascending and 'd' for descending!")
            elif len(left) > 0:
                sorted_list.append(left.pop(0))
            elif len(right) > 0:
                sorted_list.append(right.pop(0))
        return sorted_list

    # The Producer thread is responsible for putting items into the queue if it is not full
    def producer(self, out_q, array, num_of_threads):

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

        # global q_run
        #print("Stop all threads", self.q_run.get())  # Raising flag to consumer to break the while loop
        return

    # the Consumer thread consumes items if there are any.
    def consumer(self, in_q):  # removed lock parameter, using lock from above
        # global q_run

        while not self.q_run.empty():  # Thread is running until the queue is empty

            if not in_q.empty():
                data, p_evt = in_q.get()
                if data == -1:  # In case the job is done but this thread is still waiting for data on queue
                    #print("-1 Break")
                    break
                if len(data) == 0:  # in case that the list is empty
                    p_evt.set()  # Thread signaling to the producer that is done and waiting for another chunk
                # Process the data
                self.lock.acquire()  # Thread acquire to edit the list, if it's already acquired the current thread will wait.
                self.merge_sort_multiple(self.final_q, data)  # merge sort the data into final queue
                self.lock.release()  # Thread release the lock
                p_evt.set()  # Thread signaling to the producer that is done and waiting for another chunk

            if self.q_run.empty():
                # if the flag is raised and the queue is empty the threads is break out
                break

    def run(self):

        global final_sorted_result
        all_animals = self.create_animal_array()
        file = open('mergesort', 'w')
        # check Sequential time of sort
        #print('Start sequential:')
        start_sequential = time.time()
        sequential_array = self.merge_sort(all_animals)
        if self.is_sorted(sequential_array) is not True:
            print("array not sorted :(")
            return None

        elapsed_sequential = time.time() - start_sequential

        file.write("0 {0}\n".format(elapsed_sequential))

        for num_of_threads in range(1, (multiprocessing.cpu_count() * 2)+1):
            self.final_sorted_result = []
            self.main_q = Queue()  # communicate between producer and consumer
            self.q_run = Queue()  # Flag for the while consumer is running.
            self.q_run.put(1)  # while this queue is not empty the consumer will still running
            self.thread_list = []

            for _ in range(num_of_threads):
                thread = Thread(target=self.consumer, args=(self.main_q,))  # Every thread is running on the consumer program
                self.thread_list.append(thread)
                thread.start()

            start_parallel = time.time()
            self.producer(self.main_q, all_animals, len(self.thread_list))  # supervise the jobs
            elapsed_parallel = time.time() - start_parallel
            if self.is_sorted(self.final_sorted_result) is not True:
                print("array not sorted :(")
                return None
            file.write("{0} {1} \n".format(num_of_threads,elapsed_parallel))


            # merge sub-lists
            while self.final_q.qsize() > 1:
                self.merge_multiple(self.final_q, self.final_q.get(), self.final_q.get())
            final_sorted_result = self.final_q.get()



            for t in self.thread_list:  # Running on the thread list and checking who is still alive
                while t.isAlive():  # if the current thread is alive, probably it's because he's still waiting on queue
                    self.main_q.put((-1, None))  # Sending -1 to the thread queue to release the thread

            joined = 0
            for t in self.thread_list:
                t.join()  # closing the threads
                joined += 1
        file.close()
        return final_sorted_result
