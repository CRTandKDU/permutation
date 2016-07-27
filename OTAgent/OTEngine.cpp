/**
* \file		OTEngine.cpp
* \brief	Implements the 1-2 Oblivious Transfer protocol based on RSA.
* \author	jmc@massiverand.com
* \version	1.0
*/

#include "OTEngine.h"


OTEngine::OTEngine(std::string ahost, int aport )
{
	port = aport; host = ahost;
}


OTEngine::~OTEngine()
{
	if (socket) socket->close();
	if (role == OTEngine::OT_ROLESENDER) {
		if (rsa) RSA_free(rsa);
		if (e) BN_free(e);
		if (bnv) BN_free(bnv);
		if (bnx0) BN_free(bnx0);
		if (bnx1) BN_free(bnx1);
		if (bnm00) BN_free(bnm00);
		if (bnm11) BN_free(bnm11);
		if (ctx) BN_CTX_free(ctx);
	}
	if (role == OTEngine::OT_ROLERECEIVER) {
		if (NULL != bnm00) BN_free(bnm00);
		if (NULL != bnm11) BN_free(bnm11);
		if (NULL != bnk) BN_free(bnk);
		if (NULL != bnv) BN_free(bnv);
		if (NULL != bnx0) BN_free(bnx0);
		if (NULL != bnx1) BN_free(bnx1);
		if (NULL != ctx) BN_CTX_free(ctx);
		BN_free(bnn);
		BN_free(bne);
	}
}

void OTEngine::connect_bind(unsigned int agent)
{
	char buf[128];
	role = agent;
	context = zmq::context_t(1);
	if(agent == OTEngine::OT_ROLESENDER ){
		socket = new zmq::socket_t(context, ZMQ_REP);
		sprintf(buf, "tcp://*:%d", port);
		socket->bind(buf);
	}
	if(agent == OTEngine::OT_ROLERECEIVER){
		socket = new zmq::socket_t(context, ZMQ_REQ);
		sprintf(buf, "tcp://%s:%d", host.c_str(), port);
		socket->connect(buf);
	}
}

int OTEngine::init_fill(BIGNUM *m0, BIGNUM *m1, int bit)
{
	int bits = 1024;
	int ret = 1;
	// Inits common messages/bignums
	ctx = BN_CTX_new();
	bnv = BN_new(); bnx0 = BN_new(); bnx1 = BN_new();

	if (role == OTEngine::OT_ROLESENDER) {
		// Keep messages
		bnm0 = m0; bnm1 = m1;
		// Prepare RSA keys pair
		rsa = RSA_new();
		if (NULL == rsa) return 0;
		// Inits intermediate messages/bignums
		bnm00 = BN_new(); bnm11 = BN_new();
		// Create RSAkey pair
		e = BN_new();
		BN_set_word(e, RSA_F4);
		ret = RSA_generate_key_ex(rsa, bits, e, NULL);
	}
	if (role == OTEngine::OT_ROLERECEIVER) {
		// Inits intermediate messages/bignums
		bnk = BN_new();
		ret = BN_pseudo_rand(bnk, OT_RANDKSIZE, 0, 1);
		ret = BN_pseudo_rand(bnx0, OT_RANDKSIZE, 0, 1);
		ret = BN_pseudo_rand(bnx1, OT_RANDKSIZE, 0, 1);
		b1of2 = bit;
	}
	return ret;
}

void OTEngine::sendBN(BIGNUM *bn, zmq::socket_t *socket) {
	zmq::message_t reply;
	unsigned char *buf;
	size_t size;
	size = BN_bn2mpi(bn, NULL);
	buf = (unsigned char *)malloc(size);
	reply = zmq::message_t(size);
	(void)BN_bn2mpi(bn, buf);
	memcpy(reply.data(), buf, size);
	std::cout << "Sending " << size << " bytes." << std::endl;
	socket->send(reply);
	free((void *)buf);
}

bool OTEngine::onMessage(unsigned long msg, RSA *rsa, zmq::socket_t *socket, 
	BIGNUM **bn, BIGNUM *bnx)
{
	unsigned long rec;
	zmq::message_t reply, request;
	switch (msg) {
	case OT_MSG_READYB:
		sendBN(bnx, socket);
		break;

	case OT_MSG_PREPAREB:
		rec = OT_MSG_PREPAREB;
		reply = zmq::message_t(sizeof(unsigned long));
		memcpy(reply.data(), &rec, sizeof(unsigned long));
		socket->send(reply);

		socket->recv(&request);
		*bn = BN_mpi2bn((unsigned char *)request.data(), request.size(), NULL);
		std::cout << "bn = " << BN_bn2dec(*bn) << std::endl;

		reply = zmq::message_t(sizeof(unsigned long));
		memcpy(reply.data(), &rec, sizeof(unsigned long));
		socket->send(reply);
		break;

	case OT_MSG_READYEXP:
		sendBN(rsa->e, socket);
		break;

	case OT_MSG_READYRSA:
		sendBN(rsa->n, socket);
		break;

	default:
		break;
	}
	return true;
}


