import config
from merge_sort_threads import MergeSortThreads
from quick_sort_threads import QuickSortThreads
from pandas_graph import PandasGraph


if __name__ == '__main__':

    merge_sort = MergeSortThreads()
    merge_sort.run()

    quick_sort = QuickSortThreads()
    quick_sort.run()

    #raph_results = PandasGraph
    #graph_results.run()


