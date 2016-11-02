import multiprocessing.dummy

# call processFunc on every member of the dataArray using a thread pool
def executeInThreadPool(processFunc, dataArray, poolSize=4):
    pool = multiprocessing.dummy.Pool(poolSize)
    pool.map(processFunc, dataArray)
    pool.close()
    pool.join()
