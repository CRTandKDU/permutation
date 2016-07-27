// OTBob.cpp
//


#include <string>
#include <iostream>
#include "stdafx.h"
#include "OTEngine.h"

int main()
{
	std::string host;
	int port = 5555;
	OTEngine *bob;
	int bit = 0;

	host = std::string("localhost");
	bob = new OTEngine(host, port);
	bob->connect_bind(OTEngine::OT_ROLERECEIVER);
	(void) bob->init_fill(NULL, NULL, bit);
	bob->transfer();

	delete bob;

	return 0;
}
