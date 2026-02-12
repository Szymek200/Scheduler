#pragma once
#include "list_elem.h"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

using namespace std;

struct notFound {};


class lista
{
	
	//lista_elem<T>* szczyt;
	std::shared_ptr < lista_elem >  szczyt;
	int size;

public:
	void dodaj(int x)
	{
		size++;
		if (szczyt == nullptr)
		{
			//szczyt = new lista_elem<T>(x);
			
			//szczyt(new lista_elem<T>);

			//szczyt
			szczyt = std::make_unique<lista_elem>();
			szczyt->zmien(x);
			
			 
		}
		else
		{
			
			std::shared_ptr < lista_elem > wsk = szczyt;
			

			//lista_elem<T>* wsk = szczyt;
			while (wsk->next() != nullptr)
			{

				wsk = wsk->next();

			}
			std::shared_ptr < lista_elem> ptr(new lista_elem);
			ptr->zmien(x);
			wsk->save(ptr);
			//wsk_ > save(std::shared_ptr< lista_elem<T> > wsk = szczyt);
		}
	}
	void usun()//usuwamy ostatni element
	{
		size--;
		if (szczyt != nullptr)
		{
			std::shared_ptr < lista_elem > wsk = szczyt;
			//lista_elem<T>* wsk = szczyt;
			std::shared_ptr < lista_elem > ostatni_zywy;
			//lista_elem<T>* ostatni_zywy = nullptr;
			while (wsk->next() != nullptr)
			{
				ostatni_zywy = wsk;
				wsk = ostatni_zywy->next();

			}

			//delete[] wsk;
			wsk = nullptr;


			if (szczyt->next() != nullptr)
				ostatni_zywy->save(nullptr);
		}
	}

	//rozmiar od 1, ale indeks od zera
	void usun(int num)
	{
		if (num >= 0 && num < size)
		{
			if (num == 0)
			{
				usun_front();
			}
			else
			{
				size--;
				std::shared_ptr < lista_elem > chw = szczyt;
				std::shared_ptr < lista_elem > before;
				//lista_elem<T>* chw = szczyt;
				for (int i = 0; i < num; i++)//wypadkiemy na elemencie to usuniecia
				{
					//std::cout << chw->give() << std::endl;
					before = chw;
					chw = chw->next();

				}

				before->save(chw->next());

				//chw sie samo usunie???


			}
		}
		
		
	}

	int operator[](int ind)
	{
		if (ind >= 0 && ind < size)
		{
			std::shared_ptr < lista_elem > chw = szczyt;
			
			for(int i =0; i< ind; i++)
			{
				
				chw = chw->next();
			}
			
			int zm = chw->give();
			return zm;
			//return chw.give();
		}
	}

	//to samo co operator[]
	int Give(int ind)
	{
		if (ind >= 0 && ind < size)
		{
			std::shared_ptr < lista_elem > chw = szczyt;

			for (int i = 0; i < ind; i++)
			{

				chw = chw->next();
			}
			//return chw.give();
			int zm = chw->give();
			return zm;
		}
	}
	
	void set(int nVal, int ind)
	{
		if (ind >= 0 && ind < size)
		{
			std::shared_ptr < lista_elem > chw = szczyt;

			for (int i = 0; i < ind; i++)
			{

				chw = chw->next();
			}
			//return chw.give();
			chw->zmien(nVal);
		}

	}


	void likwiduj()
	{
		size = 0;
		std::shared_ptr < lista_elem > chw;
		//lista_elem<T>* chw;
		do {
			chw = szczyt;
			szczyt = szczyt->next();
			//delete[] chw;
		} while (szczyt != nullptr);
	}

	int Size()
	{
		return size;
	}
	
	void show()
	{
		std::shared_ptr < lista_elem > chw = szczyt;
		//lista_elem<T>* chw = szczyt;
		cout << "----------------------" << endl;
		while (chw != 0)
		{
			std::cout << chw->give()  << std::endl;
			chw = chw->next();
		}
		cout << "----------------------"<< " size: "<< size << endl;
	}

