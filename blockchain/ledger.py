import hashlib
import json
from time import time

class ComplaintLedger:
    def __init__(self):
        self.chain = []
        self.current_complaints = []
        self.create_block(proof=1, previous_hash='0')
    
    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'complaints': self.current_complaints,
            'proof': proof,
            'previous_hash': previous_hash
        }
        # Calculate hash AFTER creating the block structure
        block['hash'] = self.hash_block(block)
        self.current_complaints = []
        self.chain.append(block)
        return block
    
    def hash_block(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def add_complaint(self, complaint):
        complaint_with_hash = {
            'data': complaint,
            'hash': hashlib.sha256(json.dumps(complaint).encode()).hexdigest()
        }
        self.current_complaints.append(complaint_with_hash)
        return complaint_with_hash['hash']  # Return the hash for reference
