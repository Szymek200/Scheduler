#pragma once

#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include "matrix.h"

struct scheduleNotPossible {};

//algorytm ukladania grafiku
class Schedule
{
	vector<Worker> people;
	//vector<Worker> zlecenia;
	vector<matrix*> places;
	
	bool hasWorkShift(date now, int wid);

	bool workingConditions(date d, Worker* w, matrix* wp, ShifT sh);

	bool minBreak(date d, ShifT sh, Worker* w);

	//na start wektor ma miec jeden element
	//level - ile razy ma w glab isc z szukaniem zastepstw
	//po przejsciu metody trzeba znowu sprawdzic czy pracownikowi prakuje zmian(gdy tak,to wstawiamy, gdzi jest wolne miejsce)
	void findSubstitution(Worker* origin);

	bool etatcomplete(Worker* person, matrix* mx, date now, ShifT* sh);


	//checks how many unoccupied hours left
	
	

public:
	Worker* idtoPointer(int wid);

	Schedule(vector<matrix*> pl, vector<Worker> peo, date w) : places(pl), people(peo)
	{
		//znajdowanie etatowcow - etaty na samym koncu
			//for (int i = 0; i < people.size(); i++)
			//{
			//	for (int j = 1 + i; j < people.size(); j++)//chce sortowac malejaco
			//	{
			//		if (people[j - 1].give_type() < people[j].give_type())
			//		{
			//			swap(people[i], people[j]);
			//		}
			//	}
			//}

		if (possibleSchedule())
		{
			//sortowanie malejaco pracownikow
			for (int i = 0; i < people.size(); i++)
			{
				//cout << "i: "<< i << endl;
				for (int j = people.size() - 1; j > 0; j--)//chce sortowac malejaco
				{
					//cout << people[j - 1].give_type().print() <<"  "<< people[j].give_type().print() << endl;
					if (people[j - 1].give_type() < people[j].give_type())
					{
						swap(people[j-1], people[j]);

						/*Worker temp = people[i];
						people[i] = people[j];
						people[i] = temp;*/
					}
					//cout << people[j - 1].give_type().print() << "  " << people[j].give_type().print() << endl;
					//cout << "---------------------" << endl;

				}
				//cout << "wypisuje godzinowki" << endl;
				////cout << people[0].give_type().print() << "--zero-";
				//for (int i = 0; i < people.size(); i++)
				//{
				//	cout << people[i].give_type().print() << "---";
				//}
				//cout << endl;
			}
		}
		else
		{
			//najlepiej wyjatek!!!
			statistics();
			scheduleNotPossible temp;
			throw temp;
			
		}
		//cout << "wypisuje godzinowki posortowane" << endl;
		//cout << people[0].give_type().print() << "--zero-";
		/*for (int i = 0; i < people.size(); i++)
		{
			cout << people[i].give_type().print() << "---";
		}
		cout << endl;*/
		



	}

	void create();

	//ile zostalo nie zapisanyc zmian na projekt
	pair<Hour, int> leftShifts()
	{
		Hour time;
		int much = 0;
		
		for (matrix* mx : places)
		{
			date ind(mx->giveDate());
			ind.setDay(1);

			for (ShifT* sh : mx->giveemptyDay(ind))
			{
				time = time + sh->giveDuration();
				much++;
			}

			try {
				ind.increaseDay();

			}
			catch (dayOutOfRange)
			{
				break;
			}
		}


		return { time, much };
	}

	//sprawdza czy z tyloma etatami da sie stworzyc grafik
	bool possibleSchedule()
	{
		return 1;
		Hour worktime;
		for (Worker p : people)
		{
			if (p.give_type() != 0)
			{
				worktime = worktime + p.give_type();
			}
			
		}

		cout << "Possible Schedule" << endl;
		worktime.printS();

		Hour placetime;
		for (matrix * w : places)
		{
			placetime = placetime + w->giveAllHours();
		}

		placetime.printS();

		if (placetime < worktime)
			return 0;
		return 1;

	}

	void statistics();


	//czy mozemy dac ta zmiane temu pracownikowi
	

};


