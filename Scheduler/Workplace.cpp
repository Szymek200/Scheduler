#include "Workplace.h"


using namespace std;
using namespace std::filesystem;


//string -> enum

//days daysEnum(string name)
//{
//	for (int i = 1; i <= 9; i++)
//	{
//		if (name == to_string(date::daysOfWeek[i]))
//		{
//			return date::daysOfWeek[i];
//		}
//	}
//}


void Workplace::save(path newfolder)
{
	string filename = giveName() +"save" + ".txt";
	//tworzenie folderu
	path savepath = newfolder / filename;
	ofstream plz;
	plz.open(savepath);

	plz << name << endl;
	for (Rule* rule : rules)
	{
		for (string line : rule->save())
		{
			plz << line << endl;
		}
	}

	plz.close();

}

vector<ShifT> Workplace::giveTodayShifts(date m)
{
	vector<ShifT> result;
	for (Rule* rule : rules)
	{

		if (rule->isFulfilled(m))
		{
			//ShifT chw((rule->giveShift()), m, this);
			//result.push_back(chw);
		}
	}

	return result;
}


vector<Rule*> Workplace::todayRules(date d)
{
	vector<Rule*> result;
//	cout << date::dayString(d.giveName()) << "  " << d.giveDay() << "." << d.giveMonth() << endl;
	for (Rule* rule : rules)
	{
		if (rule->isFulfilled(d) == -1)
		{
			cout << "Co sie stalo z virtual" << endl;
		}
		else if (rule->isFulfilled(d))
		{
			result.push_back(rule);
		}
	}

	return result;
}