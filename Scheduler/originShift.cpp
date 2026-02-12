#include "originShift.h"

#include "Hour.h"


using namespace std;

originShift& originShift::operator=(const originShift& k)
{
	begin = k.begin;
	end = k.end;
	return *this;
}

originShift& originShift::operator=(const originShift* k)
{
	begin = k->begin;
	end = k->end;
	return *this;
}

void originShift::setShift(Hour b, Hour e)
{
	begin = b;
	end = e;
}

ostream& originShift::operator<<(ostream& os)
{
	//os << begin << " " << end;
	return os;
}

bool originShift::Fitin(originShift second)
{
	if (begin > second.begin || begin == second.begin)
	{
		if (end < second.end || end == second.end)
			return 1;
	}
	return 0;
}
