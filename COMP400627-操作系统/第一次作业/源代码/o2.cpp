#include <iostream>
#include <unistd.h>

int main()
{
	int t = 0;
	while ( true )
	{
		sleep(1);
		t++;
		std::cout<<"child has lived for " << t << " seconds." << std::endl;
	}
	return 0;
}
