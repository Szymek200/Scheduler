// dodawanie - monthT.cpp : Ten plik zawiera funkcję „main”. W nim rozpoczyna się i kończy wykonywanie programu.
//

#include <iostream>
#include <sstream>
#include <filesystem>
#include "date.h"
#include "Hour.h"
#include "originShift.h"
#include "Rule.h"
#include "EveryR.h"
#include "AllR.h"
#include "ShifT.h"
#include "Day.h"
#include "Month.h"
#include "MonthT.h"
#include "list_elem.h"
#include "list.h"
#include "matrix.h"
#include "Schedule.h"
#include "list.h"

#include "Worker.h"

using namespace std;
using namespace std::filesystem;

//miejsce robocze na dysku
path directorypath;

int rok;

struct createNotPossible {};

vector <path> filepaths;
vector<path> listDirectory(path directorypath)
{
    // path directorypath = R"raw(C:\Users\Szymek\source\repos\testShift\folderdane)raw";
    vector<path> folders;
     // To check if the directory exists or not 
    if (exists(directorypath)
        && is_directory(directorypath)) {
        // Loop through each item (file or subdirectory) in 
        // the directory 
        for (const auto& entry :
            directory_iterator(directorypath)) {
            // Output the path of the file or subdirectory 
           // cout << "File: " << entry.path() << endl;
            //cout << "File: " << directorypath << endl;
            if (is_directory(entry.path()))
            {
                listDirectory(entry.path());
                folders.push_back(entry.path());
            }
            else
            {
                //cout << "File: " << entry.path() << endl;
                filepaths.push_back(entry.path());
            }
        }
    }
    else {
        // Handle the case where the directory doesn't exist 
        cerr << "Directory not found." << endl;
    }
    return folders;
}

void openfiles()
{
    for (path p : filepaths)
    {
        ifstream plo;
        plo.open(p);

        if (plo.is_open())
        {
            while (!plo.eof())
            {
                int x;
                plo >> x;
                if (plo.fail())
                {
                    break;

                }
                std::cout << x << endl;
            }

            plo.close();
        }
    }
}

path createfolder(path directorypath, string foldername)
{
    // Define the path to create directory 
    //path directorypath = "mydirectory";

    directorypath = directorypath / foldername;
    // To check if the directory exist or not, create it if 
    // doesn't exist 
    if (!exists(directorypath)) {
        create_directory(directorypath);
       // cout << "Directory created: " << directorypath << endl;
    }

    // Define the file path within the directory and 
    // combining the directory 
    return directorypath;

    path filepath = directorypath / "my_file.txt";

    // Create and open the file for writing using 
    // std::ofstream 
    ofstream file(filepath);
    if (file.is_open()) {
        // Write data to the file 
        file << "Hello, FileSystem!";
        file.close();
        cout << "File created: " << filepath << endl;
    }
    else {
        // Handle the case if any error occured 
        cerr << "Failed to create file: " << filepath
            << endl;
    }

}

void addWorkplace();

int import();

//void save(string projectname, vector<matrix*> table);
void save(string projectname, vector<matrix*> table, date now);

std::vector<matrix*> create(date now);

int powitanie();

void workerWorkShift(path newfolder, vector<matrix*> table, Worker* w, date now);

void workplaceSave(path newfolder, vector<matrix*> table, date now);

vector<Workplace> baseny;
vector<Worker> pracownicy;

bool folderExist(path directorypath)
{
    if (exists(directorypath))
    {
        return 1;
    }
    return 0;
}

void savePlaceRules();



void testlisty();

//arg - workerID - w inne miejsce musze to dac
string workerName(int wid)
{
    for (int i = 0; i < pracownicy.size(); i++)
    {
        if (pracownicy[i].giveID() == wid)
        {
            return pracownicy[i].giveName();
        }
    }
}

int main()
{
    std::cout << "Hello World!\n";
    
    //date raz(1, 2, 2025);
   // cout << date::dayString(raz.giveName()) << endl;






    directorypath.clear();
    powitanie();
}

