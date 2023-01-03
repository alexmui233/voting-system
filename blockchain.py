import hashlib
import json
import re
import pymongo
import random
import math
from datetime import datetime
from functools import reduce
import os, Crypto.PublicKey.RSA

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["blockchain"]
coll_blockcontent = db["blockcontent"]
coll_users = db["users"]
coll_events = db["events"]
coll_records = db["records"]

def toBinary(a):
  return str(bin(int('1' + a, 16))[3:])


class Block:
  countblock = coll_blockcontent.estimated_document_count()
  lastblock = coll_blockcontent.find_one({"index": int(countblock) - 1})

  def __init__(self, index=0, timestamp=0, data=[], hash="0", prev_hash="0", difficuity=0, nonce=0):
      self.index = index
      self.timestamp = timestamp
      self.data = data
      self.hash = hash
      self.prev_hash = prev_hash
      self.difficulty = difficuity
      self.nonce = nonce

  def cal_hash(self):
      block_string = json.dumps(self.__dict__, sort_keys=True)
      returnResult = hashlib.sha256(block_string.encode('utf-8')).hexdigest()
      return returnResult

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

    #print("self.difficulty: ", self.difficulty)
    return self.difficulty

    # find the nonce of the block that satisfies the difficulty and add to chain
  def mine(self, block):
    # get the start time
    st = datetime.now().timestamp()
    #print("st:",  st)
    # attempt to get the hash of the previous block.
    # this should raise an IndexError if this is the first block.

    # loop until nonce that satisifeis difficulty is found
    while True:
      # if block.cal_hash()[:self.difficulty] == "0" * self.difficulty:
      if toBinary(block.cal_hash()).startswith('0' * self.difficulty) == True:
        #print("block.cal_hash(): ", block.cal_hash())
        savecal_hash = block.cal_hash()
        # get the end time
        et = datetime.now().timestamp()
        #print("et:",  et)
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

class Event:
  def __init__(self, eid, question, answers, owner, participants, state):
    self.eid = eid 
    self.question = question
    self.answers = answers
    self.owner = owner
    self.participants = participants
    self.state = state
  
class Record:
  def __init__(self, rid, eid, answer):
    self.rid = rid
    self.eid = eid
    self.answer = answer
    
class ring:
    def __init__(self, k, L=1024):
        self.k = k
        self.l = L
        self.n = len(list(k))
        self.q = 1 << (L - 1)

    def sign(self, m, z):
        self.permut(m)
        s = [None] * self.n
        u = random.randint(0, self.q)
        c = v = self.E(u) 
        for i in (list(range(z+1, self.n)) + list(range(z))):
            s[i] = random.randint(0, self.q)
            e = self.g(s[i], self.k[i].e, self.k[i].n)
            v = self.E(v^e) 
            if (i+1) % self.n == 0:
                c = v
        s[z] = self.g(v^u, self.k[z].d, self.k[z].n)
        return [c] + s

    def verify(self, m, X):
        self.permut(m)
        def f1(i):
            return self.g(X[i+1], self.k[i].e, self.k[i].n)
        y = list(map(f1, list(range(len(X)-1))))
        def g1(x, i):
            return self.E(x^y[i])
        r = reduce(g1, list(range(self.n)), X[0])
        return r == X[0]

    def permut(self, m):
        self.p = int(hashlib.sha256(m.encode()).hexdigest(),16)

    def E(self, x): 
        msg = '%s%s' % (x, self.p)
        return  int(hashlib.sha256(msg.encode()).hexdigest(),16)

    def g(self, x, e, n):
        q, r = divmod(x, n)
        if ((q + 1) * n) <= ((1 << self.l) - 1):
            result = q * n + pow(r, e, n)
        else:
            result = x
        return result
  
def rn(_):
  return Crypto.PublicKey.RSA.generate(1024, os.urandom)

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
    print("\nstart search.......")
    specificblock = coll_blockcontent.find_one({"index": int(GetNum)}, {"_id": 0})
    if specificblock != None:
      print(specificblock)
    else:
      print("out of index")


