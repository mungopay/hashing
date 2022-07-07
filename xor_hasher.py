from queue import Queue
from threading import Thread
import hashlib

def sha256(input):
   return hashlib.sha256(input.encode('utf-8')).hexdigest()

def xor(input1, input2):
   return ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(input1,input2))


class XorWorker:

   def __init__(self, queue):
      self.__result = ""
      self.__thread = Thread(target=self.__add_to_hash, args=(queue,))
      self.__thread.setDaemon(True)
      self.__thread.start()

   def __add_to_hash(self, queue):
      while True:
         id = queue.get()
         queue.task_done()
         hashed_id = sha256(id)
         if self.__result == "":
            self.__result = hashed_id
            continue
         self.__result = xor(self.__result, hashed_id)

   def get_result(self):
      return self.__result


class XorHasher:

   def __init__(self, num_threads, buffer_size):
      self.__queue = Queue(maxsize=buffer_size)
      self.__workers = []
      for i in range(num_threads):
         self.__workers.append(XorWorker(self.__queue))
      self.__is_finalised = False


   def add_id(self, id):
      if not self.__is_finalised:
         self.__queue.put(id)

   def finalise(self):
      self.__queue.join()
      self.__is_finalised = True

   def get_hash(self):
      result = ""
      for worker in self.__workers:
         worker_result = worker.get_result()
         if worker_result != "":
            if result == "":
               result = worker_result
               continue

            result = xor(result, worker_result)
      return sha256(result)


if __name__ == "__main__":
   xor_hasher = XorHasher(10, 1000)
   for word in [ "I'm", "a", "little", "teapot"]:
      xor_hasher.add_id(word)
   xor_hasher.finalise()
   print(xor_hasher.get_hash())