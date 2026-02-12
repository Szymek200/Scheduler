#ifndef MONTHT
#define MONTHT

#include <iostream>
#include <vector>

//#include "ShifT.h"

#include "Day.h"

class MonthT
{
	
	
		int monthsize;

		months name;
		int month;
		int year;

		vector<Day<ShifT>> content;




	public:
		void settingMonth(int m, int y)
		{
			date temp = date(1, m, y);
			monthsize = temp.monthsize();
			month = m;
			year = y;
			name = temp.giveMName();

			//tworzenie dni w miesiacu

			//zerowy element(zeby sie latwo indeksowalo)
			Day<ShifT> t(date(1,m,y));
			content.push_back(t);

			for (int i = 1; i <= monthsize; i++)
			{
				date te(i, month, year);
				Day<ShifT> newday(te);
				content.push_back(newday);
				//daloby sie od razu w psuh back podac informacje do konstuktora???
			}

			for (Day<ShifT>& d : content)
			{
				cout << date::dayString(d.giveDate().giveName()) << "  " << d.giveDate().giveDay() << "." << d.giveDate().giveMonth() << endl;
			}
		}


		MonthT(int m, int y)
		{
			settingMonth(m, y);
		}


		MonthT()
		{

			month = 0;
			year = 0;
			monthsize = 0;
			std::cout << month;
		}


		

		int monthSize()
		{
			return monthsize;
		}

		

		void editDay(int numDay, ShifT* t)//zmiana godzi zmian pracy
		{
			content[numDay].setTime(t);
		}

		void editDay(int numDay, vector<ShifT*> t)//zmiana godzi zmian pracy
		{
			content[numDay].setTime(t);
		}

		std::vector<ShifT*> todayShifts(date d)
		{

			return content[d.giveDay()].giveShiftsPoint();
		}

		//musi byc wskaznik!!!
		

		std::vector<ShifT*> todayShifts(int day)
		{

			return content[day].giveShiftsPoint();
		}



		int monthNumber()
		{
			return month;
		}

		int yearNumber()
		{
			return year;
		}



		Hour MinShift()
		{
			Hour min(25, 0);
			for (Day<ShifT> d : content)
			{
				for (ShifT sh : d.giveShifts())
				{
					if (sh.giveDuration() < min)
						min = sh.giveDuration();
				}
			}
			return min;

		}
	

};

#endif // !MONTHT



