#ifndef DATE
#define DATE

#include <map>
#include <string>

enum months { January, February, March, April, May, June, July, August, September, October, November, December, Non };
enum days { Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday, None, All };





struct dayOutOfRange {};






class date
{


	days name;
	months mname;
	int day;
	int month;
	int year;

	bool holiday;

	days reference = Monday;//moze byc statyczna

	bool przestepny(int y);


	//chyba zbedne - mamy taka sama bez argumentow
	int monthsize(months name, int year); //dlugosc miesiaca


	//konwersja enum -> int
	int monthNumber(months name);

	//konwersja enum -> int
	int dayNumber(days name);

	//nazwa dnia na poczatku roku
	//day begin i which day mozna scalic
	days daybegin();//jaki dzien tygodnia na poczatku miesiaca


	//jak znamy nazwe pierwszego dnia, to mozemy wyznaczyc nastepne
	days dayoffset(days begin, int distance);//returns a name of a day from a day (jaki dzien tygodnia za 6 dni od poniedzialku)


	months monthName(int z);


	bool verify(int d, int m, int y);


public:
	//lepiej const
	static std::string dayString(days d);
	static days daysOfWeek[8];
	static months monthsOfYear[13];
	static days daytoint(int d);

	static months monthsEnum(std::string name);
	static days daysEnum(std::string name);

	static months monthint(int n);

	static int dayint(days d);

	//jak zrobic, zeby dalo sie nie pisac typu obiektu tylko same nawiasy konstuktora???
	date(int d, int m, int y, bool b = 0)
	{
		
			set(d, m, y, b);
		

	}

	bool operator==(date second)
	{
		if (day == second.day && month == second.month && year == second.year)
			return 1;

		return 0;
	}

	//std::string dayString();

	days giveName()
	{
		return name;
	}

	months giveMName()
	{
		return mname;
	}

	int giveMonth()
	{
		return month;
	}

	int giveYear()
	{
		return year;
	}

	void set(int d, int m, int y, bool b = 0);


	void set(days dd, months mm, int y, bool b = 0);


	void setDay(int d);


	bool ifHoliday()
	{
		return holiday;
	}

	//zwiekszam o jeden dzien
	date operator++();


	//powinno byc dostepne tylko dla month
	int monthsize(); //dlugosc miesiaca


	int giveDay()
	{
		return day;
	}

	void increaseDay();


	date()
	{
		//omijamy funkcje set i verify
		day = 0;
		month = 0;
		year = 0;
		holiday = 0;
		name = None;
		//rozne enum nie moze miec tych samych wartosci???
		mname = Non;
		//jaka dac wartosc z enum???

	}

	date(std::string s)
	{
		//informacje sa oddzielone kropka
		//d.m.y
		//01.03.1940

		int d = stoi(s.substr(0, 2));
		int m = stoi(s.substr(2, 2));
		int y = stoi(s.substr(6, 4));

		set(d, m, y);


	}

	//bo operatory nie moga zglaszac wyjatkow
	void decreaseDay();





};

#endif // !DATE

