import hashlib
import json
import re
import pymongo
import random
import math
from datetime import datetime

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["blockchain"]
coll_blockcontent = db["blockcontent"]
coll_users = db["users"]


def toBinary(a):
  return str(bin(int('1' + a, 16))[3:])


class Block:
  countblock = coll_blockcontent.estimated_document_count()
  lastblock = coll_blockcontent.find_one({"index": int(countblock) - 1})

  def __init__(self, index=0, timestamp=0, data=None, hash="0", prev_hash="0", difficuity=0, nonce=0):
      self.index = index
      self.timestamp = timestamp
      self.data = data
      self.hash = hash
      self.prev_hash = prev_hash
      self.difficulty = difficuity
      self.nonce = nonce

  def cal_hash(self):
      block_string = json.dumps(self.__dict__, sort_keys=True)
      #print("block_string", block_string)
      returnResult = hashlib.sha256(block_string.encode('utf-8')).hexdigest()
      return returnResult
      # return updatehash(self.index, self.timestamp, self.previous_hash, self.difficulty, self.data, self.nonce)
  ''' def setNonce(self, inputNoce):
    self.nonce = inputNoce
    self.hash = self.Cal_hash()

  def setNonce2(self, inputNoce):
    self.nonce = inputNoce

  def Cal_hash(self):
    saveHash = self.hash
    self.hash = 0
    block_string = json.dumps(self.__dict__, sort_keys=True)
    returnResult = hashlib.sha256(block_string.encode('utf-8')).hexdigest()
    self.hash = returnResult

    return returnResult '''

  def getResult(self):
      return self.__dict__


class Blockchain():
  # the number of zeros in front of each hash
  difficulty = 15

  # restarts a new blockchain or the existing one upon initialization
  def __init__(self):
    self.chain = []

  # add a new block to the chain
  def add(self, block):
    self.chain.append(block)

  # remove a block from the chain
  def remove(self, block):
    self.chain.remove(block)

  BLOCK_GENERATION_INTERVAL = 10  # seconds
  DIFFICULTY_ADJUSTMENT_INTERVAL = 10  # blocks
  # find dynamic difficulty

  def dynamic_difficulty(self):

    total_Time = 0
    ''' updateRes = Chain[len(Chain) - 1].index % DIFFICULTY_ADJUSTMENT_INTERVAL
    if Chain[len(Chain) - 1].index > DIFFICULTY_ADJUSTMENT_INTERVAL:
        if int(updateRes) == 1:
        BlockTimeCount = Chain[len(Chain) - 1].timestamp - Chain[
            len(Chain) - DIFFICULTY_ADJUSTMENT_INTERVAL].timestamp
        global difficulty
        if BlockTimeCount > BLOCK_GENERATION_INTERVAL * 2:
            difficulty = difficulty - 1
            print("\ndifficulty - 1")
        if BlockTimeCount < BLOCK_GENERATION_INTERVAL / 2:
            difficulty = difficulty + 1
            print("\ndifficulty + 1") '''
    for x in range(10):  # 10 block
        try:
            print("self.chain[(-1 * x - 1)].timestamp",
                  self.chain[(-1 * x - 1)].timestamp)
            total_Time += self.chain[(-1 * x - 1)].timestamp
            print("total_Time: ", total_Time)
        except IndexError:
            pass

    try:
        if self.chain[-1].timestamp < 10:
            self.difficulty += 1
        elif self.chain[-1].timestamp > 30:
            self.difficulty -= 1
    except IndexError:
        pass

    #self.difficulty = math.ceil(self.difficulty)
    print("self.difficulty: ", self.difficulty)
    return self.difficulty

    # find the nonce of the block that satisfies the difficulty and add to chain
  def mine(self, block):
    # get the start time
    st = datetime.now().timestamp()
    print("st:",  st)
    # attempt to get the hash of the previous block.
    # this should raise an IndexError if this is the first block.
    countblock = coll_blockcontent.estimated_document_count()
    lastblock = coll_blockcontent.find_one({"index": int(countblock) - 1})
    ''' try:
        #block.previous_hash = self.chain[-1].hash()
        lastblock[""] = 
    except IndexError:
        pass '''

    # loop until nonce that satisifeis difficulty is found
    while True:
      # if block.cal_hash()[:self.difficulty] == "0" * self.difficulty:
      if toBinary(block.cal_hash()).startswith('0' * self.difficulty) == True:
        print("block.cal_hash(): ", block.cal_hash())
        savecal_hash = block.cal_hash()
        # get the end time
        et = datetime.now().timestamp()
        print("et:",  et)
        # get the execution time
        block.timestamp = et - st
        block.difficulty = self.difficulty
        #block.difficulty = self.dynamic_difficulty()
        block.hash = savecal_hash
        self.add(block)
        break
      else:
        # increase the nonce by one and try again
        block.nonce += 1

  # check if blockchain is valid
  def isValid(self):
    # loop through blockchain
    for i in range(1, len(self.chain)):
      _previous = self.chain[i].previous_hash
      _current = self.chain[i - 1].cal_hash()
      # compare the previous hash to the actual hash of the previous block
      if _previous != _current or _current[:self.
                                            difficulty] != "0" * self.difficulty:
          return False

    return True

