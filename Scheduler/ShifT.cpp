#include "ShifT.h"

#include <vector>
using namespace std;

ShifT& ShifT::operator=(const ShifT& k)
{
	begin = k.begin;
	end = k.end;
	return *this;
}

ShifT& ShifT::operator=(const ShifT* k)
{
	begin = k->begin;
	end = k->end;
	return *this;
}


ostream& operator<<(ostream& os, ShifT& source)
{
	//bo nie dziala operator w hour!!!
	os << source.giveBegin().giveHour() << ".";
	if (source.giveBegin().giveMinute() < 10)
	{
		os << "0" << source.giveBegin().giveMinute();
	}
	else
	{
		os << source.giveBegin().giveMinute();
	}
	os << "  ";
	os << source.giveEnd().giveHour() << ".";
	if (source.giveEnd().giveMinute() < 10)
	{
		os << "0" << source.giveEnd().giveMinute();
	}
	else
	{
		os << source.giveEnd().giveMinute();
	}

	
	
	return os;
}

void ShifT::showShifT(std::vector<ShifT*> tab)
{
	cout << "Shift: ";
	if (tab.size() == 0)
		cout << "brak";
	else
	{
		for (ShifT* s : tab)
		{
			//cout << s << "  ";
			cout << s->printH() << "  ";
		}
	}
	cout << endl;
}
