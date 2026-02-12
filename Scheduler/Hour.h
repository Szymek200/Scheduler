#ifndef HOUR
#define HOUR

#include <string>
#include <fstream>
#include <iostream>

using namespace std;

class Hour
{
	//friend ostream& operator<<(ostream& os, Hour& source);
	int hour;
	int minute;
public:
	Hour(int h = 0, int min = 0)
	{
		setHour(h);
		setMinute(min);//wypisywanie gdy jest 07 minut!!!
	}

	//co to za warning tu mam?
	Hour(string s)//konwertuje string na godzine - krokpa pomiedzy godzina i minuta
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

	void printS()
	{
		cout << hour << ".";
		if (minute < 10)
			cout << "0";
		cout << minute << endl;
	}

	std::string print()
	{
		//minuty - robi tylko 1 zero -nie dwa - czy wczytywanie da sobie rade
		string x;
		if (minute <10)
		{
			x = to_string(hour) + ".0"+ to_string(minute);
		}
		else
		{
			x = to_string(hour) + "." + to_string(minute);
		}
		//cout << "Print:" << x << endl;
		return x;
	}

	int giveHour()
	{
		return hour;
	}

	int giveMinute()
	{
		return minute;
	}


	void setHour(string s);


	void setHour(int h);


	void setMinute(int min);

	ostream& operator<<(ostream& os);

	Hour operator-(Hour second);


	Hour operator+(Hour second);


	//sprawdzamy cze second jest wiekszy
	bool operator<(Hour second);
	bool operator!=(Hour second);


	bool operator>(Hour second);


	bool operator<=(Hour second);

	bool operator>=(Hour second);



	bool operator==(Hour second);

};


//ostream& operator<<(ostream& os, Hour& source)
//{
//	os << source.hour << ".";
//	if (source.minute < 10)
//	{
//		os << "0" << source.minute;
//	}
//	else
//	{
//		os << source.minute;
//	}
//		
//	return os;
//}


#endif // !HOUR

