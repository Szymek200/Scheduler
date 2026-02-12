#include "Worker.h"

int Worker::id_set = 0;

bool Worker::workRange(date d, originShift& range)
{
	//ten wektor jest nie potrzebny
	vector<originShift*> temp = employeeDays.todayShifts(d);//jak w ogole nie pracuje tego dnia to zwroci nic!!!
	if (temp.size() == 0)//w ten dzien nie pracuje
	{
		return 0;
	}
	else
	{
		range = temp[0];
		return 1;
	}
	
	/*if (temp[0]->giveDuration() == 0)
		return 0;*/

	
}

bool Worker::thisPlace(string workplace)
{
	for (string one : m_workPlace)
	{
		if (workplace == one)
			return 1;
	}

	return 0;
}


void Worker::save(path newfolder)
{
	string filename = giveName() + "save" + ".txt";
	//tworzenie folderu
	path savepath = newfolder / filename;
	ofstream plz;
	plz.open(savepath);

	plz << name << " "<< surname << endl;
	//dyspozycje 
	plz.close();
}