void addWorkplace()
{
    system("cls");
    std::cout << "Dodawanie miejsca placy\n";
    while (true)
    {
        int p;
        string nazwa;
        std::cout << "Podaj nazwe" << endl;
        cin >> nazwa;
        vector<Rule*> zasady;
        cout << "Tworzenie zmian" << endl;
         while(true)
         {
            system("cls");
           

            string one, two;
            cout << "Podaj godzine rozpoczecia i zakonczenia  np.6.12 12.14\n Wcisnij 6 aby zakonczyc" << endl;
            cin >> one;
            if (one == "6")
                break;
            cin >> two;
            Hour f1(one);
            Hour f2(two);
            originShift chw(f1, f2);

            cout << "Opcje: kazdy - 1\n cotydzien - 2\n" << endl;

            cin >> p;
            if (p == 6)
            {
                break;
            }
            int quantity;
            cout << "Ile takich zmian chcesz stworzyc?" << endl;
            cin >> quantity;
            Rule* r1;
            switch (p)
            {
                 case 1:
                     for (int i = 0; i < quantity; i++)
                     {
                         r1 = new AllR(chw);
                         zasady.push_back(r1);
                     }
                     
                     break;
                case 2:
                    string selected;
                     cout << "Podaj dni, w ktore bedzie wystepowac zmiana(Monday ... Sunday) - bez przecinkow - tylko spacje" << endl;
                     cin.clear();
                     cin.sync();//zeby getline zadzialal
                     cin.ignore();
                     getline(cin, selected);
                 //zamiana stringa na dni w wektorze
                     stringstream ss(selected);
                      vector<days> selected_days;

                     while (ss >> selected)
                     {
                          selected_days.push_back(date::daysEnum(selected));

                     }



                //dokoncz zapisywanie!!!
                     for (int i = 0; i < quantity; i++)
                     {
                         Rule* r2 = new EveryR(chw, selected_days);

                         zasady.push_back(r2);
                     }
                        

            }

         }


        Workplace temp(nazwa, zasady);
        
        baseny.push_back(temp);

        std::cout << "Chcesz dodac nastepne miejsce pracy - kliknij 1     Wyjdz - 2" << endl;
        int x;
        cin >> x;
        if (x != 1)
        {
            break;
        }

    }
}

int import()
{
    
  
    //cin.clear();
    //cin.sync();
    //cin.ignore();
    do{
        cout << "Podaj nazwe folderu z danymi\nW fodlerze maja znajdowac sie dwa foldery(z miejscami pracy - Places oraz z pracownikami - Workers)" << endl;
        string c;
       

        getline(cin, c);
        // cin >> c;

       //  path directorypath = c;//mam nadzieje, ze sie skonwertuje
         //directorypath = R"(C:\Users\User\Desktop\baseny)";
        directorypath = c;
    } while (!std::filesystem::exists(directorypath));

    int year;
    cout << "Podaj rok, w ktorym tworzymy grafik" << endl;
    cin >> year;
    //  year = 2025;
    string c;


    vector<path> folders;
   folders= listDirectory(directorypath);

    //wywolywanie konstruktorow dla kazdego pliku
    
    for (path p : filepaths)
    {
        string now = string(p.string());

        //for (int i = now.size() - 1; i >= 1; i--)
        //{
        //    string temp = now.substr(i - 1, 1) + now.substr(i, 1);
        //    cout << now << endl;
        //    for (int j = 0; j < now.size(); j++)
        //    {
        //        cout << now[j] << "  ";
        //    }
        //    cout << endl;
        //    for (int j = 0; j < now.size(); j++)
        //    {
        //        cout <<" "<< j << "  ";
        //    }
        //    //  cout << temp << endl;
        //    if (temp == R"(s\)")
        //    {
        //        //cout << "Znaleziono" << endl;
        //        now.erase(i, now.size() - 1);
        //        //cout << now << endl;
        //        break;
        //    }

        //}
        int one;
        
        for (int i = 0; i < now.size(); i++)
        {
            string temp = now.substr(i, 1);
            if (temp == R"(\)")
            {
                one = i;
            }
        }

       
        for (int i = 0; i < now.size(); i++)
        {
            string temp = now.substr(i, 1);
            if (temp == R"(\)")
            {
                string fname = now.substr(one + 1, i - one - 1);
                if (fname == "Places")
                {

                    Workplace ch(string(p.string()));
                    baseny.push_back(ch);
                }
                else if(fname == "Workers")
                {
                    Worker chw(string(p.string()), year);
                    pracownicy.push_back(chw);
                }

                one = i;
            }
        }

        // cout << "Now:" << now << endl;
        
        //if (now == folders[1]) //1 - pracownicy, 0 - places
        //{
        //    Worker chw(string(p.string()), year);
        //    pracownicy.push_back(chw);
        //}
        //if (now == folders[0]) //1 - pracownicy, 0 - places
        //{
        //    Workplace ch(string(p.string()));
        //    baseny.push_back(ch);
        //}

          
        
    }


    cout << "Wczytalismy" << endl;
    for (Workplace w : baseny)
    {
        cout << w.giveName() << endl;
    }

    cout << "Pracownicy" << endl;
    for (Worker w : pracownicy)
    {
        cout << w.giveName() << endl;
    }

    
    return year;
}