class User:
  def __init__(self, uid, username, nickname, email, password, image):
    self.uid = uid 
    self.username = username
    self.nickname = nickname
    self.email = email
    self.password = password
    self.image = image

def addfirstblockindb():
    coll_blockcontent.insert_one({
      "index": 0,
      "timestamp": 12.881994009017944,
      "data": ["COMP4913 capstone project"],
      "hash": "000f1e0c9e22a986adcdae80213351adff656556006428c6adbb40e93ed95c24",
      "prev_hash": "0",
      "difficulty": 15,
      "nonce": 4913
    })


if not (coll_blockcontent.count_documents({"index": 0})):
  addfirstblockindb()
  print("first block is added in db")
else:
  countblock = coll_blockcontent.estimated_document_count()
  lastblock = coll_blockcontent.find_one({"index": int(countblock) - 1})
  saveblock = Block(
    lastblock["index"],
    lastblock["timestamp"],
    lastblock["data"],
    lastblock["hash"],
    lastblock["prev_hash"],
    lastblock["difficulty"],
    lastblock["nonce"]
  )


def searchblock(GetNum):
  if GetNum == None:
    try:
      specificblock = coll_blockcontent.find({}, {"_id": 0})
      print("\n------block info in the database----")
      for a in specificblock:
          print(a)
      print("------The last block info of database----\n")
    except:
      print("Not found")
  else:
    try:
      print("start search.......")
      specificblock = coll_blockcontent.find_one({"index": int(GetNum)}, {"_id": 0})
      print(specificblock)
    except:
      print("out of index")

def registeraccount():
  
  username = input("\ninput user name : ")
  print(username)
  db_username = coll_users.find_one({"username": username}, {"_id": 0})
  print(db_username)
  
  pattern = re.compile(r'([\w]+)') #\w = [A-Za-z0-9_]
  
  if username == "":
    print("\nPlease enter a username")
    registeraccount()
  elif not pattern.match(username):
    print("\nUsername can only contain letters, numbers, and underscores")
    registeraccount()
  elif db_username != None:
    if username == db_username["username"]:
      print("\nThis username is already taken")
      registeraccount()
  
  nickname = input("\ninput nickname : ")
  
  if  nickname == "":
    print("\nPlease enter a nickname")
    registeraccount()
      
  email = input("\ninput email : ")
  db_email = coll_users.find_one({"email": email}, {"_id": 0})
  pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
  if email == "":
    print("\nPlease enter a email")
    registeraccount()
  elif  not re.match(pat, email):
    print("\nInvalid email  format")
    registeraccount()
  elif db_email != None:
    if email == db_email["email"]:
      print("\nThis email is already taken")
      registeraccount()
  
  password = input("\ninput password : ")
  if  password == "":
    print("\nPlease enter a password")
    registeraccount()
  elif not pattern.match(password):
    print("\nPassword can only contain letters, numbers, and underscores")
    registeraccount()
  elif len(password) < 5:
    print("\nPassword must have at least 5 characters")
    registeraccount()
    
  countuser = coll_users.estimated_document_count()
  #lastblock = coll_blockcontent.find_one({"index": int(countblock) - 1})
  createuser = User(countuser, username, nickname, email, password, "")
  coll_users.insert_one(createuser.__dict__)
  print("\nCreate account successful")
    
