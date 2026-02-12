#include "matrix.h"


using namespace std::filesystem;

void matrix::save(path newfolder)
{
	string filename = giveName() + "schedule" + ".txt";
	//tworzenie folderu
	path savepath = newfolder / filename;
	ofstream plz;
	plz << giveName() << endl;
	for (int i = 1; i <= m->monthSize(); i++)
	{
		plz << "Dzien: " << i << "." << m->monthNumber() << endl;
		for (ShifT* day : m->todayShifts(i))
		{
			plz << day->print() << endl;
		}
		plz << endl;
	}
	plz.close();
}

void matrix::show()
{
	for (int i = 1; i <= m->monthSize(); i++)
	{
		cout << i << "." << m->monthNumber() << endl;
		for (ShifT s : m->todayShifts(i))
		{
			cout << s << endl;
		}
	}
}

