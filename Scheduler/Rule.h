#ifndef RULE
#define RULE

#include "originShift.h"//wystarczy zwykle Shift -> nie ma znaczenia od kogo nalezy
#include "date.h"
#include "vector"

using namespace std;

class Rule
{
protected:
	originShift time;
	int difference;//odleglosc pomiedzy dniami
	vector<days> occur;
public:
	Rule(originShift t) : time(t)
	{

	}

	//przeciazanie operatora aby zapisywac

	ostream& operator<<(ostream& os);

	//virtual, zeby dzialalo dla roznych zasad
	virtual bool isFulfilled(date when)//czy dzisiaj mozna zrealizowac ta zasade
	{
		return -1;
	}

	virtual std::vector<string> save()
	{
		std::vector<string> nic;
		return nic;
	}

	virtual string type()
	{
		return "Rule";
	}

	originShift  giveShift()
	{
		return time;
	}

	Rule()
	{
		difference = 0;
	}
};

#endif // !RULE