def registeraccount():
  username = input("\ninput user name : ")
  db_username = coll_users.find_one({"username": username}, {"_id": 0})
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
  createuser = User(countuser, username, nickname, email, password, "")
  coll_users.insert_one(createuser.__dict__)
  
  countblock = coll_blockcontent.estimated_document_count()
  block = Block(countblock, 0, [], "0",prev_hash=lastblock["hash"], difficuity=0, nonce=0)
  block.data.append(str(createuser.__dict__))
  b_chain.mine(block)
  coll_blockcontent.insert_one(b_chain.chain[-1].getResult())
  print("\nCreate account successful")
    
logined = False
logined_user = User(0, "", "", "", "", "")
def login():
  username = input("\ninput user name : ")
  db_username = coll_users.find_one({"username": username}, {"_id": 0})
  
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
      print("\nLogin successful")
      print("\nWelcome,", db_username["nickname"])
      global logined
      logined = True
      global logined_user
      logined_user = User(db_username["uid"], db_username["username"],  db_username["nickname"], db_username["email"], db_username["password"], db_username["image"])

def searchevent(Geteid):
  if Geteid == None: 
    countevent = coll_events.estimated_document_count()
    print("countevent: ", countevent)
    if countevent != 0:
      specificevent = coll_events.find({}, {"_id":0})
      print("\n------event info in the database----")
      for a in specificevent:
          print("eid:", a["eid"], "| question:", a["question"], "| owner:", a["owner"], "| state:", a["state"])
      print("------The last event info of database----\n")
    else:
      print("\nNot event found in database")
  else:
    print("\nstart search.......")
    specificevent = coll_events.find_one({"eid": int(Geteid)}, {"_id": 0})
    if specificevent != None:
      print("eid:", specificevent["eid"], "| question:", specificevent["question"], "| owner:", specificevent["owner"], "| state:", specificevent["state"])
    else:
      print("Not found match event id")

def createevent():
  question = input("input event question: ")
  if question == "":
    print("\nPlease enter a question")
    createevent()
  
  answers = ""
  answers_list = []
  while answers != "done":
    answers = input("input event answer / finish(done): ")
    if answers == "":
      print("\nPlease enter a answer")
    elif answers != "done":
      answers_list.append(answers)
      print("---answers---")
      for a in answers_list:
        print(answers_list.index(a), ": ", a)
      
  countevent = coll_events.estimated_document_count()
  event = Event(countevent, question, answers_list, logined_user.username, [], "registration") 
  coll_events.insert_one(event.__dict__)
  
  countblock = coll_blockcontent.estimated_document_count()
  block = Block(countblock, 0, [], "0",prev_hash=lastblock["hash"], difficuity=0, nonce=0)
  block.data.append(str(event.__dict__))
  b_chain.mine(block)
  coll_blockcontent.insert_one(b_chain.chain[-1].getResult())
  print("\nCreate event successful")
    
def joinevent():
  eid = input("input event id: ")
  try:
    specificevent = coll_events.find_one({"eid": int(eid)}, {"_id": 0})
    if specificevent != None:
      if specificevent["owner"] != logined_user.username:
        if specificevent["state"] == "voting":
          if logined_user.username in specificevent["participants"]:
            print("\nYou have been join this event")
          else:  
            coll_events.update_one({"eid": int(eid)}, {"$push":{"participants":logined_user.username}})
            countblock = coll_blockcontent.estimated_document_count()
            block = Block(countblock, 0, [], "0",prev_hash=lastblock["hash"], difficuity=0, nonce=0)
            block.data.append("participants: " + logined_user.username)
            b_chain.mine(block)
            coll_blockcontent.insert_one(b_chain.chain[-1].getResult())
            print("\nJoin event successful")
        else:
          print("\nThis event is not in voting state")
      else:
        print("\nCannot join your own event")
    else:
      print("\nNot found match event id")
  except ValueError:
    print('\nPlease input a integer')
    
