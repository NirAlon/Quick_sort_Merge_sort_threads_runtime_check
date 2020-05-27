from queue import Queue
import random, time
from threading import Thread, Event, Lock
import multiprocessing
from animal import Animal  # error for no reason. import working.
import config


class QuickSortThreads:

    lock = Lock()
    final_results = []  # final sorted list
    main_q = Queue()  # communicate between producer and consumer
    q_run = Queue()  # Flag for the while consumer is running.
    thread_list = []

    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

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

    def producer(self, out_q, lyst, num_of_threads):

        p_evt = []

        # Pick a random pivot
        # Making a list of the smaller then pivot
        # Dividing the list in num of threads (pack)
        # dividing the list to chunks by pack
        # every thread gets list(chunk) and event

        pivot = lyst[random.randint(0, len(lyst) - 1)]
        if config.SORT_ORDER is 'a':
            left_side = [x for x in lyst if x < pivot]
        elif config.SORT_ORDER is 'd':
            left_side = [x for x in lyst if x > pivot]
        pack = int(len(left_side)/num_of_threads)

        index_wait = 0
        if pack == 0:
            pack = 1
        my_chunks = self.chunks(left_side, pack)
        for i in my_chunks:
            p_evt.append(Event())
            out_q.put((i, p_evt[index_wait]))
            index_wait += 1

        # waiting for thread to finish the job
        for i in range(index_wait):
            p_evt[i].wait()

        p_evt.clear()
        p_evt.append(Event())
        out_q.put(([pivot], p_evt[0]))  # Adding the Pivot to the final result

        p_evt[0].wait()

        # Making a list of the bigger then pivot
        # Dividing the list in num of threads (pack)
        # dividing the list to chunks by pack
        # every thread gets list(chunk) and event
        if config.SORT_ORDER is 'a':
            right_side = [x for x in lyst if x >= pivot]
        elif config.SORT_ORDER is 'd':
            right_side = [x for x in lyst if x <= pivot]
        pack = int(len(right_side)/num_of_threads)
        index_wait = 0
        p_evt.clear()
        if pack == 0:
            pack = 1
        my_chunks = self.chunks(right_side, pack)
        for i in my_chunks:
            p_evt.append(Event())
            out_q.put((i, p_evt[index_wait]))
            index_wait += 1

        # waiting for thread to finish the job
        for i in range(index_wait):
            p_evt[i].wait()

        # global q_run
        if config.SORT_ORDER is 'a':
            self.final_results.sort()  # Sort final result after all the chunks are sorted in the list
        elif config.SORT_ORDER is 'd':
            self.final_results.sort(reverse=True)  # Sort final result after all the chunks are sorted in the list
        return

    def consumer(self, in_q, lock):
        # global q_run

        while not self.q_run.empty():  # Thread is running until the queue is empty

            if not in_q.empty():
                data, p_evt = in_q.get()
                if data == -1:  # In case the job is done but this thread is still waiting for data on queue
                    break
                if len(data) == 0:  # in case that the list is empty
                    p_evt.set()  # Thread signaling to the producer that is done and waiting for another chunk
                # Process the data
                lock.acquire()  # Thread acquire to edit the list, if it's already acquired the current thread will wait.
                self.final_results.extend(self.quicksort(data))  # Adding the sort chunk to the list

                lock.release()  # Thread release the lock
                p_evt.set()  # Thread signaling to the producer that is done and waiting for another chunk

            if self.q_run.empty():
                # if the flag is raised and the queue is empty the threads is break out
                break

    def quicksort(self, lyst):

        if len(lyst) <= 1:
            return lyst
        pivot = lyst[random.randint(0, len(lyst) - 1)]
        if config.SORT_ORDER is 'a':
            return self.quicksort([x for x in lyst if x < pivot]) + [pivot] + self.quicksort([x for x in lyst if x >= pivot])
        elif config.SORT_ORDER is 'd':
            return self.quicksort([x for x in lyst if x > pivot]) + [pivot] + self.quicksort([x for x in lyst if x <= pivot])

    def run(self):

        all_animals = self.create_animal_array()  # random array list of object animal

        file = open('quicksort', 'w')

        # check Sequential time of sort
        start_sequential = time.time()
        sequential_animal_array = self.quicksort(all_animals)
        if self.is_sorted(sequential_animal_array) is not True:
            print("array not sorted")
            return None

        elapsed_sequential = time.time() - start_sequential
        file.write("0 {0}\n".format(elapsed_sequential))

        for num_of_threads in range(1, (multiprocessing.cpu_count()*2) + 1):  #  Program is running between 1 to num of processors * 2
            self.final_results = []  # final sorted list
            self.main_q = Queue()  # communicate between producer and consumer
            self.q_run = Queue()  # Flag for the while consumer is running.
            self.q_run.put(1)  # while this queue is not empty the consumer will still running
            self.thread_list = []  # list of threads.
            for _ in range(num_of_threads):
                thread = Thread(target=self.consumer, args=(self.main_q, self.lock))  # Every thread is running on the consumer program
                self.thread_list.append(thread)
                thread.start()

            start_parallel = time.time()
            self.producer(self.main_q, all_animals, len(self.thread_list))  # supervise the jobs
            elapsed_parallel = time.time() - start_parallel

            file.write("{0} {1} \n".format(num_of_threads,elapsed_parallel))

            for t in self.thread_list:  # Running on the thread list and checking who is still alive
                while t.isAlive():  # if the current thread is alive, probably it's because he's still waiting on queue
                    self.main_q.put((-1, None))  # Sending -1 to the thread queue to release the thread

            joined = 0
            for t in self.thread_list:
                t.join()  # closing the threads
                joined += 1

            if self.is_sorted(sequential_animal_array) is not True:
                print("array not sorted")
                return None
        file.close()
        return self.final_results
