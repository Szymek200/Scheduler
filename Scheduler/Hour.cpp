
#include "Hour.h"

void Hour::setHour(string s)
{
	for (int i = 0; i < s.size(); i++)
	{
		if (s[i] == '.')
		{
			setHour(stoi(s.substr(0, i)));
			setMinute(stoi(s.substr(i + 1, 2)));
		}
	}
}


void Hour::setHour(int h)
{
	//if (h >= 0 && h < 24)//nie moze byc godziny 24 - automatycznie zamieniamy na 0
	{
		hour = h;
	}
	//else if (h == 24)
		//hour = 0;
}

void Hour::setMinute(int min)
{
	if (min >= 0 && min < 60)
		minute = min;
}

ostream& Hour::operator<<(ostream& os)
{
	//nie chce to dzialac
	os << hour << "." << minute;
	return os;
}

Hour Hour::operator-(const Hour second)
{
	//zeby nir zmieniac wartosci obiektu, w ktoreym jestesmy
	Hour result = *this;
	if (minute < second.minute)
	{
		//hour--;
		result.hour--;
		result.minute = result.minute - second.minute + 60;
		//minute = minute - second.minute + 60;
	}
	else
	{
		result.minute -= second.minute;
	}

	result.hour -= second.hour;
	return result;
}

Hour Hour::operator+(Hour second)
{
	if (minute + second.minute >= 60)
	{
		hour += 1;
		minute = minute + second.minute - 60;
	}
	else
	{
		minute += second.minute;
	}
	hour += second.hour;

	return *this;
}

bool Hour::operator!=(Hour second)
{
	//dlaczego jak jestem w kasie to nie mam dostepu do skladowej prywatnej second??
	if (hour == second.hour && minute == second.minute)
		return 0;
	return 1;

}

bool Hour::operator<=(Hour second)
{
	if (hour < second.hour)
		return 1;
	if (hour == second.hour)
	{
		if (minute <= second.minute)
			return 1;

	}
	return 0;
}

//bool Hour::operator>=(Hour second)
//{
//	if (hour > second.hour)
//		return 1;
//	if (hour == second.hour)
//	{
//		if (minute >= second.minute)
//			return 1;
//
//	}
//	return 0;
//}

//sprawdzamy cze second jest wiekszy
bool Hour::operator<(Hour second)
{
	if (hour < second.hour)
		return 1;
	if (hour == second.hour)
	{
		if (minute < second.minute)
			return 1;

	}
	return 0;
}

bool Hour::operator>(Hour second)
{
	if (hour > second.hour)
		return 1;
	if (hour == second.hour)
	{
		if (minute > second.minute)
			return 1;

	}
	return 0;
}

bool Hour::operator>=(Hour second)
{
	if (hour > second.hour)
		return 1;
	if (hour == second.hour)
	{
		if (minute >= second.minute)
			return 1;

	}
	return 0;
}

bool Hour::operator==(Hour second)
{
	if (hour == second.hour && minute == second.minute)
		return 1;
	return 0;
}