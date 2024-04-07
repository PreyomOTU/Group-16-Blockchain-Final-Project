'''
Ali Shaikh - 100791709
Kobi Serran - 100778822
Preyom Choudhury - 100783615
Codes on canvas was used as reference
'''

# Library

import json
import hashlib
from flask import Flask
from time import time
from uuid import uuid4
from flask.globals import request
from flask.json import jsonify


# Blockchain class, deals with creating, appending and checking blockchain

class Blockchain(object):
    # Mining difficulty level, kept at 0 for simplicity of demo
    difficulty_level = "0"
    # Creates first block, aka Genesis block
    def __init__(self):
        self.chain = []
        self.temp_trans = []

        genesis_block = {
            'index': 0,
            'transactions': [],
            'timestamp': time(),
            'nonce': 0,
            'hash_of_previous_block': '0'
        }
        self.chain.append(genesis_block)

    # Function that hashes the block using SHA256
    def Block_Hash(self, block):
        blockEncoder = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockEncoder).hexdigest()

    # Proof of work, used for security purposes
    def PoW(self, index, hash_of_previous_block, transactions):
        nonce = 0

        while self.validate_Proof(index, hash_of_previous_block, transactions, nonce) is False:
            nonce += 1
            print(nonce)
        print(nonce)
        return nonce

    def validate_Proof(self, index, hash_of_previous_block, transactions, nonce):
        data = f'{index},{hash_of_previous_block},{transactions},{nonce}'.encode()
        hash_data = hashlib.sha256(data).hexdigest()
        return hash_data[:len(self.difficulty_level)] == self.difficulty_level


    # Appending newly created block to blockchain
    def append_block(self, nonce, hash_of_previous_block):
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transactions': self.temp_trans,
            'nonce': nonce,
            'hash_of_previous_block': hash_of_previous_block
        }
        self.temp_trans = []
        self.chain.append(block)

        return block

    def add_transaction(self, supplier, customer, supply):
        self.temp_trans.append({
            'supply': supply,
            'customer': customer,
            'supplier': supplier
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

# Flask routes
app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', "")
blockchain = Blockchain()

# Route for viewing the current blocks
@app.route('/block', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

# Mines a new block, adding a sample transaction and performing proof of work
@app.route('/mineblock', methods=['GET'])
def mine_block():

    blockchain.add_transaction(
        supplier="0",
        customer=node_identifier,
        supply="boxes"
    )
    last_block_hash = blockchain.Block_Hash(blockchain.last_block)
    index = len(blockchain.chain)
    nonce = blockchain.PoW(index, last_block_hash, blockchain.temp_trans)
    block = blockchain.append_block(nonce, last_block_hash)
    response = {
        'message': "new block has been mined",
        'index': block['index'],
        'hash_of_previous_block': block['hash_of_previous_block'],
        'nonce': block['nonce'],
        'transaction': block['transactions']
    }

    return jsonify(response), 200

# list of pending transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():

    return jsonify(blockchain.temp_trans), 200

# Accepts a new transaction in JSON format and adds it to the pending transactions
@app.route('/newtransactions', methods=['POST'])
def new_transactions():

    values = request.get_json()
    required_fields = ['supplier', 'customer', 'supply']

    if not all(k in values for k in required_fields):
        return ('Missing Fields', 400)
    index = blockchain.add_transaction(
        values['supplier'],
        values['customer'],
        values['supply']
    )
    response = {'message': f'Transaction added to the block {index}'}
    return (jsonify(response), 200)

# Run on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


