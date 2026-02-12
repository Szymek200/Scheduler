#ifndef WORKER
#define WORKER

#include <string>
#include <vector>
#include <iostream>
#include <filesystem>
#include "Month.h"
#include "originShift.h"

using namespace std;
using namespace std::filesystem;

//months monthsEnum(string name)
//{
//	for (int i = 1; i <= 9; i++)
//	{
//		if (name == to_string(date::monthsOfYear[i]))
//		{
//			return date::monthsOfYear[i];
//		}
//	}
//
//	return date::monthsOfYear[0];
//}

//days daysEnum(string name)
//{
//	for (int i = 1; i <= 9; i++)
//	{
//		if (name == to_string(date::daysOfWeek[i]))
//		{
//			return date::daysOfWeek[i];
//		}
//	}
//
//	return date::daysOfWeek[0];
//}

class Worker
{
	std::string name;
	std::string surname;
	int id;

	static int id_set;
	//Month* shifts;//zmiany - dni w ktorych pracownik chce pracowac//juz zbedne!!!

	//zmiana - data(dzien, miesiac) rodziny (rozpoczecia - zakonczenia)

	//std::vector<int> cos; - tu skladnia jest poprawna!!!
	Month employeeDays; // dni w ktorych chce pracowac - index jest numerem dnia - Shift, bo zalezy nam tylko na zakresie godzin

	//informacje czy jest zatrudniony na zlecenie czy umowa do pracy
	//nie ma restrykcji godzinowych
	Hour etat;//ile godzin musi wyrobic!!!
	//najlepiej jak bysmy gdzies to zapisywali

	// na jakich basenach chce

	Hour workHours;//ile godzin przepracowal w miesiacu
	Hour sleepTime;//da sie w tym miejscu ustawic wartosc?

	vector<std::string> m_workPlace;

	static int settingID()
	{
		id_set++;
		return id_set;
	}

public:

	int giveID()
	{
		return id;
	}

	std::string giveName()
	{
		return name  +surname;
	}

	static bool WorkerExist(int num)
	{
		if (num > 0 && num <= id_set)
			return 1;
		return 0;
	}
	Worker(string namee, string surnamee, int mon, int year, Hour et) : name(namee), surname(surnamee), etat(et)//nie wykorzystuje tego!!!
	{
		//employeeDays = new Month<originShift>(mon, year);
		employeeDays.settingMonth(mon, year);

		id = settingID();
		//int* wsk = new int;
	}

	Worker(string file, int year)
	{
		ifstream plo;
		plo.open(file);

		workHours.setHour(0);
		workHours.setMinute(0);
		id = settingID();

		plo >> name;
		plo >> surname;

		//ludzi o takim samym imieniu moga sie powtarzac - maja ID
		

		int et;
		plo >> et;
		etat.setHour(et);
		//miejsca pracy
		string places;
		plo.clear();
		plo.sync();
		plo.ignore();
		getline(plo, places);
		//szybciej sstream
		places += " ";
		string temp = "";
		for (int i = 0; i < places.size(); i++)
		{
			if (places[i] == ' ')
			{
				m_workPlace.push_back(temp);
				temp = "";
			}
			else
				temp += places[i];
		}
		string miesiac;
		plo >> miesiac;//pracownik musi zapisac miesiac!!!
		//konwersja 
		//employeeDays = new Month<originShift>(monthsEnum(miesiac), year);
		employeeDays.settingMonth(date::monthsEnum(miesiac), year);

		//dzien + godzina

		while (!plo.eof())//jedziemy, az nie wyskoczy blad konca plikui
		{
			int numb;
			plo >> numb;
			if (plo.fail())
				break;

			string zakresGodzin;//wszystkie zmiany ktore sa wewnatrz tych godzin
			//plo >> zakresGodzin;//14-22
			plo.clear();
			plo.sync();
			plo.ignore();
			std::getline(plo, zakresGodzin);
			originShift* k = new originShift(zakresGodzin);
			employeeDays.editDay(numb, k);


		}



		sleepTime.setHour(11);

		plo.close();
	}

	void changeEtat(int x)
	{
		etat = x;
	}

	void save(path newfolder);

	Hour give_type()
	{
		//zero oznacza, ze zlecenie
		return etat;
	}

	bool workRange(date d, originShift& range);

	bool thisPlace(string workplace);

	Hour giveWorkHours()
	{
		return workHours;
	}

	void addWork(Hour dur)
	{
		workHours = workHours + dur;
	}

	void deleteWork(Hour dur)
	{
		workHours = workHours - dur;

	}
	//czy wpisalismy go do pracy
	//bool hasWorkShift(date d, vector<Shift>& result);

	//bool hasWorkShift(date d);

	Hour givesleepTime()
	{
		return sleepTime;
	}



	void giveEmployeeDays(Month& result)
	{
		result = employeeDays;
	}
};

#endif // !WORKER

