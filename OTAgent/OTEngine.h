#pragma once
#include <zmq.hpp>
#include <string>
#include <iostream>
#ifndef _WIN32
#include <unistd.h>
#else
#include <windows.h>
#define sleep(n)    Sleep(n)
#endif

#include <openssl/bn.h>
#include <openssl/rsa.h>

#define OT_MSG_READYRSA	1000UL
#define OT_MSG_READYEXP	1001UL
#define OT_MSG_PREPAREB	2000UL
#define OT_MSG_READYB	2001UL

#define OT_RANDKSIZE 32
#define OT_MSGSIZE 256

class OTEngine
{
private:
	// 0MQ connection information
	std::string host;
	int port;
	zmq::context_t context = (zmq::context_t)NULL;
	zmq::socket_t  *socket = NULL;

	// Agent can be sender or receiver in the 1-2-Oblivious-Transfer protocol
	unsigned int role = 0;

	// Commmon data
	BIGNUM *bnv, *bnx0, *bnx1;
	BN_CTX *ctx;

	// Sender data
	RSA *rsa;
	BIGNUM *e;
	BIGNUM *bnm0, *bnm1, *bnm00, *bnm11;

	// Receiver data
	BIGNUM *bnn, *bnk, *bne;
	int b1of2;

	void sendBN(BIGNUM *bn, zmq::socket_t *socket);
	bool onMessage(unsigned long msg, RSA *rsa, zmq::socket_t *socket, BIGNUM **bn, BIGNUM *bnx);

public:
	static const unsigned int OT_ROLESENDER = 1;
	static const unsigned int OT_ROLERECEIVER = 2;

	OTEngine(std::string ahost, int aport);
	~OTEngine();

	void connect_bind(unsigned int role);
	int init_fill( BIGNUM *m0, BIGNUM *m1, int bit);
	void transfer();
};

