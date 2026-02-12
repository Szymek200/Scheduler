#ifndef EVERYR
#define EVERYR

#include "Rule.h"
#include "Date.h"
#include <sstream>
class EveryR :
    public Rule
{
    //int difference;
    //int type; //1-day, 2-month, 3 year - jak liczymy odstep -na razie tylko podajemy dni wystepowania
    vector<days> when;//od kiedy zaczynamy odliczanie
    //cotydzien, miesiac, bla, bla
public:

    EveryR(originShift  t,   vector<days> s) : Rule(t), when(s)
    {
        
    }
    std::vector<string> save()
    {
        std::vector<string> result;
        result.push_back("EveryR");
        result.push_back(time.save());
        string x="";



        for (days n : when)
        {
            x += date::dayString(n) + " ";
        }
        result.push_back(x);

        return result;
    }

    string type()
    {
        return "EveryR";
    }

    //nie wiem czy bedzie dzialac poprawnie!!!
    EveryR(std::ifstream& plo, std::vector<Rule*>& memory)//zapisuje dynamicznie w pamieci zasady
    {
        //nazwa zasady - odczytuje funkcja w workplace
        //Shift
        string shift;
        getline(plo, shift);
        originShift temp(shift);
        //te rzeczy moga byc w jednej linii
        //int d, t;
        //plo >> d;
       // plo >> t;
        //dni w ktorych sie odbywa
        getline(plo, shift);

        stringstream ss(shift);
        vector<days> selected_days;


        while (ss >> shift)
        {

            selected_days.push_back(date::daysEnum(shift));

        }


        cout << temp.giveBegin().print() << " - " << temp.giveEnd().print() << endl;
        EveryR* result = new EveryR(temp,selected_days);//nie mozna zrobic obiektu bez nazwy, ktory byly jako argument funkcji

        memory.push_back(result);
    }


    bool isFulfilled(date ask)//czy dzisiaj mozna zrealizowac ta zasade
    {
        //cout << date::dayString(ask.giveName()) << endl;
        for (days nam : when)
        {
            if (nam == ask.giveName())
            {
               //giveShift().print(); cout << endl;
                return true;
            }
        }
        return false;
        
    }

};

#endif // !EVERYR

