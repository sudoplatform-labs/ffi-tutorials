#include <stdint.h>
#include <stdio.h>

uint32_t count_characters(const char* str);

int main() {

    char *str = "Hello World!";
    uint32_t count = count_characters(str);
    printf("There are %d chars in \"%s\"\n", count, str);

    return 0;
}


