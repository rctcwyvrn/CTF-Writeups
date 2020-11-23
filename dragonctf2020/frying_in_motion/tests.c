#define _GNU_SOURCE
#include <err.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define FLAG_PATH "flag.txt"
#define TIMES 0x14000000ul
#include "./random-bits.h"

static size_t read_line(char* buf, size_t size) {
    if (size == 0) {
        return 0;
    }

    size_t i = 0;
    while (i < size - 1) {
        char c;
        ssize_t x = read(0, &c, 1); // read from the 0? 0th file handle or smth? i guess this is user input?
        if (x < 0) {
            if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK) {
                continue;
            }
            err(1, "read");
        } else if (x == 0) {
            break;
        }

        if (c == '\n') { // stop when we hit a newline
            break;
        }

        buf[i++] = c; // add c to the buf
    }

    buf[i] = '\0'; // null terminate

    return i;
}

char * strfry_local (char *string) {
  static int init;
  static struct random_data rdata;

  if (!init)
    {
      static char state[32];
      rdata.state = NULL;
      initstate_r (random_bits (),
		     state, sizeof (state), &rdata);
      init = 1;
    }

  size_t len = strlen (string);
  if (len > 0) {
    for (size_t i = 0; i < len - 1; ++i) {
      int32_t j;
      random_r (&rdata, &j);
      j = j % (len - i) + i;

      char c = string[i];
      string[i] = string[j];
      string[j] = c;
      }
  }
    return string;
}

char * strfry_from_seed(char *string, time_t tv_sec, long tv_nsec) {
    // init rdata
    struct random_data rdata;
    char state[32];
    rdata.state = NULL;
    initstate_r (random_bits_from_seed (tv_sec, tv_nsec),
            state, sizeof (state), &rdata);
    printf("type: %d \n", rdata.rand_type);
    // perform extra taps of the rdata to get it to match what the challenge does
    size_t i;
    int32_t j;
    size_t len_garbage = 0x101;
    for (i = 0; i < TIMES / 0x100; ++i) { // 1310720 times
        for (size_t i = 0; i < len_garbage - 1; ++i) {
            random_r (&rdata, &j); 
        }
    }

    // strfry
    size_t len = strlen (string);
    if (len > 0)
        for (size_t i = 0; i < len - 1; ++i) {
            int32_t j;
            random_r (&rdata, &j);
            j = j % (len - i) + i;

            char c = string[i];
            string[i] = string[j];
            string[j] = c;
        }
    return string;
}

int main() {
    printf("Hi\n");
    char buf[0x1000] = { 0 };
    while (1) {
        read_line(buf, sizeof(buf)); 
        printf("%s -> ", buf);
        printf("%s \n", strfry_local(buf));
        // printf("test: %s \n", strfry_from_seed(buf, 100, 314));
    }
}
