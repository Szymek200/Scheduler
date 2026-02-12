#include "Schedule.h"
#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <string>
#include "Worker.h"
#include "Workplace.h"

#include "matrix.h"

Worker* Schedule::idtoPointer(int wid)
{
	for (int i = 0; i < people.size(); i++)
	{
		if (people[i].giveID() == wid)
			return &people[i];
	}
}

void Schedule::create()
{
	//najpierw etaty - gdzie chca i musza sie im zgadac godziny - moze byc odchylka, ale o mniej niz 1 zmiana
	//potem zlecenia

	//kazdy miesiac ma wszystkie dni, tylko w niektorych shift = nullptr

	date indicator(places[0]->giveDate());
	indicator.setDay(1);
	while (true)//kazdy dzien, po kolei
	{
		//cout << "dzien" <<indicator.giveDay()<<" "<<date::dayString(indicator) <<"---------------------------------- - "<< endl;
		//kazda zmiana w dniu-> jak to zrobic z wieloma workplace??
		for (matrix* w : places)//kazdy place
		{
			cout << "Workplace: " << w->giveName() << endl;
			vector<ShifT*> thisPlace;
			thisPlace = w->giveemptyDay(indicator);
			ShifT::showShifT(thisPlace);

			for (ShifT *sh : thisPlace)//kazda zmiana w place
			{
				cout <<"Sh: "<< sh->printH() << endl;
				//szukamy osoby na dana zmiane
				for (Worker& person : people)//zaczynamy od najwiekszej liczby godzin 
				{
					cout << person.giveName() << endl;
					//tymczasowo wstawiamy goscia do zmiany(zeby min break moglo dobrze dzialac
					//sh->setWorker(person.giveID());
					//sprawdzamy liczbe godzin, dzien, zmiane (czy pasuje)
					if (workingConditions(indicator, &person, w, sh))
					{
						cout << "Tak" << endl;
						//person.saveWorkShift(indicator, sh);
						//w.editDay(indicator, sh);
						sh->setWorker(person.giveID()); // robimy juz to wczesniej
						//zwiekszamy liczbe godzin

						idtoPointer(person.giveID())->addWork(sh->giveDuration());
						cout << "worker hours: "; idtoPointer(person.giveID())->giveWorkHours().printS(); cout << endl;
						w->addWorker(sh);
						break;//inaczej to zapisuje wiele osob do 1 zmiany
					}
					else
					{
						//sh->setWorker(0);//kasujemy pracownika, bo byl na chwile i nie mozemy go wpisac na stale
					}
				}
			}
		}
		try {
			indicator.increaseDay();//zwiekszamy o jeden dzien!!!
		}
		catch (dayOutOfRange)
		{
			
			break;
		}
	}

	//druga runda -  przenosimy zmiany
	cout << "Druga runda" << endl;
	vector<Worker*> left;//jaka za malo godzin
	

	left.clear();
	//ponownie sprawdzamy czy wszyscy etatowcy maja wyrobione godziny
	
	for (Worker& person : people)
	{
		if (person.give_type() != Hour())//domysla wartosc - zero
		{
			//places[0]->minShift().print();

			if (person.give_type() > person.giveWorkHours())
			{
				left.push_back(&person);
			}
		}
	}

	//wstawiamy jak leci, bo musza wyrobic godziny
	date ind(indicator);
	ind.setDay(1);
	system("cls");
	while (true)
	{
		for (matrix* mx : places)
		{
				for (ShifT* sh : mx->giveemptyDay(ind))
				{
					cout << sh->giveDate().giveDay() << endl;
					for (Worker* p : left)
					{
						
						if (etatcomplete(p, mx, sh->giveDate(),sh) == 0)//jeszcze mozemy dodac godzine
						{
							cout << p->giveName() << "  Tak" << endl;
							sh->setWorker(p->giveID()); // robimy juz to wczesniej
							//zwiekszamy liczbe godzin

							idtoPointer(p->giveID())->addWork(sh->giveDuration());
							cout << "worker hours: "; idtoPointer(p->giveID())->giveWorkHours().printS(); cout << " id "<< p->giveName() << endl;
							mx->addWorker(sh);
							goto identyfikator;
						}
						else
						{
							cout << p->giveName() << "  NIe" << endl;
						}
					}	
				}

			identyfikator:
				cout << "wyszedlem" << endl;
		}
		try {
			ind.increaseDay();//zwiekszamy o jeden dzien!!!
		}
		catch (dayOutOfRange)
		{

			break;
		}
	}

	left.clear();

	for (Worker& person : people)
	{
		if (person.give_type() != Hour())//domysla wartosc - zero
		{
			//places[0]->minShift().print();

			if (person.give_type() - person.giveWorkHours() >= places[0]->minShiftD())
			{
				left.push_back(&person);
			}
		}
	}

	cout << "Ludzie bez pracy: " << left.size() << endl;
	pair <Hour, int> t = leftShifts();
	cout << "Puste zmiany: ";  t.first.printS(); cout << " " << t.second << endl;



	for (Worker* p : left)
	{
		date ind(places[0]->giveDate());
		ind.setDay(1);
		int level = 1;//obecnie substitution nie wykorzystuje tego

		//while (p->giveWorkHours() <= p->give_type() - places[0]->minShiftD())
		{
			//dla goscia z argumentu ma wyszukac 
			//funkcja robi chyba wszystkie mozliwe zamiany- wystarczy zrobic raz dla kazdego pracownika
			findSubstitution(p);


		}
	}

}

