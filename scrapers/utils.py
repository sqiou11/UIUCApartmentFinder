"""
call processFunc on every member of the dataArray using a thread pool
"""
def executeParallel(processFunc, dataArray, poolSize=4):
    import multiprocessing
    pool = multiprocessing.Pool(poolSize)
    results = pool.map(processFunc, dataArray)
    pool.close()
    pool.join()
    return results
