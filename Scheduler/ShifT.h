#ifndef SHIFT
#define SHIFT

#include <fstream>
#include <iostream>
#include <string>
#include <vector>

#include "originShift.h"

#include "date.h"


using namespace std;

class ShifT : public originShift //dwie godziny
{
	//mozemy sprobowac dac date
protected:
	date when;
	int workerID;
	friend ostream& operator<<(ostream& os, ShifT& source);

public:
	static void showShifT(std::vector<ShifT*> tab);

	ShifT(Hour a, Hour b, date w, int wid = 0) : originShift(a, b), when(w), workerID(wid)
	{

	}

	ShifT(string zakresgodzin, date w, int wid = 0) : originShift(zakresgodzin), when(w), workerID(wid)
	{

	}

	ShifT(originShift source, date w, int wid = 0) : workerID(wid)
	{
		begin = source.giveBegin();
		end = source.giveEnd();
		when = w;

	}

	ShifT()
	{
		begin.setHour(0);
		begin.setMinute(0);
		begin.setHour(0);
		begin.setMinute(0);
		workerID = 0;

	}

	//co ma sie dziac z workerID???
	ShifT(ShifT* k)//kopiujacy
	{
		begin = k->begin;
		end = k->end;
		when = k->when;
		workerID = k->workerID;

	}

	ShifT(ShifT& k)//kopiujacy
	{
		begin = k.begin;
		end = k.end;
		when = k.when;
		workerID = k.workerID;

	}

	//potrzebowal cosnt - inaczej - blad
	ShifT(const ShifT& k)//kopiujacy
	{
		begin = k.begin;
		end = k.end;
		when = k.when;
		workerID = k.workerID;

	}

	//mam dac jako noexcept - dlaczego?
	ShifT(ShifT&& k)//przenoszacy
	{
		begin = k.begin;
		end = k.end;
		workerID = k.workerID;
	}

	//operatory nie sa dziedziczone???
	ShifT& operator=(const ShifT& k);

	ShifT& operator=(const ShifT* k);

	ostream& operator<<(ostream& os);

	//sprawdzamy czy drugi jest wiekszy

	date giveDate()
	{
		return when;
	}

	void setDate(date w)
	{
		when = w;
	}

	string print()
	{//konwersja na wskaznik i wypisanie imienia
		string x = begin.print() + " " + end.print() + " " + to_string(workerID);
		return x;
	}

	string printH()
	{//konwersja na wskaznik i wypisanie imienia
		string x = begin.print() + " " + end.print() ;
		//" when: " + to_string(when.giveDay())
		return x;
	}

	pair<Hour, Hour> giveShift()
	{
		pair<Hour, Hour> w = { begin, end };
		return w;
	}

	bool ShiftOccupied()
	{
		if (workerID != 0)
			return 1;
		return 0;
	}

	bool equaltime(ShifT second)
	{
		//to samo co rowna sie, ale bez worker
		if (when == second.when)
		{
			if (begin == second.begin && end == second.end)
			{
				return 1;
			}
		}
	}

	bool operator==(ShifT second)
	{
		//porownuje date i godziny
		//i pracownika
		if (second.giveWorker() == workerID)
		{
			if (when == second.when)
			{
				if (begin == second.begin && end == second.end)
				{
					return 1;
				}
			}
		}


		return 0;

	}

	void setWorker(int id)
	{
		//if (Worker::WorkerExist(id))
		{
			workerID = id;
		}
		//else wyjatek!!
	}


	int giveWorker()
	{
		return workerID;
	}

	

	originShift rawShift()
	{
		return originShift(begin, end);
	}
};

#endif // !SHIFT

