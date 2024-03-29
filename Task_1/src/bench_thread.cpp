#include "tools.h"

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("Parameter is missing");
        return 0;
    }
    int thrds;
    thrds = atoi(argv[1]);
    int list_lengths[3] = {10000, 20000, 50000};
    int Len = sizeof(list_lengths) / sizeof(list_lengths[0]);

    for (int i = 0; i < Len; i++)
    {
        threads_function(thrds, list_lengths[i]);
    }

    return 0;
}