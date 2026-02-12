#ifndef ORIGINSHIFT
#define ORIGINSHIFT

#include "Hour.h"
#include <sstream>
class originShift
{
protected:
	Hour begin;
	Hour end;
public:
	originShift(Hour b, Hour e) : begin(b), end(e)//nie wystarczy, ze hour jest domyslne???
	{}

	originShift(string b, string e) : begin(b), end(e)
	{}

	//jedna spacja pomiedzy godzinami -kropka pomiedzy godzina i minuta

	std::string save()
	{
		return begin.print() + " " + end.print();
	}

	originShift()
	{
		begin.setHour(0);
		begin.setMinute(0);
		end.setHour(0);
		end.setMinute(0);
	}

	originShift(string zakresGodzin)//14-22 lub 12.22-6.07
	{
		//for (int i = 0; i < zakresGodzin.size(); i++)
		//{
		//	if (zakresGodzin[i] == '-')
		//	{
		//		begin.setHour(zakresGodzin.substr(0, i));
		//		end.setHour(zakresGodzin.substr(i + 1, zakresGodzin.size() - 1 - i));//mam nadzieje, ze sie nie pomylilem
		//	}
		//}

		stringstream ss(zakresGodzin);
		string dwa;
		ss >> zakresGodzin;
		ss >> dwa;
		begin = zakresGodzin;
		end = dwa;

	}



	originShift(originShift& k)//kopiujacy
	{
		begin = k.begin;
		end = k.end;
	}

	originShift(const originShift& k)//kopiujacy
	{
		begin = k.begin;
		end = k.end;
	}

	originShift(originShift&& k)//przenoszacy
	{
		begin = k.begin;
		end = k.end;
	}

	bool operator==(originShift second)
	{
		if (begin == second.begin && end == second.end)
		{
			return 1;
		}
		return 0;
	}

	void print()
	{
		begin.printS();
		cout << "  ";
		end.printS();
		cout << endl;
	}

	originShift& operator=(const originShift& k);

	originShift& operator=(const originShift* k);

	//void setShift(string b, string e)
	//{
	//	begin = b;// w locie jest wstanie skonwertowac na hour ze string
	//	end = e;
	//}

	void setShift(Hour b, Hour e);

	ostream& operator<<(ostream& os);

	//sprawdzamy czy drugi jest wiekszy


	Hour giveDuration()
	{
		return end - begin;
	}

	//sprawdza czy dana zmiana miesci sie w innej zmianie
	bool Fitin(originShift second);

	Hour giveEnd()
	{
		return end;
	}

	Hour giveBegin()
	{
		return begin;
	}

};

#endif // !ORIGINSHIFT