//sprawdza czy ktos dzisiaj pracuje we wszystkich matrix
bool Schedule::hasWorkShift(date now, int wid)
{
	for (matrix * mx : places)
	{
		if (mx->workHere(wid))
		{
			if (mx->hasWorkShift(now, wid))
				return 1;
		}
	}
	return 0;

}

bool Schedule::etatcomplete(Worker * person,matrix * mx,date now, ShifT *sh)
{
	if (person->give_type() > person->giveWorkHours())//czy moze jeszcze pracowac??? -> automatycznie powinien sprawdzac
	{
		//czy przerwa pomiedzy zmianami
		if (minBreak(now, sh, person))
		{
			return 0;


		}
		

	}
	return 1;
}

bool Schedule::workingConditions(date d, Worker* person, matrix* w, ShifT sh)
{
	//sh to ustanawiana zmiana

	//czy chce pracowac w ten dzien
	//czy ta zmiana mu pasuje
	//czy odstep pomiedzy zmianami jest wystarczajacy
	//czy ma odpowiednia liczbe wolnych dni
	ShifT workinghours;
	if (person->thisPlace(w->giveName()) && person->workRange(d, workinghours))
	{
		//zmiany workera w ten dzien - jest tylko jedna zmiana - chodzi o przedzial czasowy(nie konkretne zmiany)
		// = person->todayShift(d);
		if (sh.Fitin(workinghours))//czy miescimy sie w wybracych godzinach pracy???
		{
			//dla zleceniowcow trzeba inaczej	//min shift trzeba dopracowac!!!
			//czy miescimy sie w etacie
			Hour zero;
			if (person->give_type() != zero)
			{
				if (person->give_type() - person->giveWorkHours() >= w->minShiftD())//czy moze jeszcze pracowac??? -> automatycznie powinien sprawdzac
				{
					//czy przerwa pomiedzy zmianami
					if (minBreak(d, sh, person))
					{
						return 1;


					}


				}
			}
			else
			{
				//zleceniowcy
			}
			
		}
	}

	return 0;





}

//chodzi o sen - wiec tylko w nocy
bool Schedule::minBreak(date d, ShifT sh, Worker* w)
{
	//sh - ustanawiana zmiana


	//lepiej zeby hour bylo czescia date - latwiej sie odejmuje wiele dni

	bool ok = 1;

	for (matrix* mx : places)
	{
		if (mx->workHere(w->giveID()))
		{
			//Workhere jest puste!!!

			//obliczamy dystans pomiedzy zmianami
			//zmiana sh musi juz miec zapisanego goscia!!!
			ShifT *ealier = mx->earlierShift(sh, w->giveID());
			if (ealier == nullptr) // warunek workHere powinien wszystko wylapywac
				continue;
			Hour diff;
			if (sh.giveDate().giveDay() != ealier->giveDate().giveDay())
			{
				//ograniczenie godzinowe!!!
				diff =(sh.giveDate().giveDay() - ealier->giveDate().giveDay() - 1) * 24, 0;//-1 -> chodzi nam o pelne dni pomiedzy
				diff = diff + Hour(24, 0) - ealier->giveEnd();
				diff = diff + sh.giveBegin();
			}
			else
			{
				//zmiany w tym samym dniu
				if (w->give_type() != 0)
				{
					//etatowcy nie moga pracowac w tym samym dniu!!!
					return 0;
				}
				else
				{
					//bardziej skomplikowane warunki!!!
					if (sh.giveBegin() >= ealier->giveEnd())//sh jest pozniej od ealier
					{
						diff = sh.giveBegin() - ealier->giveEnd();
					}
					else if (sh.giveEnd() >= ealier->giveEnd())
					{
						diff = ealier->giveEnd() - sh.giveBegin();
					}
				}
				
			}
			
			if (diff < w->givesleepTime())
				ok = 0;
		}
	}

	return ok;//jeden - przerwa jest zachowana - odstep pomiedzy zmianami - problem dla zleceniowcow(brak 2 zmian pod rzad)

}