void OTEngine::transfer()
{
	zmq::message_t reply;
	zmq::message_t request;
	unsigned long msg;
	int ret;

	if (role == OTEngine::OT_ROLESENDER) {
		std::cout << "RSA keys:" << std::endl;
		std::cout << "n = " << BN_bn2dec(rsa->n) << std::endl;
		std::cout << "d = " << BN_bn2dec(rsa->d) << std::endl;
		std::cout << "e = " << BN_bn2dec(rsa->e) << std::endl;
		std::cout << "Messages:" << std::endl;
		std::cout << "m0 = " << BN_bn2dec(bnm0) << std::endl;
		std::cout << "m1 = " << BN_bn2dec(bnm1) << std::endl;
		socket->recv(&reply);
		memcpy(&msg, reply.data(), reply.size());
		std::cout << "Received OT message: " << msg << std::endl;
		(void)onMessage(msg, rsa, socket, NULL, NULL);

		socket->recv(&reply);
		memcpy(&msg, reply.data(), reply.size());
		std::cout << "Received OT message: " << msg << std::endl;
		(void)onMessage(msg, rsa, socket, NULL, NULL);

		socket->recv(&reply);
		memcpy(&msg, reply.data(), reply.size());
		std::cout << "Received OT message: " << msg << std::endl;
		(void)onMessage(msg, rsa, socket, &bnv, NULL);

		socket->recv(&reply);
		memcpy(&msg, reply.data(), reply.size());
		std::cout << "Received OT message: " << msg << std::endl;
		(void)onMessage(msg, rsa, socket, &bnx0, NULL);

		socket->recv(&reply);
		memcpy(&msg, reply.data(), reply.size());
		std::cout << "Received OT message: " << msg << std::endl;
		(void)onMessage(msg, rsa, socket, &bnx1, NULL);

		ret = BN_sub(bnm00, bnv, bnx0);
		ret = BN_mod_exp(bnm00, bnm00, rsa->d, rsa->n, ctx);
		ret = BN_mod_add(bnm00, bnm00, bnm0, rsa->n, ctx);
		ret = BN_sub(bnm11, bnv, bnx1);
		ret = BN_mod_exp(bnm11, bnm11, rsa->d, rsa->n, ctx);
		ret = BN_mod_add(bnm11, bnm11, bnm1, rsa->n, ctx);

		socket->recv(&reply);
		memcpy(&msg, reply.data(), reply.size());
		std::cout << "Received OT message: " << msg << std::endl;
		(void)onMessage(msg, rsa, socket, NULL, bnm00);

		socket->recv(&reply);
		memcpy(&msg, reply.data(), reply.size());
		std::cout << "Received OT message: " << msg << std::endl;
		(void)onMessage(msg, rsa, socket, NULL, bnm11);
	}

	if (role == OTEngine::OT_ROLERECEIVER) {
		reply = zmq::message_t(sizeof(unsigned long));
		msg = OT_MSG_READYRSA;
		memcpy(reply.data(), &msg, sizeof(unsigned long));
		socket->send(reply);
		socket->recv(&request);
		bnn = BN_mpi2bn((unsigned char *)request.data(), request.size(), NULL);
		std::cout << "n = " << BN_bn2dec(bnn) << std::endl;

		reply = zmq::message_t(sizeof(unsigned long));
		msg = OT_MSG_READYEXP;
		memcpy(reply.data(), &msg, sizeof(unsigned long));
		socket->send(reply);
		socket->recv(&request);
		bne = BN_mpi2bn((unsigned char *)request.data(), request.size(), NULL);
		std::cout << "e = " << BN_bn2dec(bne) << std::endl;

		// Sending a bignum
		ret = BN_mod_exp(bnv, bnk, bne, bnn, ctx);
		ret = BN_mod_add(bnv, bnv, 0 == b1of2 ? bnx0 : bnx1, bnn, ctx);
		std::cout << "v  = " << BN_bn2dec(bnv) << std::endl;
		std::cout << "x0 = " << BN_bn2dec(bnx0) << std::endl;
		std::cout << "x1 = " << BN_bn2dec(bnx1) << std::endl;

		reply = zmq::message_t(sizeof(unsigned long));
		msg = OT_MSG_PREPAREB;
		memcpy(reply.data(), &msg, sizeof(unsigned long));
		socket->send(reply);
		socket->recv(&request);
		// Should check here the receipt
		sendBN(bnv, socket);
		socket->recv(&request);
		// Should check here the receipt

		reply = zmq::message_t(sizeof(unsigned long));
		msg = OT_MSG_PREPAREB;
		memcpy(reply.data(), &msg, sizeof(unsigned long));
		socket->send(reply);
		socket->recv(&request);
		// Should check here the receipt
		sendBN(bnx0, socket);
		socket->recv(&request);
		// Should check here the receipt

		reply = zmq::message_t(sizeof(unsigned long));
		msg = OT_MSG_PREPAREB;
		memcpy(reply.data(), &msg, sizeof(unsigned long));
		socket->send(reply);
		socket->recv(&request);
		// Should check here the receipt
		sendBN(bnx1, socket);
		socket->recv(&request);
		// Should check here the receipt

		reply = zmq::message_t(sizeof(unsigned long));
		msg = OT_MSG_READYB;
		memcpy(reply.data(), &msg, sizeof(unsigned long));
		socket->send(reply);

		socket->recv(&request);
		bnm00 = BN_mpi2bn((unsigned char *)request.data(), request.size(), NULL);
		std::cout << "m00 = " << BN_bn2dec(bnm00) << std::endl;

		reply = zmq::message_t(sizeof(unsigned long));
		msg = OT_MSG_READYB;
		memcpy(reply.data(), &msg, sizeof(unsigned long));
		socket->send(reply);

		socket->recv(&request);
		bnm11 = BN_mpi2bn((unsigned char *)request.data(), request.size(), NULL);
		std::cout << "m11 = " << BN_bn2dec(bnm11) << std::endl;

		ret = BN_sub(bnv, 0 == b1of2 ? bnm00 : bnm11, bnk);
		std::cout << "mb   = " << BN_bn2dec(bnv) << std::endl;
	}

}
