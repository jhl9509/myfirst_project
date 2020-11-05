from flask import Flask, render_template, jsonify, redirect, request
import requests
import json
from textwrap import dedent
from uuid import uuid4
from time import time
from blockchain import Blockchain

 
app = Flask(__name__)
 
node_identifier = str(uuid4()).replace('-', '')
print(node_identifier)
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
