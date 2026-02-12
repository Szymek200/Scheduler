#include "date.h"
#include <map>
#include <iostream>

days date::daysOfWeek[8] = { None, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday };


months date::monthsOfYear[13] = { Non, January, February, March, April, May, June, July, August, September, October, November, December };


days date::daysEnum(std::string name)
{
	/*for (int i = 1; i <= 9; i++)
	{
		if (name == std::to_string(date::daysOfWeek[i]))
		{
			return date::daysOfWeek[i];
		}
	}

	return date::daysOfWeek[0];*/

	std::map< std::string, days > mapa;

	mapa["Monday"] = Monday;
	mapa["Tuesday"] = Tuesday;
	mapa["Wednesday"] = Wednesday;
	mapa["Thursday"] = Thursday;
	mapa["Friday"] = Friday;
	mapa["Saturday"] = Saturday;
	mapa["Sunday"] = Sunday;
	return mapa[name];

}

//czy ma byc statyczna?
std::string date::dayString(days d)
{
	std::map<days, std::string> mapa;

	mapa[Monday] = "Monday";
	mapa[Tuesday] = "Tuesday";
	mapa[Wednesday] = "Wednesday";
	mapa[Thursday] = "Thursday";
	mapa[Friday] = "Friday";
	mapa[Saturday] = "Saturday";
	mapa[Sunday] = "Sunday";

	

	return mapa[d];

}

int date::dayint(days d)
{
	std::map<days, int> mapa;

	mapa[Monday] = 1;
	mapa[Tuesday] = 2;
	mapa[Wednesday] = 3;
	mapa[Thursday] = 4;
	mapa[Friday] = 5;
	mapa[Saturday] = 6;
	mapa[Sunday] = 7;



	return mapa[d];

}

days date::daytoint(int d)
{
	std::map<int, days> mapa;

	mapa[1] = Monday;
	mapa[2] = Tuesday;
	mapa[3] = Wednesday;
	mapa[4] = Thursday;
	mapa[5] = Friday;
	mapa[6] = Saturday;
	mapa[7] = Sunday;



	return mapa[d];

}


months date::monthint(int n)
{
	std::map<int, months> mapa;

	{
		mapa[1] = January;
		mapa[2] = February;
		mapa[3] = March;
		mapa[4] = April;
		mapa[5] = May;
		mapa[6] = June;
		mapa[7] = July;
		mapa[8] = August;
		mapa[9] = September;
		mapa[10] = October;
		mapa[11] = November;
		mapa[12] = December;
	}
	//months wynik = mapa[name];

	return mapa[n];

}

months date::monthsEnum(std::string name)
{
	
	
		std::map<std::string, months> mapa;
		
		{
			mapa["January"] = January;
			mapa["February"] = February;
			mapa["March"] = March;
			mapa["April"] = April;
			mapa["May"] = May;
			mapa["June"] = June;
			mapa["July"] = July;
			mapa["August"] = August;
			mapa["September"] = September;
			mapa["October"] = October;
			mapa["November"] = November;
			mapa["December"] = December;
		}
		//months wynik = mapa[name];

		return mapa[name];
		//warunek nie chce dzialac
		/*if (name == std::to_string(date::monthsOfYear[i]))
		{
			return date::monthsOfYear[i];
		}*/

	
	

	return date::monthsOfYear[0];
}

bool date::przestepny(int y)
{
	if (y % 400 == 0)
		return 1;
	if (y % 4 == 0 && y % 100 != 0)
		return 1;

	return 0;
}

//chyba zbedne - mamy taka sama bez argumentow
int date::monthsize(months name, int year) //dlugosc miesiaca
{
	if (name == April || name == June || name == September || name == November)
	{
		return  30;
	}
	if (name == February)
	{
		if (year % 4 == 0)//przestepny
			return  29;
		else
			return  28;
	}
	else
		return  31;
}

