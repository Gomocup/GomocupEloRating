#include<iostream>
#include<fstream>
#include<regex>
using namespace std; 

int main()
{
	ifstream fin("score.txt");
	ofstream fout("record.pgn");
	regex pattern("\"(.+)\"\\s+(\\d+)\\s+(\\d+)\\s+(\\d+)\\s+\"(.+)\"");
	while(!fin.eof())
	{
		char reads[1000];
		fin.getline(reads, 1000);
		string s(reads);
		match_results<string::const_iterator> result;
		if(regex_match(s, result, pattern))
		{
			string pl[2];
			pl[0] = result[1].str();
			pl[1] = result[5].str();
			int wnum = atoi(result[2].str().c_str());
			int dnum = atoi(result[3].str().c_str());
			int lnum = atoi(result[4].str().c_str());
			int i=0;
			for(;i<wnum;i++)
			{
				char outs[1000];
				if(i<(wnum+dnum+lnum)/2)
				{
					sprintf_s(outs,"[White \"%s\"]\n[Black \"%s\"]\n[Result \"1-0\"]\n\n1. d4 d5 1-0\n\n", pl[0].c_str(),pl[1].c_str());
				}
				else
				{
					sprintf_s(outs,"[White \"%s\"]\n[Black \"%s\"]\n[Result \"0-1\"]\n\n1. d4 d5 0-1\n\n", pl[1].c_str(),pl[0].c_str());
				} 
				fout << outs ;
			}
			for(;i<wnum+dnum;i++)
			{
				char outs[1000];
				if(i<(wnum+dnum+lnum)/2)
				{
					sprintf_s(outs,"[White \"%s\"]\n[Black \"%s\"]\n[Result \"1/2-1/2\"]\n\n1. d4 d5 1/2-1/2\n\n", pl[0].c_str(),pl[1].c_str());
				}
				else
				{
					sprintf_s(outs,"[White \"%s\"]\n[Black \"%s\"]\n[Result \"1/2-1/2\"]\n\n1. d4 d5 1/2-1/2\n\n", pl[1].c_str(),pl[0].c_str());
				} 
				fout << outs ;
			}
			for(;i<wnum+dnum+lnum;i++)
			{
				char outs[1000];
				if(i<(wnum+dnum+lnum)/2)
				{
					sprintf_s(outs,"[White \"%s\"]\n[Black \"%s\"]\n[Result \"0-1\"]\n\n1. d4 d5 0-1\n\n", pl[0].c_str(),pl[1].c_str());
				}
				else
				{
					sprintf_s(outs,"[White \"%s\"]\n[Black \"%s\"]\n[Result \"1-0\"]\n\n1. d4 d5 1-0\n\n", pl[1].c_str(),pl[0].c_str());
				} 
				fout << outs ;
			}
		}
	}
	fin.close();
	fout.close();
	return 0;
}
