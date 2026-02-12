#ifndef MONTH
#define MONTH

#include <iostream>
#include <vector>

#include "originShift.h"

#include "Day.h"



class Month
{
	int monthsize;

	months name;
	int month;
	int year;

	vector<Day<originShift>> content;




public:

	void settingMonth(int m, int y)
	{
		date temp = date(1, m, y);
		monthsize = temp.monthsize();
		month = m;
		year = y;
		name = temp.giveMName();

		//tworzenie dni w miesiacu

		for (int i = 1; i <= monthsize; i++)
		{
			date te(i, month, year);
			Day<originShift> newday(te);
			content.push_back(newday);
			//daloby sie od razu w psuh back podac informacje do konstuktora???
		}



		
	}

	int monthSize()
	{
		return monthsize;
	}

	Month(int m, int y)
	{
		settingMonth(m, y);
	}


	Month()
	{

		month = 0;
		year = 0;
		monthsize = 0;
		std::cout << month;
	}

	void editDay(int numDay, originShift* t)//zmiana godzi zmian pracy
	{
		
		content[numDay].setTime(t);
	}

	void editDay(int numDay, vector<originShift*> t)//zmiana godzi zmian pracy
	{
		
		content[numDay].setTime(t);
	}

	//musi byc wskaznik!!!
	std::vector<originShift*> todayShifts(date d)
	{

		return content[d.giveDay()].giveShiftsPoint();
	}
	/*void todayShifts(date d, vector<originShift>& result)
	{

		content[d.giveDay()].giveShiftsPoint();
	}*/



	int monthNumber()
	{
		return month;
	}

	int yearNumber()
	{
		return year;
	}



	Hour MinShift()
	{
		Hour min(25, 0);
		for (Day<originShift> d : content)
		{
			for (originShift *sh : d.giveShifts())
			{
				if (sh->giveDuration() < min)
					min = sh->giveDuration();
			}
		}
		return min;

	}
};

#endif // !MONTH

