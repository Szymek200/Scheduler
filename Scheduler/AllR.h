#ifndef ALLR
#define ALLR

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include "Rule.h"
using namespace std;

class AllR :
    public Rule
{
public:
    //w kazdy dzien jest;
    AllR(originShift t) : Rule(t)
    {

    }

    std::vector<string> save()
    {
        std::vector<string> result;
        result.push_back("AllR");
        result.push_back(time.save());

        return result;
    }

    bool isFulfilled(date when)//czy dzisiaj mozna zrealizowac ta zasade
    {
        return true;
    }

    string type()
    {
        return "AllR";
    }

    AllR(std::ifstream& plo, std::vector<Rule*>& memory)//zapisuje dynamicznie w pamieci zasady
    {
        //nazwa zasady - odczytuje funckja w workplace
        //Shift
        string shift;
        string sh2;
       // getline(plo, shift);
        plo >> shift;
        plo >> sh2;

        originShift   temp(shift, sh2);
        AllR* result = new AllR(temp);//nie mozna zrobic obiektu bez nazwy, ktory byly jako argument funkcji
        memory.push_back(result);
    }
};

#endif // !ALLR

