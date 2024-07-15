import sys
import inspect
import heapq, random
from collections import deque

"""
 Data structures useful for implementing SearchAgents
"""
# TODO modify the priority queue function as per the latest doc strings to add all the required functionalities.

class Stack(deque):
    "A container with a last-in-first-out (LIFO) queuing policy."
    def __init__(self):
        self.stack = deque([])

    def push(self ,item):
        "Push 'item' onto the stack. In this case appends to the right"
        self.stack.append(item)

    def isEmpty(self):
        "Returns true if the stack is empty"
        return len(self.list) == 0


class Queue(deque):
    "A container with a first-in-first-out (FIFO) queuing policy."

    def __init__(self):
        self.queue = deque([])

    def push(self, item):
        "Enqueue the 'item' into the queue"
        self.queue.append(item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue. Overwrites the standard pop function of the deque object to enforce
          FIFO.
        """
        return self.queue.popleft()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0

class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.

      Note that this PriorityQueue does not allow you to change the priority
      of an item.  However, you may insert the same item multiple times with
      different priorities.
    """

    def __init__(self):
        self.heap = []

    def push(self, item, priority):
        pair = (priority, item)
        heapq.heappush(self.heap, pair)

    def pop(self):
        (priority, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0


def raiseNotDefined():
  print (f"Method not implemented: {inspect.stack()[1][3]}")
  sys.exit(1)

def flipCoin(p) :
    """ p is the beas of the coin in favor of True"""
    r = random.random()
    return r < p

def pause():
  """
  Pauses the output stream awaiting user feedback.
  """
  print("<Press enter/return to continue>")
  input()