logined = False
def login():
  global logined
  username = input("\ninput user name : ")
  print(username)
  db_username = coll_users.find_one({"username": username}, {"_id": 0})
  print(db_username)
  
  if username == "":
    print("\nPlease enter a username")
    login()
  elif db_username == None:
    print("\nNo account found with that username")
    login()
  else:
    password = input("\ninput password : ")
    if  password == "":
      print("\nPlease enter a password")
      login()
    elif password != db_username["password"]:
      print("\nThe password you entered was not valid")
      login()
    else:
      print("Login successful")
      print("logined be: ", print(logined))
      logined = True
      print("logined af: ", print(logined))
    
  
    

def voting():
  a = ""
  while a != "0":
    print("\nVoting Function:")
    print("1 -- List All Vote Activity")
    print("2 -- Search Specific Block Content:")
    print("3 -- input data:")
    print("4 -- Mining:")
    print("5 -- voting:")
    print("6 -- Create Account:")
    print("0 -- Quit:")
    a = input("input  : ")
    if a == "1":
      print("all vote here.")
    
  
countblock = coll_blockcontent.estimated_document_count()
lastblock = coll_blockcontent.find_one({"index": int(countblock) - 1})
saveblock = Block(
  lastblock["index"],
  lastblock["timestamp"],
  lastblock["data"],
  lastblock["hash"],
  lastblock["prev_hash"],
  lastblock["difficulty"],
  lastblock["nonce"]
)
#database = ["hello", "bye", "ggg", "reg", "hsfdhdfg", "right", "alex"]

b_chain = Blockchain()

l, rl, data = "", "", ""
username, password  = "", ""
#logined = False

while rl != "0":
  print("\n1 -- Register Account")
  print("2 -- Log In")
  print("0 -- Quit:")
  rl = input("input  : ")
  if rl == "1":
    registeraccount()
  elif rl == "2":
    #logined = True
    login()
    
    print("logined: ", logined)
    
    a = ""
    while a != "0" and logined == True:
      print("\nBlockchain Function:")
      print("1 -- List All Block Content")
      print("2 -- Search Specific Block Content:")
      print("3 -- input data:")
      print("4 -- Mining:")
      print("5 -- voting:")
      print("0 -- Quit:")
      a = input("input  : ")
      if a == "1":
        b = None
        searchblock(b)
      elif a == "2":
        b = input("input block index: ")
        searchblock(b)
      elif a == "3":
        data = input("input data: ")
      elif a == "4":
        if data != "":
          b_chain.mine(
          block=Block(countblock,
                      data=[data],
                      prev_hash=lastblock["hash"],
                      nonce=0))
          print(b_chain.chain.__dict__)
          coll_blockcontent.insert_one(b_chain.chain.getResult())
        else:
          print("\nNo data for mining. Please input data.\n")
      elif a == "5":
        voting()
      elif a == "0":
        logined = False

#for data in database:
  #countblock += 1
  #countblock += 1
  ''' b_chain.mine(
      Block(num,
              data=data,
              difficulty=b_chain.dynamic_difficulty(),
              nonce=0)) '''
  ''' countblock = coll_blockcontent.estimated_document_count()
  lastblock = coll_blockcontent.find_one({"index": int(countblock) - 1})
  saveblock = Block(
    lastblock["index"],
    lastblock["timestamp"],
    lastblock["data"],
    lastblock["hash"],
    lastblock["prev_hash"],
    lastblock["difficulty"],
    lastblock["nonce"]
  ) '''
  #print("countblock: ", countblock)
  ''' b_chain.mine(
    block=Block(countblock,
                data=[data],
                prev_hash=lastblock["hash"],
                nonce=0))
  countblock += 1 '''


''' for block in b_chain.chain:
  print(block.__dict__)
  coll_blockcontent.insert_one(block.getResult()) '''

