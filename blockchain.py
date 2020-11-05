import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
#import db

class Blockchain(object):  # 블록체인 클래스
    def __init__(self):  # 초기화 
        self.chain = [] 
        self.current_transactions = []
        self.new_block(previous_hash=1, proof=100)
        self.nodes = set()  

    def new_block(self, proof, previous_hash=None): 
        block = {
            'index': len(self.chain) + 1, 
            'timestamp': time(), 
            'transaction': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) # previous_hash 에 대한역할 
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def register_node(self, address):  
        parsed_url = urlparse(address)# address 쉽게 표현 
        self.nodes.add(parsed_url.netloc)  # 받은 address 넷주소 + port
        
        
    def new_transaction(self, sender, recipient, ssoin):
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'ssoin': ssoin
        })
        return self.last_block['index'] + 1

    def valid_chain(self, chain):  # 각가의 블록과 증명의 유효성을 검사합니다.

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):  
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------------\n")

            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):  # 합의 알고리즘으로 체인이 가장긴 것 체인으로 교체

        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length :
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = str(last_proof * proof).encode()
        #  guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == "0000"  # 0000 nonce값  (난이도조절)