def eventvote():
  joined = coll_events.find({"participants": logined_user.username}, {"_id": 0})
  if joined != None:
    print("\n------Joined events info in the database----")
    for j in joined:
      print("eid:", j["eid"], "| question:", j["question"], "| state:", j["state"])
    print("------The last joined event info of database----")
  voteeventid = ""
  while voteeventid !=  "cancel":
    voteeventid = input("\nfor vote input event id / cancel: ")
    try:
      voteevent = coll_events.find_one({"eid": int(voteeventid)}, {"_id": 0})
      if voteevent != None:
        if logined_user.username in voteevent["participants"]:
          if voteevent["state"] == "voting":
            print("question:", voteevent["question"], "\nanswers:")
            for ans in voteevent["answers"]:
              print(voteevent["answers"].index(ans), "-", ans)
              
            ansindex = input("input answer index: ")
            for (index, item) in enumerate(voteevent["answers"]):
              if index == int(ansindex):
                countrecord = coll_records.estimated_document_count()
                voterecord = Record(countrecord, int(voteeventid), item)
                
                key = list(map(rn, list(range(len(voteevent["participants"])))))
                r = ring(key)
                ringsign = r.sign(str(voterecord.__dict__), 0)
                print("Signature is", ringsign)
                print("Signature verified:",r.verify(str(voterecord.__dict__), ringsign))
                
                if r.verify(str(voterecord.__dict__), ringsign) == True:
                  coll_records.insert_one(voterecord.__dict__)
                  countblock = coll_blockcontent.estimated_document_count()
                  block = Block(countblock, 0, [], "0",prev_hash=lastblock["hash"], difficuity=0, nonce=0)
                  block.data.append(str(voterecord.__dict__))                
                  b_chain.mine(block)
                  coll_blockcontent.insert_one(b_chain.chain[-1].getResult())
                  print("\nVote successful")
                  break
                else: 
                  print(("\nSignature is not valid"))
            else:
              print("\nNot found match answer index")
          else:
            print("\nThis event is not in voting state")
        else:
          print("\nYou have not joined this event")
      else:
        print("\nNot found match event id")
    except ValueError:
      if voteeventid != "cancel":
        print('\nPlease input a integer')
  
def mycreateevent():
  myevent = coll_events.find({"owner": logined_user.username}, {"_id": 0})
  if myevent != None:
    print("\n------my events info in the database----")
    for e in myevent:
      print("eid:", e["eid"], "| question:", e["question"], "| participants:", len(e["participants"]), "| state:", e["state"])
    print("------The last my event info of database----")
    mce = ""
    while mce !=  "0":
      print("1 -- Change state")
      print("2 -- View event detail")
      print("0 -- Quit")
      mce = input("input  : ")
      if mce == "1":
        eid = ""
        while eid != "cancel":
          eid = input("\nfor change state input event id / cancel: ")
          try:
            changestateevent = coll_events.find_one({"eid": int(eid), "owner": logined_user.username}, {"_id": 0})
            if changestateevent != None:
              if changestateevent["state"] == "registration":
                coll_events.update_one({"eid": int(eid)}, {"$set":{"state":"voting"}})
              elif changestateevent["state"] == "voting":
                coll_events.update_one({"eid": int(eid)}, {"$set":{"state":"result"}})
              
              if changestateevent["state"] != "result":
                changedstate = coll_events.find_one({"eid": int(eid), "owner": logined_user.username}, {"_id": 0})
                print("\neid:", changedstate["eid"], "| state:", changedstate["state"])
                print("\nChange event state successful")
              else:
                print("\nThe event state is result")
            else:
              print("\nNot found match event id")
          except ValueError:
            if eid != "cancel":
              print('\nPlease input a integer')
      elif mce == "2":
        eid = ""
        while eid != "cancel":
          eid = input("\nfor view event detail input event id / cancel: ")
          try:
            specificevent = coll_events.find_one({"eid": int(eid), "owner": logined_user.username}, {"_id": 0})
            
            if specificevent != None:
              if specificevent["state"] == "result":
                totalans = coll_records.count_documents({"eid":{"$eq": int(eid)}})
                print("question:", specificevent["question"], "\nvoters:", totalans, "\nanswers:")
                for ans in specificevent["answers"]:
                  anscount = coll_records.count_documents({"eid":{"$eq": int(eid)}, "answer": ans})
                  if totalans != 0:
                    print(ans, "--", round(anscount / totalans * 100), "%")
                  else:
                    print(ans, "--", "0 %")
                ''' anspercent = coll_records.aggregate([{"$group" : {"_id":"$answer", "count":{"$sum":1}}}, {"$sort": {"count":-1}}])
                
                for a in anspercent:
                  if totalans != 0:
                    print(a["_id"], "--", round(a["count"] / totalans * 100), "%")
                  else:
                    for a in specificevent["answers"]:
                      print(a, "--", "0 %") '''
              else:
                print("\nThe event state is not result")
            else:
              print("\nNot found match event id")
          except ValueError:
            if eid != "cancel":
              print('\nPlease input a integer')
  else:
    print("Not found your events")
  
