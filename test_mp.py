import multiprocessing
import sys

def worker(x):
    return x * x

def main():
    multiprocessing.freeze_support()
    print(f"CPUs: {multiprocessing.cpu_count()}")
    with multiprocessing.Pool(2) as p:
        print(p.map(worker, [1, 2, 3]))

if __name__ == '__main__':
    main()
