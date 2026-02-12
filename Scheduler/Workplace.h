#ifndef WORKPLACE
#define WORKPLACE

#include <iostream>
#include <vector>
#include <sstream>
#include "EveryR.h"//moze to sie dodawac, gdy dodaje rule?
#include "AllR.h"
#include <filesystem>

#include "MonthT.h"
#include "originShift.h"

using namespace std;
using namespace std::filesystem;

//days daysEnum(string name);

class Workplace
{

	string name;
	//jak przechowywac zasady
	vector <Rule*> rules;//int numery zasad: 1 - kazdy dzien, 2 - cotydzien




public:
	Workplace(string namee, vector <Rule*> zasady) : name(namee), rules(zasady)
	{

	}



	//zmien wczytywanie danych dla nowych zasad
	Workplace(string file)//importowanie z pliku
	{
		ifstream plo;
		plo.open(file);

		rules.clear();
		plo >> name;
		//cin.clear();
		//cin.sync();
		//cin.ignore(); //czeka na enter???
		plo.clear();
		plo.sync();
		plo.ignore();
		while (!plo.eof())
		{
			string zasada;
			
			
			getline(plo, zasada);
			if (plo.fail())
				break;

			//zasada
			//przekierowujemy do odpowiedniej funkcji
			if (zasada == "AllR")
				AllR(plo, rules);
			if (zasada == "EveryR")
				EveryR(plo, rules);


			//tworzenie miesiaca z zasad
		}

		cout << "Zasady " <<giveName() << endl;
		for (Rule* r : rules)
		{
			cout << r->type() << "  ";
			originShift s = r->giveShift();
			{
				cout << s.giveBegin().print() << " - "<< s.giveEnd().print()<< endl;
			}
			
		}

		plo.close();
	}

	string giveName()
	{
		return name;
	}





	vector<ShifT> giveTodayShifts(date m);

	//minimalna zmiana na miesiac -> co gdy kilka osob bedzie potrzebowalo tej krotkiej zmiany???
	//minimalna zmiana w miesiacu


	void save(path newfolder);

	void editDay(date d, ShifT* sh);


	//zwraca niezajete jeszcze zmiany
	vector<ShifT> freeShifts(date d);

	vector<Rule*> todayRules(date d);


};

#endif // !WORKPLACE

