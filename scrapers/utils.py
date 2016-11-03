import multiprocessing

# call processFunc on every member of the dataArray using a thread pool
def executeInThreadPool(processFunc, dataArray, poolSize=4):
    pool = multiprocessing.Pool(poolSize)
    results = pool.map(processFunc, dataArray)
    pool.close()
    pool.join()
    return results
