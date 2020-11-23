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

#include "./random-bits.h"
#include <time.h>

#define FLAG_PATH "flag.txt"
#define TIMES 0x14000000ul


char * strfry_local (char *string) {
  static int init;
  static struct random_data rdata;
  // static int taps;
  // printf("Taps of the strfry_local rdata: %d\n", taps);
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


// exits
static void alarm_handler(int _x) {
    (void)_x;
    puts("Time's up!");
    _exit(0);
}

// starts the code with setting the alarm thing?
static __attribute__((constructor)) void inits(void) {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);

    struct sigaction sa = {
        .sa_handler = alarm_handler,
    };
    if (sigaction(SIGALRM, &sa, NULL) < 0) {
        err(1, "sigaction");
    }

    alarm(20); // 20 second cutoff
}

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

static size_t read_file(int fd, char* buf, size_t size) {
    size_t i = 0;

    while (i < size) {
        ssize_t x = read(fd, buf + i, size - i); // read from file descriptor into the buf
        if (x < 0) {
            if (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK) {
                continue;
            }
            err(1, "read");
        } else if (x == 0) {
            break;
        }

        i += x;
    }

    return i;
}

// size: # of hex chars to get
static void read_rand_hexstr(char* buf, size_t size) {
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) {
        err(1, "read random");
    }

    size_t i = 0;
    while (i < size) {
        char c;
        read_file(fd, &c, 1); // read one byte from /dev/urandom
        char hex[3]; 
        if (snprintf(hex, sizeof(hex), "%02hhx", c) != 2) {
            err(1, "snprintf");
        }
        buf[i++] = hex[0]; // convert to hex and write one hex char at a time (could this end up with an odd number of hex chars?)
        if (i < size) {
            buf[i++] = hex[1];
        }
    }

    if (close(fd) < 0) {
        err(1, "close random");
    }
}

// win
static void print_flag(void) {
    int fd = open(FLAG_PATH, O_RDONLY);
    if (fd < 0) {
        err(1, "open flag");
    }

    char buf[0x100] = { 0 };
    read_file(fd, buf, sizeof(buf) - 1);

    if (close(fd) < 0) {
        err(1, "close flag");
    }

    printf("FLAG: %s\n", buf);
}

int main(void) {
    char buf[0x1000] = { 0 };

    puts("Welcome!");

    read_rand_hexstr(buf, 0x101); // read 0x101 from urandom into buf

    // strfry buf a bunch of times
    // why? what does this accomplish?
    // I think this just makes guessing the time seed harder 
    // 1. takes up time
    // 2. makes confirming a seed harder because you gotta tap it a shit ton of times before you can confirm it shuffled your input the same

    // DEBUG:
    // struct timespec tv;
    // clock_gettime (CLOCK_MONOTONIC, &tv);
    // printf("\n main debug: Time data: %lld | . | %.9ld \n", (long long)tv.tv_sec, tv.tv_nsec);
    // END DEBUG

    size_t i;
    for (i = 0; i < TIMES / 0x100; ++i) { // 1310720 times
        // strfry(buf); 
        strfry_local(buf);
    }
    // printf("i = %zu \n", i);

    puts("gib:");

    // Read some user input
    read_line(buf, sizeof(buf)); 

    // strfry and print it
    // strfry(buf); 
    strfry_local(buf);
    puts(buf);

    char fry_buf[0x100] = { 0 };
    read_rand_hexstr(fry_buf, 64); // read 64 hex chars to fry_buf

    strcpy(buf, fry_buf); // copy it into buf
    //strfry(buf); // strfry and print it
    strfry_local(buf);
    puts(buf);

    read_line(buf, sizeof(buf)); // read another line

    if (!strcmp(buf, fry_buf)) { // input must match fry_buf
        print_flag();
    } else {
        puts("WRONG");
    }

    return 0;
}
