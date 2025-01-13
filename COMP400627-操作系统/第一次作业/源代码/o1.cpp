#include <iostream>
#include <unistd.h>
#include <signal.h>

int main()
{
	pid_t pid = fork();
	if(pid == 0)
	{
		execl("o2","o2",NULL);
	}
	else if(pid > 0)
	{
		long long  t = 0;
		t =  2 << 29;
		long long p = t;
		long long s = 0;
		while(p != 1)
		{
			long long c = t%p;
			if( c == 0)
				s++;
			p--;
		}
		kill(pid,SIGTERM);
		exit(0);
	}
	else
	{
		std::cout << "failed to create a new process."<< std::endl;
	}
	return 0;

}

