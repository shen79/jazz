#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>

void xread(char* f) {
    char buf[32];
    char* read;
    FILE * fp;

    fp = fopen(f, "r");
    if (fp == NULL)
        exit(EXIT_FAILURE);
    while ((read = fgets(buf, 64, fp)) != NULL) {
        printf("%s", buf);
    }
    fclose(fp);
}

int main(int argc, char** argv)
{
	xread(argv[1]);
    return 0;
}
