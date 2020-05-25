import config
from merge_sort_threads import MergeSortThreads
from quick_sort_threads import QuickSortThreads
from pandas_graph import PandasGraph
import multiprocessing

def copy_from_file(from_file,f1):
    with open(from_file) as f:
            for line in f:
                f1.write(line)
    f.close()

def sample_of_animals():
    from random import randint
    a_set = set()
    while True:
        a_set.add(randint(0, config.ARRAY_LENGTH))
        if len(a_set) == 10:
            break
    lst = sorted(list(a_set))

    for i in lst:
        yield i


if __name__ == '__main__':
    print("Start Program...")
    file_prompt = open('prompt', 'w')
    file_prompt.write(
        "Animal Array Size: {0}\nSort Order: {1}\nList Priority: {2}\nCPU NUMBER: {3}\n"
        .format(config.ARRAY_LENGTH, config.SORT_ORDER,config.list, multiprocessing.cpu_count()))
    file_prompt.write("\nMergeSort:\n")
    merge_sort = MergeSortThreads()
    final_list=merge_sort.run()
    copy_from_file("mergesort",file_prompt)

    for i in sample_of_animals():
        file_prompt.write(final_list[i].__str__()+"\n")
    file_prompt.write("\nQuickSort:\n")
    quick_sort = QuickSortThreads()
    final_list=quick_sort.run()
    copy_from_file("quicksort", file_prompt)
    for i in sample_of_animals():
        file_prompt.write(final_list[i].__str__() + "\n")
    file_prompt.close()
    print("Finish Program...\nPresenting Results")
    graph_results = PandasGraph()
    graph_results.run()



