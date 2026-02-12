#pragma once
#include "list.h"
#include "Hour.h"
//#include "ShifT.h"
#include "Workplace.h"
#include "Worker.h"
//#include "Month.h"
//#include "MonthT.h"
#include <filesystem>
#include "list.h"
#include "list_elem.h"

class matrix
{

	Workplace* w;
	date month;
	MonthT* m;
	originShift minshift;
	Hour allHours;
	//vector<int> WorkerID;//zapisujemy ludzi, ktorzy juz maja zmiany na obiekcie
	lista WorkerID;

public:

	matrix(Workplace* we, date now): w(we)
	{
		minshift = originShift("0.00", "24.00");
		now.setDay(1);
		month = now;
		m = new MonthT(now.giveMonth(), now.giveYear());
		
		for (int i = 1; i <= now.monthsize(); i++)
		{
			now.setDay(i);

			vector<ShifT*> todayShifts;
			
			
			//ustawiam na sztywno minshift - bo algorytm caly czas zmniejsza end!!!

			//minshift = originShift("0.00", "8.00");
			cout << date::dayString(now.giveName()) << endl;
			
 			for (Rule* rule : w->todayRules(now))
			{
				
				//minshift.print();
				if ((rule->giveShift()).giveDuration() < minshift.giveDuration())
				{

					//cout << "zmiana" << endl;
					
					
						minshift = rule->giveShift();
						
					
					//rule->giveShift().print();
					
					//minshift.print();
				}
				//minshift.print();
				ShifT * temp = new ShifT(rule->giveShift(), now);
				//minshift.print();
				todayShifts.push_back(temp);

			//	allHours = allHours + temp->giveDuration();
				//allHours.printS();
				//minshift.print();
				//cout << "--------------------" << endl;

			}
			for (ShifT* s : todayShifts)
			{
				cout << s->print()<< endl;
			}

			m->editDay(i, todayShifts);
			cout << endl;

			//cout << "Minumal" << endl;
			//minshift.print();
		}

		system("cls");

		


	}

	Hour giveAllHours()
	{
		return allHours;
	}

	void show();

	//godziny zmiany musza byc rowne - nie zawierac sie w srodku
	//zapisuje do vektora workerID, ze ma takiego pracownika
	void addWorker(ShifT * sh)
	{
		//if (Worker::WorkerExist(sh.giveWorker()))
		//{
		//	
		//	for (ShifT* elem : m->todayShifts(sh.giveDate()))
		//	{
		//		if (elem->giveBegin() == sh.giveBegin() && elem->giveEnd() == sh.giveEnd())
		//		{
		//			//potrzebny wskaznik na ShifT
		//			if (elem->giveWorker() == 0)
		//			{
		//				elem->setWorker(sh.giveWorker());
		//				WorkerID.push_back(sh.giveWorker());
		//				cout << "workerID: " << WorkerID.back() << " size " << WorkerID.size() << endl;
		//				break;
		//			}
		//			
		//			//trzeba zwiekszac workhours w worker - problem z zapetleniem??
		//			//w schedule to robie!!!

		//			//break;
		//		}
		//	}

		//sh - jest to konkretna zmiana z matrix - trzeba tylko ustawic workerID
		try {
			WorkerID.find(sh->giveWorker());
		}
		catch (notFound)
		{
			WorkerID.dodaj(sh->giveWorker());
		}
		
			
		//cout << "workerID: " << WorkerID.back() << " size " << WorkerID.Size() << endl;
		
	}

	void addWorker(int wid, originShift sh, date now)
	{
		if (Worker::WorkerExist(wid))
		{
			

			for (ShifT* elem : m->todayShifts(now))
			{
				if (sh.Fitin(elem->rawShift()))
				{

					elem->setWorker(wid);
					WorkerID.dodaj(wid);

					//cout << "workerID: " << WorkerID.back() <<  " size "<< WorkerID.size() << endl;
					//nie wiem czy sa inne miejsca, gdzie ta funkcje wywoluje
					//trzeba zwiekszac workhours w worker - problem z zapetleniem??
					//w schedule to robie!!!
					break;
				}
			}
		}
	}

	void deleteWorker(ShifT *clean)
	{
		
		m->todayShifts(clean->giveDate());
		for (ShifT* elem : m->todayShifts(clean->giveDate()))
		{
			if (elem == clean)
			{
				//usuwanie z wektora - iiny kontener?? - wlasny
				//tymczasem
				for (int i = 0; i < WorkerID.Size(); i++)
				{
					if (WorkerID[i] == elem->giveWorker())
					{
						//int z = WorkerID[i].conv(); // przeciez typ T to jest w tym wypadku int!!!
						//WorkerID[i] = 0;//marnowanie miejsca!! - tu nie ma problemu z typem!!!
						

						//usuwamy element
						WorkerID.usun(i);
						break;
					}
				}
				elem->setWorker(0);

			//	WorkerID.usun(WorkerID.find(clean->giveWorker())); //ta linijka wywoluje blad w find - list
				
				break;
			}
			//else wyjatek!!!
		}
	}

	//daje puste zmiany na dany dzien
	vector<ShifT*> giveemptyDay(date now)
	{
		vector<ShifT*>result;
		
		for (ShifT* d : m->todayShifts(now))
		{
			if (d->giveWorker() == 0)
			{
				result.push_back(d);
			}
		}
		return result;
	}

	bool hasWorkShift(date now, int wid)
	{
		vector<ShifT> result;//w result mamy kopie danych z miesiaca?!
		
		for (ShifT* d : m->todayShifts(now))
		{
			if (d->giveWorker() == wid)
				return 1;
		}
		return 0;
	}

	std::vector<ShifT*> todayShifts(date now)
	{
		return m->todayShifts(now);
	}

	//zwracane zmiany musza sie miescic w zakresie
	std::vector<ShifT*> todayShifts(date now, originShift range)
	{
		std::vector<ShifT*> r;
		for (ShifT* d:m->todayShifts(now))
		{
			if (d->Fitin(range))
				r.push_back(d);
		}

		
		return r;
	}

	ShifT * earlierShift(ShifT origin, int wid)
	{
		for (int i = origin.giveDate().giveDay(); i >= 1; i--)
		{
			vector<ShifT*> result = m->todayShifts(i);
			for (ShifT* d : result)
			{
				if (d->giveWorker() == wid)
				{
					return d;
				}
			}
		}
	}

	string giveName()
	{
		return w->giveName();
	}

	//zwraca zmiany, ktore czlowiek ma w dany dzine
	vector<ShifT*> workerShifts(int wid, date now)
	{
		vector<ShifT*> result;
		for (ShifT* sh : m->todayShifts(now))
		{
			if (sh->giveWorker() == wid)
			{
				result.push_back(sh);
			}
		}

		return result;
	}

	Hour minShiftD()
	{
		return minshift.giveDuration();
	}

	originShift minShift()
	{
		return minshift;
	}

	//czy dostal tutaj zmiane
	bool workHere(int wid)
	{
		for (int i = 0; i < WorkerID.Size(); i++)
		{
			if (WorkerID[i] == wid)
			{
				return 1;
			}
		}
		return 0;
	}

	date giveDate()
	{
		return month;
	}

	void save(path newfolder);
};

