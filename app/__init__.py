import logging



from app import *
from app import log, storage, node, transaction
from app.block import Block
from app.communicator import receiver, sender, my_ip_address
from app.consensus.merkle_tree import merkle_tree, merkle_tree_2
from app.consensus.pow import proof_of_work
from app.node.Node import Node
from app.node import key

storage.init()


listen_thread = None
port_number = None

def send_transaction(msg):
	# pri_key, pub_key = key.get_key()
	tx = transaction.create_tx(msg)
	transaction.send_tx(tx)

def initiate_node(port):
	port_number = port
	set_my_node(False)
	node.key.generate_key()

	log.write("Start node")
	start_node()


'''
	Start Receiver Thread
	PORT: 10654
'''


def start_node():
	import threading
	global listen_thread
	listen_thread = threading.Thread(target=receiver.start, args=("Listener_Thread",
																  my_ip_address.get_ip_address('en0'), port_number))
	listen_thread.start()


def stop_node():
	storage.session.commit()
	storage.session.close()
	receiver.stop()
	global listen_thread
	listen_thread.join()


def create_block():
	transactions = transaction.get_transactions()

	# transaction이 없을 경우 block을 생성하지 않음
	if len(transactions) == 0:
		return

	_block = block.create_block(transactions)

	block.store_block(_block)

	# 내 node가 가지고 있는 transaction 삭제
	transaction.remove_all()

	# 나머지 node에게 block 전송
	sender.send_to_all_node((_block.to_json()), except_my_node=True)


def list_all_node():
	for n in node.get_all():
		log.write(n, logging.DEBUG)


def list_all_transaction():
	for t in transaction.get_transactions():
		log.write(t, logging.DEBUG)


def list_all_block():
	for b in block.get_all_block():
		log.write(b, logging.DEBUG)


def set_my_node(set_my_node=True):
	if set_my_node:
		my_node = Node(my_ip_address.get_ip_address('en0'))
		node.add_node(my_node)
	log.write("Set my node")