int powitanie()
{
    while (true)
    {
        system("cls");
       
        int x;
        if (directorypath.empty())
        {
           // cout << "Najpierw musisz zaimportowac pracownikow\nWskaz sciezke dostepu do folderu, w ktorym sa dyspozycje pracownikow" << endl;
           
            x = 1;
        }
        else{
            cout << "Menu\nMozliwe operacje:" << endl;
            cout << "Importowanie - 1\nTworzenie miejsca pracy - 2\nTworzenie grafiku - 3\nZapisywanie stworzonych miejsc pracy - 4\nKoniec - 6 " << endl;
            cin >> x;
        }
        
       
        switch (x)
        {
        case 1:
           rok = import();
            break;
        case 2:
            addWorkplace();
            break;
       
        case 3:
            //jestpoza switch
            //std::vector<matrix*> chw= ;
           // save(projectname, create(date(1, z, y)));
            
            break;
        case 4:
            savePlaceRules();
            break;
        case 6:

            savePlaceRules();
            return 0;
        default:
            cout << "Podales zla opcje" << endl;

        }

        if (x == 3)
        {
            
            int z;
            cout << "Podaj numer miesiaca, na ktory tworzymy grafik" << endl;
            cin >> z;
            

            //z = 2;
            
            int czy = 1;
            string projectname;
            do {
                czy = 1;
                cout << "Jak chcesz nazwac swoj projekt(nazwe zacznij od litery)" << endl;

                 cin >> projectname;
                //switchowi nie podoba sie project name!!!
               // projectname = "nazwaproj";
                path projectpath = directorypath / projectname;
                if (folderExist(projectpath))
                {
                    cout << "Projekt o takiej nazwie juz istnieje. Czy chcesz nadpisac projekt. Y -1 N -0" << endl;

                    cin >> czy;
                    // czy = 1;
                    if (czy)
                    {
                        std::filesystem::remove_all(projectpath);
                    }

                }

            } while (czy == 0);

            date t(1, z, rok);
            cout << t.monthsize() << endl;
            cout << t.giveMonth() << endl;
            std::vector<matrix*> chw;
            try {
                //co z wektorem, gdy jest wyjatek??
                chw = create(t);
            }
            catch (createNotPossible)
            {
                cout << endl;

                cout << "Grafik nie mozliwy do stworzenia." << endl;
                cout << "Za duzo etatow na liczbe dostepnych godzin" << endl;
                cin.sync();
                cin.clear();
                cin.ignore();
            }



            //save(projectname, create(date(1, z, y)));
            if (chw.size() > 0)
            {
                save(projectname, chw, t);
            }
        }
        
        cout << "Nacisnij Enter, aby kontynuowac" << endl;
        getchar();
    }

}

void save(string projectname, vector<matrix*> table, date now)
{
    //jak folder juz istnieje to przydaloby sie utworzyc inny lub go wyczyscic
    path newfolder = createfolder(directorypath, projectname);

    path placefolder = createfolder(newfolder, "PlaceSchedule");

    for (Workplace& w : baseny)
    {

       // w.save(placefolder);
        workplaceSave(placefolder, table, now);
    }
    //osobny folder dla pracownikow!!!

    path workerfolder = createfolder(newfolder, "WorkerSchedule");
    now.setDay(1);
    for (Worker& w : pracownicy)
    {

        workerWorkShift(workerfolder ,table,&w,now);
       
    }
}


