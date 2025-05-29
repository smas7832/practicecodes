#include <cstdio>
#include <fstream>
#include <string>


int audioMetaExtraction(char *filePath) {
    std::ifstream file (filePath);
    if(!file.is_open())
        return 1; // Unable to open file for reading

    std::string line;
    while (std::getline(file, line)) {
        if (line.find("TITLE=") == 0) {
            std::string title = line.substr(6);
            std::ofstream out (filePath);
            if(!out.is_open())
                return 1; // Unable to open file for writing
            out << "Title: " << title << "\n";
            out.close();
        } else if (line.find("ARTIST=") == 0) {
            std::string artist = line.substr(7);
            std::ofstream out (filePath, std::ios::app);
            if(!out.is_open())
                return 1; // Unable to open file for writing
            out << "Artist: " << artist << "\n";
            out.close();
        } else if (line.find("ALBUM=") == 0) {
            std::string album = line.substr(6);
            std::ofstream out (filePath, std::ios::app);
            if(!out.is_open())
                return 1; // Unable to open file for writing
            out << "Album: " << album << "\n";
            out.close();
        } else if (line.find("COMMENT=") == 0) {
            std::string comment = line.substr(8);
            std::ofstream out (filePath, std::ios::app);
            if(!out.is_open())
                return 1; // Unable to open file for writing
            out << "Comment: " << comment << "\n";
            out.close();
        } else if (line.find("GENRE=") == 0) {
            std::string genre = line.substr(6);
            std::ofstream out (filePath, std::ios::app);
            if(!out.is_open())
                return 1; // Unable to open file for writing
            out << "Genre: " << genre << "\n";
            out.close();
        } else if (line.find("YEAR=") == 0) {
            int year = std::stoi(line.substr(5));
            std::ofstream out (filePath, std::ios::app);
            if(!out.is_open())
                return 1; // Unable to open file for writing
            out << "Year: " << year << "\n";
            out.close();
        } else if (line.find("TRACKNUMBER=") == 0) {
            int track = std::stoi(line.substr(13));
            std::ofstream out (filePath, std::ios::app);
            if(!out.is_open())
                return 1; // Unable to open file for writing
            out << "Track: " << track << "\n";
            out.close();
        }
    }

    return 0;
}

