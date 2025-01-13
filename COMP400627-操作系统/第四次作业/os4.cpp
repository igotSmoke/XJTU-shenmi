#include <iostream>
#include <vector>
#include <unordered_set>
#include <list>
#include <algorithm>
#include <unordered_map>

using namespace std;

vector<int> randString(int length, int pageCount) {
    vector<int> pag_str;
    for (int i = 0; i < length; ++i) {
        pag_str.push_back(rand() % pageCount);
    }
    return pag_str;
}

// FIFO 页面置换算法
int fifo(const std::vector<int>& pages, int frames) {
    
    std::unordered_set<int> s; 
    std::vector<int> pageOrder(frames, -1);  
    int flt_cnt = 0;  
    int pos = 0; 

    for (int page : pages) {
        if (s.find(page) == s.end()) {
            flt_cnt++;

            if (s.size() < frames) {
                s.insert(page);
                pageOrder[pos] = page;
                pos = (pos + 1) % frames;
            }
            else {
                
                int pr = pageOrder[pos];
                s.erase(pr);
                s.insert(page);
                pageOrder[pos] = page;
                pos = (pos + 1) % frames;
            }
        }
    }
    return flt_cnt;
}

int lru(const std::vector<int>& pages, int frames) {
    std::unordered_set<int> s; 
    std::unordered_map<int, int> pagCnt;  // 每个页面的最近使用时间索引
    int flt_cnt = 0; 

    for (int i = 0; i < pages.size(); ++i) {
        int pag = pages[i];
        if (s.find(pag) == s.end()) {
            flt_cnt++;
            if (s.size() < frames) {
                s.insert(pag);
            }
            else {
                int i = -1;
                int j = i;
                for (const int& page : s) {
                    if (pagCnt[page] < j) {
                        j = pagCnt[page];
                        i = page;
                    }
                }
                s.erase(i);
                s.insert(pag);
            }
        }
        pagCnt[pag] = i;
    }
    return flt_cnt;
}

// 最优页面置换算法
int opt(const vector<int>& pages, int frames) {
    unordered_set<int> s;
    int flt_cnt = 0;
    for (int i = 0; i < pages.size(); ++i) {
        if (s.find(pages[i]) == s.end()) 
        {
            flt_cnt++;
            if (s.size() < frames) 
            {
                s.insert(pages[i]);
            }
            else 
            {
                // 找到哪个页面在未来最长时间内不会再被访问
                int ans = -1;
                int rep = -1;
                for (auto page : s) {
                    int j;
                    for (j = i + 1; j < pages.size(); ++j) 
                    {
                        if (pages[j] == page) 
                            break;
                    }
                    if (j == pages.size()) {
                        rep = page;
                        break;
                    }
                    if (j > ans) {
                        ans = j;
                        rep = page;
                    }
                }
                s.erase(rep);
                s.insert(pages[i]);
            }
        }
    }

    return flt_cnt;
}

int main() {
    int pag_cnt = 10; 
    int ref_len = 20; 

    vector<int> pages = randString(ref_len, pag_cnt);
    //pages = { 7, 2, 3, 1, 2, 5, 3, 4, 6, 7, 7, 1, 0, 5, 4, 6, 2, 3, 0, 1 };

    for (int i : pages) {
        cout << i << " ";
    }
    cout << endl;

    int frames;
    cout << "cin the number of frames (1-7): ";
    cin >> frames;


    // 计算并输出每个算法的缺页错误次数
    cout << endl;
    cout << "With " << frames << " frames:" << endl;
    cout << "FIFO  Faults: " << fifo(pages, frames) << endl;
    cout << "LRU  Faults: " << lru(pages, frames) << endl;
    cout << "Optimal  Faults: " << opt(pages, frames) << endl;

    return 0;
}