//wyszukuje zmiany dla goscia co ma za malo godzin
//znajduje zmiane, ktora moglby wzmiac -> i szuka innej zmiany dla osoby, ktora obecnie zajmuje ta zmiane!!
void Schedule::findSubstitution(Worker* origin)
{
	//przeszukiwania zaczynamy od poczatku miesiaca czy od miejsca zamiany???
	date ind( places[0]->giveDate());
	ind.setDay(1);

	//udaje, ze robie dla jednego origin i result
	cout << origin->giveName() << endl;
	while (true)
	{
		cout << "Origin day " << ind.giveDay() << endl;
		for (matrix* w : places)
		{
			cout << w->giveName() << endl;
			originShift posSh;//zakres godzin dla pracownika
			if (origin->workRange(ind, posSh) && hasWorkShift(ind, origin->giveID()) == 0 && origin->thisPlace(w->giveName()))//moze pracowac, ale nic nie dostal
			{
				//cout << origin->giveName() << " moze pracowac w godzinach "; posSh.print();
				//szuka drugiej osoby, dla ktorej mamy puste miejsce - level 1
				//przechodze po zmianach->osobach - i szukam czy w miesiacu jest wolna zmiana, ktora mogliby wziac

				int zet = 0; //testowa - do zliczania wyjscia 11111
				for (ShifT* temp : w->todayShifts(ind, posSh))
				{

					//--------------------------------DRUGI GOSC----------------------------------------
					//dla kazdego goscia poszukujemy wolnej zmiany
					//cout << "Zastepca jest" << idtoPointer(temp->giveWorker())->giveName()<<" ------------------------------------------" << endl;

					date index(ind);
					index.setDay(1);

					//petla po calym miesiacu dla drugiego pracownika
					while (true)
					{
						//dni w ktorych moglby pracowac - level 1 szukamy tylko wolnych zmian
						originShift vek;//mozliwe zmiany -> zakres godzin, wkotrych drugi moze pracowac
						//cout << "index " << index.giveDay() << endl;
						if (idtoPointer(temp->giveWorker())->workRange(ind, vek) && hasWorkShift(ind, temp->giveWorker()) == 0)
						{
							//^ moze pracowac dzisiaj, ale nie ma zmiany dzisiaj
							for (matrix* we : places)
							{
			
								if(idtoPointer(temp->giveWorker())->thisPlace(we->giveName()))//chce pracowac w tym miejscu
								{
									//cout << w->giveName() << endl;
									for (ShifT *chw : we->giveemptyDay(index))//wolne zmiany na dany obiekt
									{
										chw->printH();
										if (workingConditions(chw->giveDate(), idtoPointer(temp->giveWorker()), we, chw) && minBreak(chw->giveDate(), chw, idtoPointer(temp->giveWorker())))
										{
											//origin i temp - pracownicy - wskazniki
											cout << "Tak" << endl;
											ShifT* forOrigin = temp;

											//musimy zrobic przez add i delete worker, zeby working hours sie zmienily!!!
											chw->setWorker(temp->giveWorker());
											idtoPointer(temp->giveWorker())->addWork(chw->giveDuration());
											we->addWorker(chw);

											w->deleteWorker(temp);
											idtoPointer(temp->giveWorker())->deleteWork(temp->giveDuration());//czy uda sie usunac samego siebie

											//drugi zostal przesuniety

											temp->setWorker(origin->giveID());
											idtoPointer(origin->giveID())->addWork(temp->giveDuration());
											w->addWorker(temp);

											

											//chyba dobrze, ale mozna lepiej to zrobic?
										}
									}
								}
							}
						}
						try {
							index.increaseDay();
						}
						catch (dayOutOfRange)
						{
							zet++;
							//cout << "WYCHODZE1111111---------------------------------------- " << zet << endl;
							
							break;
						}
					}
				}
			}
		}
		//inkrementacja
		try {
			ind.increaseDay();
		}
		catch (dayOutOfRange)
		{
			cout << "WYCHODZE22222----------------------------------------" << endl;
			break;
		}
	}
}

void Schedule::statistics()
{
	date ind(places[0]->giveDate());
	
	Hour lefth;
	int shifts = 0;

	while (true)
	{
		for (matrix* mx : places)
		{
			for (ShifT* sh : mx->giveemptyDay(ind))
			{
				
				lefth = lefth + sh->giveDuration();
				shifts++;
			}
		}
		try {
			ind.increaseDay();//zwiekszamy o jeden dzien!!!
		}
		catch (dayOutOfRange)
		{
			break;
		}
	}

	cout << "Pozostalo wolnych zmia: " << shifts << " co oznacza godzin: " << lefth.print() << endl;
	
}