	std::vector<int> showV()
	{
		std::shared_ptr < lista_elem > chw = szczyt;
		std::vector<int> result;
		//lista_elem<T>* chw = szczyt;
		while (chw != 0)
		{
			//std::cout << chw->give() << std::endl;
			result.push_back(chw->give());
			chw = chw->next();
		}
		return result;
	}


	lista(): szczyt(nullptr), size(0)
	{}

	lista(lista & origin)
	{
		size = origin.size;
		szczyt = std::make_unique<lista_elem>();//cos w nawiasie??

		for (int val : origin.showV())
		{
			dodaj(val);
		}
	}

	lista(lista&& origin)
	{
		size = origin.size;
		szczyt = origin.szczyt;
	}

	//op przypisania
	void operator=(lista& origin)//co gdy beda rozne typy w instancjach szablonu??
	{
		//if (typeid(T).name() == ) jak sprawdzic czy sa dwa rozne typy???
		likwiduj();
		//tak sie niestety nie da!!!
		//lista (origin);
		size = origin.size;
		szczyt = std::make_unique<lista_elem>();//cos w nawiasie??

		for (int val : origin.showV())
		{
			dodaj(val);
		}
	}

	void operator=(lista&& origin)//co gdy beda rozne typy w instancjach szablonu??
	{
		//if (typeid(T).name() == ) jak sprawdzic czy sa dwa rozne typy???
		likwiduj();
		szczyt = origin.szczyt;
		size = origin.size;
	}




	//wyszukiwanie
	int find(int missing)
	{
		std::shared_ptr < lista_elem > chw = szczyt;
		//lista_elem<T>* chw = szczyt;
		int i = 0;
		while (chw != 0)
		{
			//if (chw->give() == missing)
			if (chw->give()== missing)
			{
				return i;

			}
				
			chw = chw->next();
			i++;
		}
		//porownywanie zwracanego wyniku z -1 - blad konwersji z typu T????
		//return -1;
		notFound cos;
		throw cos;
	}
	//sortowanie
	void sort(bool dir = 0)
	{
		//0 - rosnaco
		for (int i = 0; i < size; i++)
		{
			cout << "i++" << endl;
			for (int j = 1; j < size-i; j++)
			{
				if (Give(j - 1) > Give(j))
				{
						//swap(people[i], people[j]);
					cout << Give(j - 1) << "  " << Give(j) << endl;
					int temp = Give(j - 1);
					set(Give(j), j - 1);
					set(temp,j);

					cout << Give(j - 1) << "  " << Give(j) << endl;

				}
			}
		}

		if (dir)//odwracamy, zeby bylo odwrotnie
		{
			for (int i = 0; i < size/2; i++)
			{
				lista_elem temp = Give(i);
				set(Give(size-1-i), i);
				set(temp.give(), size - i - 1);

			}
			
		}
		
	}

	void save(string filename)
	{
		std::shared_ptr < lista_elem > chw = szczyt;
		ofstream plo;
		plo.open(filename);
		if (plo.is_open())
		{
			while (chw != 0)
			{
				plo << chw->give() << endl;
				chw = chw->next();
			}
			plo.close();
		}
		
	}

	void import(string filename)
	{
		std::shared_ptr < lista_elem > chw = szczyt;
		ifstream plo;
		plo.open(filename);
		if (plo.is_open())
		{
			while (!plo.eof())
			{
				int temp;
				plo >> temp;
				if (plo.fail())
					break;

				dodaj(temp);
			}
			plo.close();
		}

	}


	//usuwa pierwszy element z listy
	void usun_front()
	{
		size--;
		if (szczyt != nullptr)
		{
			if (szczyt->next() != nullptr)//tylko 1 elem
			{
				std::shared_ptr < lista_elem > temp = szczyt->next();
				//lista_elem<T> * temp = szczyt->next();
				
				//delete szczyt;
				szczyt = temp;
			}
			else
			{
				//delete szczyt;
				szczyt = nullptr;
			}
		}
	}

	int give_f()
	{
		return szczyt->give();
	}

	

	//jak zrobic funkcje ktora zwraca wartosc, a potem usuwa ja???
	


};



