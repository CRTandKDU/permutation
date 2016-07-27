// OTAlice.cpp
//
#include <string>
#include <iostream>
#include "stdafx.h"
#include "OTEngine.h"

int main()
{
	std::string host; 
	int ret, port = 5555;
	OTEngine *alice;
	BIGNUM *bnm0, *bnm1;

	host = std::string("localhost");
	bnm0 = BN_new(); bnm1 = BN_new();
	ret = BN_pseudo_rand(bnm0, OT_MSGSIZE, 0, 1);
	ret = BN_pseudo_rand(bnm1, OT_MSGSIZE, 0, 1);

	alice = new OTEngine(host, port);
	alice->connect_bind(OTEngine::OT_ROLESENDER);
	(void) alice->init_fill( bnm0, bnm1, 0 );
	alice->transfer();

	delete alice;

	BN_free(bnm0); BN_free(bnm1);
    return 0;
}