//konwersja enum -> int
int date::monthNumber(months name)
{

	for (int i = 1; i <= 12; i++)
	{
		if (monthsOfYear[i] == name)
		{
			return i;
		}
	}

	return 0;

}
//konwersja enum -> int
int date::dayNumber(days name)
{
	for (int i = 1; i <= 7; i++)
	{
		if (daysOfWeek[i] == name)
		{
			return i;
		}
	}

	return 0;

}
//nazwa dnia na poczatku roku
//day begin i which day mozna scalic
days date::daybegin()//jaki dzien tygodnia na poczatku miesiaca
{//mamy numer miesiaca = monthnumber i rok mYear
	int ryear = 1;//o dwa dni co roku sie przesuwamy - gdy przestepny = 2
	int difference = 0;
	for(int i = 2024; i < year; i++)
	//while (2024 + difference < year)
	{
		if (przestepny(difference + 2024))
			difference += 2;
		else
			difference++;

		
	}

	for (int i = 1; i < month; i++)//bez miesiaca, w ktorym jestesmy
	{
		difference += monthsize(monthint(i), year);
	}

	//difference++;//abyu wskoczyc na pierwszy dzien w naszym miesiacu
	//2024 zaczyna sie od poniedzialku
	return dayoffset(Monday, difference);
}

//jak znamy nazwe pierwszego dnia, to mozemy wyznaczyc nastepne
days date::dayoffset(days begin, int distance)//returns a name of a day from a day (jaki dzien tygodnia za 6 dni od poniedzialku)
{
	int offset = distance % 7;

	if (dayNumber(begin) + offset > 7)
	{
		offset = dayNumber(begin) + offset - 7;
		return daysOfWeek[offset];
	}
	else
	{
		return daysOfWeek[offset + dayNumber(begin)];
	}
	
}

months date::monthName(int z)
{
	if (z > 0 && z < 13)
	{
		return monthsOfYear[z];
	}

	return monthsOfYear[0];
}

bool date::verify(int d, int m, int y)
{
	if (m < 1 || m >12)
		return 0;

	if (d > 0 && d <= monthsize())
	{
		return 1;
	}
	else
		return 0;

}


void date::set(int d, int m, int y, bool b)
{
	if (verify(d, m, y))
	{
		year = y;
		month = m;
		day = d;

		days resp = daybegin();
		
		name = dayoffset(resp, d-1);

		holiday = b;

		mname = monthName(month);

	}
	//else
	//{
	//	//wyjatek!!! - przyda sie do czegos???
	//	//dayOutOfRange message;
	//	//throw message;
	//}

}

void date::set(days dd, months mm, int y, bool b)
{
	int m = monthNumber(mm);
	int d = dayNumber(dd);

	if (verify(d, m, y))
	{
		year = y;
		month = m;
		day = d;
		name = dayoffset(daybegin(), d);

		holiday = b;

		mname = monthName(month);

	}
	else
	{
		//wyjatek!!!
		dayOutOfRange message;
		throw message;
	}

}

void date::setDay(int d)
{
	if (verify(d, month, year))
	{
		int x = date::dayint(giveName());
		x++;
		x = x % 8;
		
		name = daytoint(x);
		day = d;
		//zmiana nazwy dnia
		
		
	}
	else
	{
		//wyjatek!!!
		//dayOutOfRange message;
		//throw message;
	}
}

date date::operator++()
{
	if (day + 1 <= monthsize())
		day += 1;
	else
	{
		//wyjatek!!!
		dayOutOfRange message;
		throw message;
	}

}

//powinno byc dostepne tylko dla month
int date::monthsize() //dlugosc miesiaca
{
	if (month == 4 || month == 6 || month == 9 || month == 11)
	{
		return 30;
	}
	if (month == 2)
	{
		if (przestepny(year))//przestepny
			return 29;
		else
			return 28;
	}
	else
		return 31;
}

void date::increaseDay()
{
	if (day + 1 <= monthsize())
	{
		day++;
	}
	else
	{
		dayOutOfRange nazwajeden;
		throw nazwajeden;
	}


}

void date::decreaseDay()
{
	if (day - 1 <= monthsize())
	{
		day--;
	}
	else
	{
		dayOutOfRange nazwajeden;
		throw nazwajeden;
	}


}