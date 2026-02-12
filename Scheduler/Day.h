#ifndef DAY
#define DAY

#include <vector>
#include "ShifT.h"
#include "originShift.h"
//#include "date.h"
using namespace std;
//mozna jakos zawezic mozliwe typy w szablonie???

//ShifT lub originshift
template <typename T>
class Day
{
	date id;
	vector<T*> time;

public:
	Day(date d, T *h) : id(d)//wykorzytujemy przy importowaniu - nie potrzeba wiadomosci o miesiacu???
	{
		//time = new ShifT(h);
		setTime(h);
	}

	Day(date d) : id(d)//wykorzytujemy przy importowaniu - nie potrzeba wiadomosci o miesiacu???
	{}

	Day(date d, vector<T*> h) : id(d)//wykorzytujemy przy importowaniu - nie potrzeba wiadomosci o miesiacu???
	{
		//time = new Shift(h);
		setTime(h);
	}

	void setDay(days namee, int num)
	{
		id.setDay(namee);
		id.number = num;
	}

	void setDate(date d)
	{
		id = d;
	}

	void setTime(T *h)
	{
		//time* = h;//co jest nie tak z przeladowaniem operatora???
		time.clear();
		time.push_back(h);
	}

	void setTime(vector<T*> w)//dodawanie wielu zmian na jeden dzien
	{
		time.clear();//konieczne??
		time = w;

	}

	vector<T*> giveShifts()
	{
		return time;
	}


	std::vector<T*> giveShiftsPoint()
	{
		return time;
	}

	date giveDate()
	{
		return id;
	}
	//give onwner
};

#endif // !DAY