std::vector<matrix*> create(date now)
{
    std::vector<matrix*> table;
    for (Workplace& w : baseny)
    {
        matrix* temp = new matrix(&w, now);
       // cout << temp->giveName() <<"-------------------------------------" << endl;
       // temp->show();
        table.push_back(temp);
    }

    Schedule* wplan;
    try {
       wplan = new Schedule(table, pracownicy, now);
       cout << "STATS______________________" << endl;
       //wplan->statistics();
      
    }
    catch (scheduleNotPossible)
    {
        createNotPossible temp;
       
        throw temp;

    }

    wplan->create();
   

    return table;
}

void workerWorkShift(path newfolder, vector<matrix*> table,Worker * w ,date now)
{
    string filename = w->giveName() + "Work" + ".txt";
    //tworzenie folderu
    path savepath = newfolder / filename;
    ofstream plz;
    plz.open(savepath);
    plz << w->giveName() << endl;
   
    Hour workhour;//tymczasowe, bo w schedule nie ma wskaznikow na worker i workhours sie nie przenosza
    now.setDay(1);
    while (true)
    {
        
        for (matrix* mx : table)
        {
            vector<ShifT*> onematrix = mx->workerShifts(w->giveID(), now);
            for (int i = 0; i < onematrix.size(); i++)
            {
                plz << now.giveDay() << "." << now.giveMonth() << "  ";
                plz << mx->giveName() << " " << onematrix[i]->printH() << endl;
                workhour = workhour + onematrix[i]->giveDuration();
            }
        }

        try {
            now.increaseDay();
        }
        catch (dayOutOfRange)
        {
            break;
        }
    }
  
    plz << "Suma godzin: " << workhour.print() << endl;
    plz << "Etat: " << w->give_type().print() << endl;

    plz.close();
}


void workplaceSave(path newfolder, vector<matrix*> table, date now)
{

    for (matrix* mx : table)
    {
        string filename = mx->giveName() + "save" + ".txt";
        //tworzenie folderu
        path savepath = newfolder / filename;
        ofstream plz;
        plz.open(savepath);

        plz << mx->giveName() << endl;
        now.setDay(1);
        while (true)
        {
            plz << now.giveDay() << "."<< now.giveMonth() << endl;
            for (ShifT* sh : mx->todayShifts(now))
            {
                plz << sh->print() << "  ";

                if (sh->giveWorker() == 0)
                {
                    plz << endl;
                }
                else
                {
                    //szukamy imienia na podstawie id
                    for (Worker p : pracownicy)
                    {
                        if (p.giveID() == sh->giveWorker())
                        {
                            plz << p.giveName() << endl;
                            break;
                        }
                    }
                }
                
            }


            try {
                now.increaseDay();

            }
            catch (dayOutOfRange)
            {
                break;
            }
        }
        

        plz.close();
    }
   
}


void testlisty()
{
    lista radek;

    radek.dodaj(235);
    radek.dodaj(6); radek.dodaj(34); radek.dodaj(0); radek.dodaj(9); radek.dodaj(120);

    

    radek.show();
    radek.usun(radek.find(34));
   // radek.dodaj(1);
    radek.usun(radek.find(120));
   // radek.dodaj(11);
    radek.show();


    /*radek.show();
    cout << radek.Size() << endl;
    cout << radek.find(8) << endl;
    cout << "---" << endl;
    radek.sort(1);
    radek.show();
    radek.save("mojradek.txt");
    cout << "----------------" << endl;
    lista<int> kasia;

    kasia.import("mojradek.txt");
    kasia.show();
    radek.sort();
    kasia = radek;
    cout << "----------------" << endl;
    kasia.show();*/

}

void savePlaceRules()
{
    cin.clear();
    cin.sync();
    cin.ignore();
    if (directorypath.empty())
    {
        cout << "Najpierw musisz zaimportowac pracownikow" << endl;
        cout << "Nacisnij Enter, aby kontynuowac" << endl;
        getchar();
     }
    else
    {
        path placerules;
     if(!std::filesystem::exists(directorypath));
     {
         placerules = createfolder(directorypath, "Places");
     }
       // path placerules = directorypath / "Places";
        for (Workplace& w : baseny)
        {
            w.save(placerules);
        }
    }
     
   
}