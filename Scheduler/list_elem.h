#pragma once
#include <memory>
#include <iostream>


class lista_elem
{
	
	//lista_elem* nastepny;
	std::shared_ptr < lista_elem > nastepny;
	int value;

public:
	int give()
	{
		return value;
	}
	void zmien(int x)
	{
		value = x;
	}

	/*lista_elem<T>* next()
	{
		return nastepny;
	}*/

	std::shared_ptr < lista_elem > next()
	{
		return nastepny;
	}

	int conv()
	{
		//	sprawdzenie czy jest intem!!!
		{
			return  value;
		}

		//co by sie stalo, gdyby funkcja nic nie zwrocila???
	}
	/*void save(lista_elem<T>* p)
	{
		nastepny = p;
	}*/

	//zapisuje, kto jest nastepnym elementem
	void save(std::shared_ptr < lista_elem > p)
	{
		nastepny = p;
	}

	lista_elem(int x = 0) : value(x), nastepny(nullptr)
	{
	}

	//lista_elem(const lista_elem<T>& origin)
	//{
	//	value = origin.value;
	//	nastepny = origin.nastepny;
	//}

	//lista_elem( lista_elem<T>&& origin)
	//{
	//	// w srodku cos zmieniamy??
	//	value = origin.value;
	//	nastepny = origin.nastepny;
	//}


};