def viewjoinedeventresult():
  joined = coll_events.find({"participants": logined_user.username}, {"_id": 0})
  if joined != None:
    print("\n------Joined events info in the database----")
    for j in joined:
      print("eid:", j["eid"], "| question:", j["question"], "| state:", j["state"])
    print("------The last joined event info of database----")
    eid = ""
    while eid != "cancel":
      eid = input("\nfor view event detail input event id / cancel: ")
      try:
        specificevent = coll_events.find_one({"eid": int(eid), "participants": logined_user.username}, {"_id": 0})
        
        if specificevent != None:
          if specificevent["state"] == "result":
            totalans = coll_records.count_documents({"eid":{"$eq": int(eid)}})
            print("question:", specificevent["question"], "\nvoters:", totalans, "\nanswers:")
            for ans in specificevent["answers"]:
              anscount = coll_records.count_documents({"eid":{"$eq": int(eid)}, "answer": ans})
              if totalans != 0:
                print(ans, "--", round(anscount / totalans * 100), "%")
              else:
                print(ans, "--", "0 %")
          else:
            print("\nThe event state is not result")
        else:
          print("\nNot found match event id")
      except ValueError:
        if eid != "cancel":
          print('\nPlease input a integer')
  else:
    print("Not found your events")

def voting():
  a = ""
  while a != "0":
    print("\nVoting Function:")
    print("1 -- List all vote events")
    print("2 -- Search specific event Content")
    print("3 -- Create event")
    print("4 -- Join event")
    print("5 -- Event vote")
    print("6 -- My created events")
    print("7 -- View joined event result")
    print("0 -- Quit")
    a = input("input  : ")
    if a == "1":
      b = None
      searchevent(b)
    elif a == "2":
      b = input("input event id: ")
      searchevent(b)
    elif a == "3":
      createevent()
    elif a == "4":
      joinevent()
    elif a == "5":
      eventvote()
    elif a == "6":
      mycreateevent()
    elif a == "7":
      viewjoinedeventresult()
    
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

b_chain = Blockchain()

l, rl, inputdata = "", "", ""

while rl != "0":
  print("\n1 -- Register account")
  print("2 -- Log in")
  print("0 -- Quit")
  rl = input("input  : ")
  if rl == "1":
    registeraccount()
  elif rl == "2":
    login()
    
    a = ""
    while a != "0" and logined == True:
      print("\nBlockchain Function")
      print("1 -- List all block content")
      print("2 -- Search specific block content")
      print("3 -- Input data")
      print("4 -- Mining")
      print("5 -- Voting")
      print("0 -- Quit")
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
          Block(countblock,
                      data=[inputdata],
                      prev_hash=lastblock["hash"],
                      nonce=0))
          for bk in b_chain.chain:
            print(bk.__dict__)
            coll_blockcontent.insert_one(bk.getResult())
        else:
          print("\nNo data for mining. Please input data.\n")
      elif a == "5":
        voting()
      elif a == "0":
        logined = False

