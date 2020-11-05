import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import requests
from flask import Flask, render_template, jsonify, redirect, request
import requests
from textwrap import dedent
from time import time
import db

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
        myid = address
         # parsed_url = urlparse(address)# address 쉽게 표현 
         # self.nodes.add(parsed_url.netloc)  # 받은 address 넷주소 + port
        self.nodes.add(myid)
        
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
    
    
    
app = Flask(__name__)
#mydb=MysqlController() 
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


@app.route('/')
def index():
    return render_template('index.html')
 

@app.route('/trade')
def trade():
    return render_template('trade.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced==True:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    elif replaced==False:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Error : Not resolved',
            'chain': blockchain.chain
        }
    return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine():

    last_block = blockchain.last_block
    last_proof = last_block['proof']

    
    proof = blockchain.proof_of_work(last_proof)
    
    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        ssoin=1
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'new block forged',
        'index': block['index'],
        'transactions': block['transaction'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
        }
    return jsonify(response), 200
    
    
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    sender = request.form['sender']
    recipient = request.form['recipient']
    ssoin = request.form['ssion']
    
    data = {
        'sender' : sender,
        'recipient' : recipient,
        'ssoin': ssoin
    }
    
    index = blockchain.new_transaction(data['sender'],
                                       data['recipient'],
                                       data['ssoin'])

    response = {'message':
                'Transaction will be added to Block {0}'.format(index)}

    return jsonify(response), 201

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    reg_nodes = request.form['node']
    
    print(reg_nodes)
    
    values = {
        "nodes" : [reg_nodes],
    }
    
    nodes = values.get('nodes')
        
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    
    return jsonify(response), 201, 
    #return values

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=5000)

